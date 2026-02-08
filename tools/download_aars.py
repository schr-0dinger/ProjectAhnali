#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


DEFAULT_REPOS = [
    "https://dl.google.com/dl/android/maven2",
    "https://maven.google.com",
    "https://repo1.maven.org/maven2",
]
POM_NS = {"m": "http://maven.apache.org/POM/4.0.0"}


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
    with urllib.request.urlopen(url) as resp, dest.open("wb") as f:
        f.write(resp.read())


def _read_pom(repos: list[str], group: str, artifact: str, version: str) -> str:
    base = _maven_path(group, artifact, version)
    last_err = None
    for repo in repos:
        pom_url = f"{repo}/{base}/{artifact}-{version}.pom"
        try:
            with urllib.request.urlopen(pom_url) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as exc:
            last_err = exc
            continue
    raise RuntimeError(f"Failed to fetch POM for {group}:{artifact}:{version}") from last_err


def _extract_deps(pom_text: str) -> list[tuple[str, str, str, str]]:
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
        if dep_type not in ("aar", ""):
            continue
        if not (group and artifact and version):
            continue
        if "lint" in artifact:
            continue
        if artifact.endswith("-ktx") or artifact.endswith("-ktx-lint"):
            continue
        deps.append((group, artifact, version, scope))
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


def download_aars(coords: list[str], out_dir: Path, repos: list[str]) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    resolved = []
    seen = set()
    queue = list(coords)

    while queue:
        coord = queue.pop(0)
        if coord in seen:
            continue
        seen.add(coord)
        group, artifact, version = _coord_parts(coord)
        version = _normalize_version(version)
        if not version:
            raise RuntimeError(f"Missing version for {coord}")

        base = _maven_path(group, artifact, version)
        aar_url = f"{repos[0]}/{base}/{artifact}-{version}.aar"
        dest = out_dir / f"{artifact}-{version}.aar"
        aar_downloaded = False
        for repo in repos:
            aar_url = f"{repo}/{base}/{artifact}-{version}.aar"
            try:
                _download(aar_url, dest)
                resolved.append(dest)
                aar_downloaded = True
                break
            except Exception:
                continue
        if not aar_downloaded:
            # If no AAR, skip downloading but still parse POM.
            pass

        try:
            pom_text = _read_pom(repos, group, artifact, version)
        except Exception:
            continue
        for g, a, v, _ in _extract_deps(pom_text):
            v = _normalize_version(v)
            if v:
                queue.append(f"{g}:{a}:{v}")

    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description="Download AARs from Maven.")
    parser.add_argument("--repo", action="append", default=None)
    parser.add_argument("--out", default="libs")
    parser.add_argument("--coord", action="append", default=None)
    parser.add_argument("--manifest", default="tools/aar_manifest.json")
    args = parser.parse_args()

    coords = args.coord
    if coords is None:
        manifest = Path(args.manifest)
        if not manifest.exists():
            raise SystemExit("No coords provided and manifest missing.")
        coords = json.loads(manifest.read_text()).get("coords", [])

    out_dir = Path(args.out)
    repos = args.repo or list(DEFAULT_REPOS)
    resolved = download_aars(coords, out_dir, repos)
    for p in resolved:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
