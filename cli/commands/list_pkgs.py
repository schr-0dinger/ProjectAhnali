"""List packages command - list installed packages."""

from __future__ import annotations

import sys
from pathlib import Path
import json

import click

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.utils import echo


PACKAGES_DIR = Path.home() / ".ahnali" / "packages"


@click.command("list")
def list_packages():
    """List installed packages.
    
    Example:
        ahnali list
    """
    if not PACKAGES_DIR.exists():
        echo("No packages installed.")
        return
    
    packages = []
    for pkg_dir in PACKAGES_DIR.iterdir():
        if pkg_dir.is_dir():
            versions = [v.name for v in pkg_dir.iterdir() if v.is_dir()]
            if versions:
                packages.append({"name": pkg_dir.name, "versions": versions})
    
    if not packages:
        echo("No packages installed.")
        return
    
    echo("Installed packages:")
    for pkg in sorted(packages, key=lambda p: p["name"]):
        versions_str = ", ".join(pkg["versions"])
        echo(f"  {pkg['name']}: {versions_str}")