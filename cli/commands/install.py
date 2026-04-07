"""Install command - install packages from registry."""

from __future__ import annotations

import sys
from pathlib import Path
import urllib.request
import json
import zipfile

import click

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.utils import echo, die


DEFAULT_REGISTRY = "https://ahnali-pkg.github.io/packages/index.json"
PACKAGES_DIR = Path.home() / ".ahnali" / "packages"


@click.command()
@click.argument("package")
@click.option(
    "--registry",
    default=DEFAULT_REGISTRY,
    help="Package registry URL",
)
@click.option(
    "--version",
    default="latest",
    help="Specific version to install",
)
def install(package: str, registry: str, version: str):
    """Install a package from the registry.
    
    PACKAGE is the package name (e.g., 'ui-charts', 'http-client').
    
    Example:
        ahnali install ui-charts
    """
    echo(f"Installing {package}@{version} from {registry}...")
    
    try:
        PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
        
        with urllib.request.urlopen(registry, timeout=10) as resp:
            package_index = json.loads(resp.read().decode("utf-8"))
        
        pkg_info = None
        for p in package_index.get("packages", []):
            if p.get("name") == package:
                pkg_info = p
                break
        
        if pkg_info is None:
            die(f"Package '{package}' not found in registry")
        
        version_to_use = version
        if version == "latest":
            version_to_use = pkg_info.get("latest", pkg_info["versions"][-1])
        
        download_url = None
        for v in pkg_info.get("versions", []):
            if v.get("version") == version_to_use:
                download_url = v.get("download_url")
                break
        
        if not download_url:
            die(f"Version {version} not found for {package}")
        
        echo(f"Downloading {download_url}...")
        
        with urllib.request.urlopen(download_url, timeout=30) as resp:
            package_data = resp.read()
        
        pkg_dir = PACKAGES_DIR / package / version_to_use
        pkg_dir.mkdir(parents=True, exist_ok=True)
        
        zip_path = pkg_dir / "package.zip"
        zip_path.write_bytes(package_data)
        
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(pkg_dir)
        
        zip_path.unlink()
        
        echo(f"✓ Installed {package}@{version_to_use}")
        echo(f"  Location: {pkg_dir}")
        
    except Exception as e:
        die(f"Installation failed: {e}")