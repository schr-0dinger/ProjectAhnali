#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from dsl.runtime.diagnostics import emit_cli_error, emit_cli_info

SCHEMA_VERSION = "python_library_policy/1"
DEFAULT_POLICY_PATH = "cfg/python_library_policy.json"


@dataclass(frozen=True)
class ImportUse:
    path: Path
    module_name: str
    lineno: int
    imported_module: str
    root: str


def _load_policy(path: Path) -> dict[str, object]:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in policy file {path}: {exc}") from exc

    if obj.get("schema_version") != SCHEMA_VERSION:
        raise RuntimeError(
            f"Unexpected policy schema_version in {path}. Expected {SCHEMA_VERSION}."
        )

    for key in (
        "approved_external_roots",
        "forbidden_external_roots",
        "wrapper_module_roots",
    ):
        if key not in obj:
            raise RuntimeError(f"Policy file {path} is missing key '{key}'")

    approved = obj.get("approved_external_roots")
    test_only = obj.get("test_only_external_roots", [])
    forbidden = obj.get("forbidden_external_roots")
    wrappers = obj.get("wrapper_module_roots")

    if not isinstance(approved, list) or not all(isinstance(x, str) and x for x in approved):
        raise RuntimeError("approved_external_roots must be a non-empty string list")
    if not isinstance(test_only, list) or not all(isinstance(x, str) and x for x in test_only):
        raise RuntimeError("test_only_external_roots must be a string list")
    if not isinstance(forbidden, list) or not all(isinstance(x, str) and x for x in forbidden):
        raise RuntimeError("forbidden_external_roots must be a non-empty string list")
    if not isinstance(wrappers, dict):
        raise RuntimeError("wrapper_module_roots must be an object")
    for root, values in wrappers.items():
        if not isinstance(root, str) or not root:
            raise RuntimeError("wrapper_module_roots keys must be non-empty strings")
        if not isinstance(values, list) or not all(isinstance(x, str) and x for x in values):
            raise RuntimeError(
                f"wrapper_module_roots['{root}'] must be a non-empty string list"
            )

    return obj


def _module_name_for_file(repo_root: Path, path: Path) -> str:
    rel = path.relative_to(repo_root)
    no_suffix = rel.with_suffix("")
    parts = list(no_suffix.parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _local_roots(repo_root: Path) -> set[str]:
    out: set[str] = set()
    for item in repo_root.iterdir():
        name = item.name
        if name.startswith("."):
            continue
        if item.is_dir():
            out.add(name)
        elif item.suffix == ".py":
            out.add(item.stem)
    return out


def _iter_python_files(repo_root: Path):
    ignored_dirs = {
        ".git",
        ".venv",
        "build",
        "__pycache__",
        ".pytest_cache",
    }
    for path in sorted(repo_root.rglob("*.py")):
        if any(part in ignored_dirs for part in path.parts):
            continue
        yield path


def _collect_imports(repo_root: Path) -> list[ImportUse]:
    out: list[ImportUse] = []
    for path in _iter_python_files(repo_root):
        module_name = _module_name_for_file(repo_root, path)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            raise RuntimeError(f"Unable to parse {path}: {exc}") from exc

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_module = alias.name
                    root = imported_module.split(".", 1)[0]
                    out.append(
                        ImportUse(
                            path=path,
                            module_name=module_name,
                            lineno=getattr(node, "lineno", 1),
                            imported_module=imported_module,
                            root=root,
                        )
                    )
            elif isinstance(node, ast.ImportFrom):
                if getattr(node, "level", 0):
                    continue
                if not node.module:
                    continue
                imported_module = node.module
                root = imported_module.split(".", 1)[0]
                out.append(
                    ImportUse(
                        path=path,
                        module_name=module_name,
                        lineno=getattr(node, "lineno", 1),
                        imported_module=imported_module,
                        root=root,
                    )
                )

    return out


def _module_matches_prefix(module_name: str, allowed_prefix: str) -> bool:
    return module_name == allowed_prefix or module_name.startswith(allowed_prefix + ".")


def check_python_library_policy(
    *,
    repo_root: Path,
    policy_path: Path,
) -> tuple[bool, str]:
    policy = _load_policy(policy_path)

    approved: set[str] = set(policy.get("approved_external_roots", []))
    test_only_roots: set[str] = set(policy.get("test_only_external_roots", []))
    forbidden: set[str] = set(policy.get("forbidden_external_roots", []))
    wrappers: dict[str, list[str]] = {
        str(k): [str(x) for x in v]
        for k, v in dict(policy.get("wrapper_module_roots", {})).items()
    }
    allow_tests_direct = bool(policy.get("allow_tests_direct_imports", False))

    stdlib = set(getattr(sys, "stdlib_module_names", set()))
    local_roots = _local_roots(repo_root)

    violations: list[str] = []

    for imp in _collect_imports(repo_root):
        root = imp.root
        if root in local_roots:
            continue
        if root in stdlib:
            continue

        loc = f"{imp.path}:{imp.lineno}"

        if root in forbidden:
            violations.append(
                f"{loc}: forbidden external library root '{root}' ({imp.imported_module})"
            )
            continue

        if root in test_only_roots:
            if imp.module_name == "tests" or imp.module_name.startswith("tests."):
                continue
            violations.append(
                f"{loc}: test-only external library root '{root}' is not allowed in module '{imp.module_name}'"
            )
            continue

        if root not in approved:
            violations.append(
                f"{loc}: unapproved external library root '{root}' ({imp.imported_module})"
            )
            continue

        allowed_wrappers = wrappers.get(root, [])
        if not allowed_wrappers:
            continue

        if allow_tests_direct and imp.module_name.startswith("tests."):
            continue

        if not any(_module_matches_prefix(imp.module_name, pref) for pref in allowed_wrappers):
            wrapper_list = ", ".join(allowed_wrappers)
            violations.append(
                f"{loc}: '{root}' import is only allowed from wrappers [{wrapper_list}], "
                f"found in module '{imp.module_name}'"
            )

    if violations:
        msg = "Python library policy violations detected:\n" + "\n".join(violations[:200])
        return False, msg

    return True, ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check Python third-party library policy for deterministic/static-first Ahnali builds."
    )
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--policy", default=DEFAULT_POLICY_PATH)
    args = parser.parse_args(argv)

    ok, message = check_python_library_policy(
        repo_root=Path(args.repo_root),
        policy_path=Path(args.policy),
    )
    if not ok:
        emit_cli_error(message, code="PythonLibraryPolicyError")
        return 1
    emit_cli_info(
        f"Python library policy check passed: {args.policy}",
        code="PythonLibraryPolicyOK",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
