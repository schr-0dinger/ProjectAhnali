"""Publish command - publish a package to the registry."""

from __future__ import annotations

import sys
from pathlib import Path
import json
import zipfile

import click

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.utils import echo, die


@click.command()
@click.argument("package_dir", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--registry",
    default="https://ahnali-pkg.github.io/packages/submit",
    help="Registry submit URL",
)
@click.option(
    "--version",
    required=True,
    help="Package version (e.g., 1.0.0)",
)
@click.option(
    "--name",
    required=True,
    help="Package name",
)
@click.option(
    "--description",
    default="",
    help="Package description",
)
def publish(package_dir: Path, registry: str, version: str, name: str, description: str):
    """Publish a package to the registry.
    
    PACKAGE_DIR is the directory containing the package source.
    
    Example:
        ahnali publish ./my-package --name ui-charts --version 1.0.0
    """
    echo(f"Publishing {name}@{version} to {registry}...")
    
    required_files = ["__init__.py", "package.json"]
    for f in required_files:
        if not (package_dir / f).exists():
            die(f"Package must contain {f}")
    
    metadata = {
        "name": name,
        "version": version,
        "description": description,
    }
    
    zip_path = package_dir / "dist" / f"{name}-{version}.zip"
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in package_dir.rglob("*.py"):
            arcname = file_path.relative_to(package_dir)
            zf.write(file_path, arcname)
    
    echo(f"✓ Package created: {zip_path}")
    echo(f"  To publish, upload to your registry or submit PR to {registry}")