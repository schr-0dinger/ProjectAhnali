import json
from pathlib import Path

from tools.python_library_policy import check_python_library_policy


def _write_policy(path: Path):
    policy = {
        "schema_version": "python_library_policy/1",
        "approved_external_roots": ["rich", "httpx", "tenacity", "pydantic"],
        "test_only_external_roots": ["pytest"],
        "forbidden_external_roots": ["rx", "reactivex", "sqlalchemy"],
        "wrapper_module_roots": {
            "rich": ["dsl.runtime.diagnostics"],
            "httpx": ["dsl.runtime.http_client"],
            "tenacity": ["dsl.runtime.http_client"],
            "pydantic": ["dsl.runtime.models"],
        },
        "allow_tests_direct_imports": False,
        "static_mode_invariants": {
            "static_default": True,
            "reactive_opt_in": True,
            "no_implicit_observers_in_static_mode": True,
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(policy, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_python_library_policy_repo_check_passes():
    ok, message = check_python_library_policy(
        repo_root=Path("."),
        policy_path=Path("cfg/python_library_policy.json"),
    )
    assert ok, message


def test_python_library_policy_flags_forbidden_external_import(tmp_path):
    (tmp_path / "foo.py").write_text("import rx\n", encoding="utf-8")
    policy_path = tmp_path / "cfg" / "python_library_policy.json"
    _write_policy(policy_path)

    ok, message = check_python_library_policy(repo_root=tmp_path, policy_path=policy_path)
    assert not ok
    assert "forbidden external library root 'rx'" in message


def test_python_library_policy_flags_unapproved_external_import(tmp_path):
    (tmp_path / "foo.py").write_text("import requests\n", encoding="utf-8")
    policy_path = tmp_path / "cfg" / "python_library_policy.json"
    _write_policy(policy_path)

    ok, message = check_python_library_policy(repo_root=tmp_path, policy_path=policy_path)
    assert not ok
    assert "unapproved external library root 'requests'" in message


def test_python_library_policy_flags_approved_import_outside_wrapper(tmp_path):
    (tmp_path / "foo.py").write_text("import httpx\n", encoding="utf-8")
    policy_path = tmp_path / "cfg" / "python_library_policy.json"
    _write_policy(policy_path)

    ok, message = check_python_library_policy(repo_root=tmp_path, policy_path=policy_path)
    assert not ok
    assert "'httpx' import is only allowed from wrappers" in message


def test_python_library_policy_allows_approved_wrapper_import(tmp_path):
    wrapper = tmp_path / "dsl" / "runtime" / "http_client.py"
    wrapper.parent.mkdir(parents=True, exist_ok=True)
    wrapper.write_text("import httpx\n", encoding="utf-8")
    policy_path = tmp_path / "cfg" / "python_library_policy.json"
    _write_policy(policy_path)

    ok, message = check_python_library_policy(repo_root=tmp_path, policy_path=policy_path)
    assert ok, message


def test_python_library_policy_restricts_test_only_roots_to_tests(tmp_path):
    (tmp_path / "foo.py").write_text("import pytest\n", encoding="utf-8")
    policy_path = tmp_path / "cfg" / "python_library_policy.json"
    _write_policy(policy_path)

    ok, message = check_python_library_policy(repo_root=tmp_path, policy_path=policy_path)
    assert not ok
    assert "test-only external library root 'pytest'" in message
