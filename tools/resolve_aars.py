#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


DEFAULT_COORDS = [
    "androidx.constraintlayout:constraintlayout",
    "com.google.android.material:material",
    "androidx.appcompat:appcompat",
    "androidx.core:core",
    "androidx.coordinatorlayout:coordinatorlayout",
    "androidx.recyclerview:recyclerview",
    "androidx.cardview:cardview",
    "androidx.drawerlayout:drawerlayout",
    "androidx.customview:customview",
    "androidx.vectordrawable:vectordrawable",
    "androidx.transition:transition",
    "androidx.viewpager:viewpager",
    "androidx.viewpager2:viewpager2",
    "androidx.fragment:fragment",
    "androidx.activity:activity",
]


def _find_gradle_cache() -> Path:
    home = Path.home()
    return home / ".gradle" / "caches" / "modules-2" / "files-2.1"


def _find_latest_aar(cache_root: Path, group: str, artifact: str) -> Path | None:
    group_path = cache_root / group
    artifact_path = group_path / artifact
    if not artifact_path.exists():
        return None
    versions = sorted((p for p in artifact_path.iterdir() if p.is_dir()), reverse=True)
    for ver in versions:
        aar = next(ver.rglob("*.aar"), None)
        if aar is not None:
            return aar
    return None


def resolve_aars(coords: list[str], out_dir: Path) -> list[Path]:
    cache_root = _find_gradle_cache()
    out_dir.mkdir(parents=True, exist_ok=True)
    resolved = []
    missing = []
    for coord in coords:
        group, artifact = coord.split(":", 1)
        aar_path = _find_latest_aar(cache_root, group, artifact)
        if aar_path is None:
            missing.append(coord)
            continue
        dest = out_dir / aar_path.name
        shutil.copy2(aar_path, dest)
        resolved.append(dest)
    if missing:
        missing_list = ", ".join(missing)
        raise SystemExit(
            f"Missing AARs in Gradle cache: {missing_list}. "
            "Build them once with Gradle or download from Maven Central."
        )
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve AARs from Gradle cache.")
    parser.add_argument("--out", default="libs", help="Output directory for AARs.")
    parser.add_argument("--coord", action="append", default=None, help="group:artifact (repeatable)")
    args = parser.parse_args()

    coords = args.coord or list(DEFAULT_COORDS)
    out_dir = Path(args.out)
    resolved = resolve_aars(coords, out_dir)
    for p in resolved:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
