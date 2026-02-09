#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


DEFAULT_REPOS = [
    "https://dl.google.com/dl/android/maven2",
    "https://maven.google.com",
    "https://repo1.maven.org/maven2",
]
POM_NS = {"m": "http://maven.apache.org/POM/4.0.0"}


def _is_compose_artifact(group: str, artifact: str) -> bool:
    if group.startswith("androidx.compose"):
        return True
    if "compose" in artifact:
        return True
    return False


def _coord_parts(coord: str) -> tuple[str, str, str]:
    parts = coord.split(":")
    if len(parts) != 3:
        raise ValueError(f"Bad coord: {coord}")
    return parts[0], parts[1], parts[2]


def _maven_path(group: str, artifact: str, version: str) -> str:
    gpath = group.replace(".", "/")
    return f"{gpath}/{artifact}/{version}"


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=30) as resp, dest.open("wb") as f:
        f.write(resp.read())


def _read_pom(repos: list[str], group: str, artifact: str, version: str) -> str:
    base = _maven_path(group, artifact, version)
    last_err = None
    for repo in repos:
        pom_url = f"{repo}/{base}/{artifact}-{version}.pom"
        try:
            with urllib.request.urlopen(pom_url, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as exc:
            last_err = exc
            continue
    raise RuntimeError(f"Failed to fetch POM for {group}:{artifact}:{version}") from last_err


def _text(elem, path, default=""):
    if elem is None:
        return default
    val = elem.findtext(path, default="", namespaces=POM_NS)
    return val.strip() if val else default


def _resolve_props(value: str, props: dict[str, str]) -> str:
    if not value:
        return ""
    out = value
    # Replace ${...} tokens
    for _ in range(5):
        m = re.findall(r"\\$\\{([^}]+)\\}", out)
        if not m:
            break
        for key in m:
            rep = props.get(key, "")
            out = out.replace("${" + key + "}", rep)
    return out.strip()


def _parse_properties(root: ET.Element) -> dict[str, str]:
    props = {}
    props_elem = root.find("m:properties", POM_NS)
    if props_elem is not None:
        for child in list(props_elem):
            tag = child.tag.split("}", 1)[-1]
            if child.text:
                props[tag] = child.text.strip()
    return props


def _parse_dep_mgmt(root: ET.Element) -> dict[tuple[str, str], str]:
    out = {}
    dm = root.find("m:dependencyManagement", POM_NS)
    if dm is None:
        return out
    deps = dm.findall(".//m:dependency", POM_NS)
    for dep in deps:
        group = _text(dep, "m:groupId")
        artifact = _text(dep, "m:artifactId")
        version = _text(dep, "m:version")
        if group and artifact and version:
            out[(group, artifact)] = version
    return out


def _extract_deps(
    pom_text: str,
    *,
    props: dict[str, str],
    dep_mgmt: dict[tuple[str, str], str],
) -> list[tuple[str, str, str, str, str]]:
    deps = []
    root = ET.fromstring(pom_text)
    for dep in root.findall(".//m:dependency", POM_NS):
        group = dep.findtext("m:groupId", default="", namespaces=POM_NS)
        artifact = dep.findtext("m:artifactId", default="", namespaces=POM_NS)
        version = dep.findtext("m:version", default="", namespaces=POM_NS)
        scope = dep.findtext("m:scope", default="compile", namespaces=POM_NS)
        dep_type = dep.findtext("m:type", default="aar", namespaces=POM_NS)
        optional = dep.findtext("m:optional", default="false", namespaces=POM_NS)
        if scope not in ("compile", "runtime"):
            continue
        if optional.lower() == "true":
            continue
        if dep_type not in ("aar", "jar", ""):
            continue
        group = _resolve_props(group, props)
        artifact = _resolve_props(artifact, props)
        version = _resolve_props(version, props)
        if not version and (group, artifact) in dep_mgmt:
            version = _resolve_props(dep_mgmt[(group, artifact)], props)
        if not (group and artifact and version):
            continue
        if _is_compose_artifact(group, artifact):
            continue
        if "lint" in artifact:
            continue
        if artifact.endswith("-ktx") or artifact.endswith("-ktx-lint"):
            continue
        deps.append((group, artifact, version, scope, dep_type or "aar"))
    return deps


def _normalize_version(version: str) -> str:
    if not version:
        return ""
    v = re.sub(r"\\$\\{.*?\\}", "", version).strip()
    # Handle range syntax like [1.6.1] or [1.6.1,2.0)
    if v.startswith("[") or v.startswith("("):
        v = v[1:-1]
    if "," in v:
        parts = [p.strip() for p in v.split(",") if p.strip()]
        v = parts[0] if parts else ""
    return v


def _version_key(version: str) -> tuple:
    # Best-effort semantic-ish sort for Maven versions.
    parts = re.split(r"[.-]", version)
    key = []
    for p in parts:
        if p.isdigit():
            key.append((0, int(p)))
        else:
            key.append((1, p))
    return tuple(key)


def _merge_props(parent: dict[str, str], child: dict[str, str]) -> dict[str, str]:
    out = dict(parent)
    out.update(child)
    return out


def _merge_dep_mgmt(parent: dict[tuple[str, str], str], child: dict[tuple[str, str], str]) -> dict[tuple[str, str], str]:
    out = dict(parent)
    out.update(child)
    return out


def _parse_pom_meta(
    repos: list[str],
    group: str,
    artifact: str,
    version: str,
    *,
    visited: set[str] | None = None,
) -> tuple[str, dict[str, str], dict[tuple[str, str], str]]:
    visited = visited or set()
    key = f"{group}:{artifact}:{version}"
    if key in visited:
        return _read_pom(repos, group, artifact, version), {}, {}
    visited.add(key)
    pom_text = _read_pom(repos, group, artifact, version)
    root = ET.fromstring(pom_text)

    # Parent inheritance
    parent_props = {}
    parent_dep_mgmt = {}
    parent = root.find("m:parent", POM_NS)
    if parent is not None:
        p_group = _text(parent, "m:groupId")
        p_artifact = _text(parent, "m:artifactId")
        p_version = _text(parent, "m:version")
        if p_group and p_artifact and p_version:
            _, parent_props, parent_dep_mgmt = _parse_pom_meta(
                repos, p_group, p_artifact, p_version, visited=visited
            )

    props = _merge_props(parent_props, _parse_properties(root))
    # Standard properties
    props.setdefault("project.groupId", group)
    props.setdefault("project.artifactId", artifact)
    props.setdefault("project.version", version)
    props.setdefault("pom.groupId", group)
    props.setdefault("pom.artifactId", artifact)
    props.setdefault("pom.version", version)

    dep_mgmt = _merge_dep_mgmt(parent_dep_mgmt, _parse_dep_mgmt(root))

    # BOM imports
    dm = root.find("m:dependencyManagement", POM_NS)
    if dm is not None:
        for dep in dm.findall(".//m:dependency", POM_NS):
            scope = _text(dep, "m:scope", "compile")
            dep_type = _text(dep, "m:type", "jar")
            if dep_type != "pom" or scope != "import":
                continue
            b_group = _resolve_props(_text(dep, "m:groupId"), props)
            b_artifact = _resolve_props(_text(dep, "m:artifactId"), props)
            b_version = _resolve_props(_text(dep, "m:version"), props)
            if not (b_group and b_artifact and b_version):
                continue
            _, bom_props, bom_dep_mgmt = _parse_pom_meta(
                repos, b_group, b_artifact, b_version, visited=visited
            )
            props = _merge_props(props, bom_props)
            dep_mgmt = _merge_dep_mgmt(dep_mgmt, bom_dep_mgmt)

    return pom_text, props, dep_mgmt


def download_aars(
    coords: list[str],
    out_dir: Path,
    repos: list[str],
    *,
    progress: bool = True,
    progress_interval: float = 2.0,
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    seen = set()
    selected = {}
    queue = list(coords)
    processed = 0
    pom_fail = 0
    last_report = time.monotonic()

    while queue:
        coord = queue.pop(0)
        if coord in seen:
            continue
        seen.add(coord)
        processed += 1
        now = time.monotonic()
        if progress and (now - last_report) >= progress_interval:
            print(
                f"[download_aars] processed={processed} queued={len(queue)} "
                f"pom_fail={pom_fail}",
                file=sys.stderr,
            )
            last_report = now
        group, artifact, version = _coord_parts(coord)
        if _is_compose_artifact(group, artifact):
            continue
        version = _normalize_version(version)
        if not version:
            raise RuntimeError(f"Missing version for {coord}")
        ga = (group, artifact)
        prev = selected.get(ga)
        if prev is None or _version_key(version) > _version_key(prev):
            selected[ga] = version
        else:
            continue

        try:
            pom_text, props, dep_mgmt = _parse_pom_meta(repos, group, artifact, version)
        except Exception:
            pom_fail += 1
            continue
        for g, a, v, _, _ in _extract_deps(pom_text, props=props, dep_mgmt=dep_mgmt):
            v = _normalize_version(v)
            if v:
                queue.append(f"{g}:{a}:{v}")

    # Download selected AARs (deduped, highest versions only)
    resolved = []
    downloaded = 0
    last_report = time.monotonic()
    items = sorted(selected.items())
    for idx, ((group, artifact), version) in enumerate(items, start=1):
        if _is_compose_artifact(group, artifact):
            continue
        base = _maven_path(group, artifact, version)
        dest = out_dir / f"{artifact}-{version}.aar"
        if dest.exists():
            resolved.append(dest)
            continue
        downloaded_artifact = False
        for repo in repos:
            aar_url = f"{repo}/{base}/{artifact}-{version}.aar"
            try:
                _download(aar_url, dest)
                resolved.append(dest)
                downloaded += 1
                downloaded_artifact = True
                break
            except Exception:
                continue
        if not downloaded_artifact:
            jar_dest = out_dir / f"{artifact}-{version}.jar"
            for repo in repos:
                jar_url = f"{repo}/{base}/{artifact}-{version}.jar"
                try:
                    _download(jar_url, jar_dest)
                    resolved.append(jar_dest)
                    downloaded += 1
                    downloaded_artifact = True
                    break
                except Exception:
                    continue
        if progress:
            now = time.monotonic()
            if (now - last_report) >= progress_interval:
                print(
                    f"[download_aars] downloading {idx}/{len(items)} "
                    f"downloaded={downloaded}",
                    file=sys.stderr,
                )
                last_report = now
        if not downloaded_artifact:
            # Non-AAR or unavailable artifact; skip.
            continue

    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description="Download AARs from Maven.")
    parser.add_argument("--repo", action="append", default=None)
    parser.add_argument("--out", default="libs")
    parser.add_argument("--coord", action="append", default=None)
    parser.add_argument("--manifest", default="tools/aar_manifest.json")
    parser.add_argument("--no-progress", action="store_true", help="Disable progress output")
    parser.add_argument("--progress-interval", type=float, default=2.0)
    args = parser.parse_args()

    coords = args.coord
    if coords is None:
        manifest = Path(args.manifest)
        if not manifest.exists():
            raise SystemExit("No coords provided and manifest missing.")
        coords = json.loads(manifest.read_text()).get("coords", [])

    out_dir = Path(args.out)
    repos = args.repo or list(DEFAULT_REPOS)
    resolved = download_aars(
        coords,
        out_dir,
        repos,
        progress=not args.no_progress,
        progress_interval=args.progress_interval,
    )
    # Remove stale Compose artifacts to reduce size/noise.
    for path in out_dir.glob("*.aar"):
        name = path.name
        if "compose" in name:
            path.unlink(missing_ok=True)
            continue
        if name.startswith(("runtime-", "runtime-saveable-", "ui-")):
            path.unlink(missing_ok=True)
            continue
        if name in ("ui.aar", "runtime.aar"):
            path.unlink(missing_ok=True)
    resolved_list = [str(p) for p in resolved]
    (out_dir / "aar_resolved.json").write_text(
        json.dumps({"resolved": resolved_list, "coords": coords}, indent=2),
        encoding="utf-8",
    )
    for p in resolved:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
