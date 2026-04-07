"""Run command - build, install, and run on device."""

from __future__ import annotations

import sys
from pathlib import Path
import importlib.util

import click

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.utils import echo


@click.command()
@click.argument("source", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--application-id",
    default="com.ahnali.app",
    help="Android application ID",
)
@click.option(
    "--min-sdk",
    type=int,
    default=21,
    help="Minimum Android SDK version",
)
@click.option(
    "--target-sdk",
    type=int,
    default=33,
    help="Target Android SDK version",
)
@click.option(
    "--uninstall/--no-uninstall",
    default=True,
    help="Uninstall before installing",
)
def run(source: Path, application_id: str, min_sdk: int, target_sdk: int, uninstall: bool):
    """Build, install, and run the app on device.
    
    SOURCE is the path to your Python source file.
    
    Example:
        ahnali run myapp.py
    """
    echo(f"Building and running {source}...")
    
    try:
        spec = importlib.util.spec_from_file_location("app_module", source)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Cannot load module from {source}")
        
        module = importlib.util.module_from_spec(spec)
        
        app_builtins = {
            "activity": None,
            "app": None,
            "button": None,
            "text": None,
            "on_click": lambda *args, **kwargs: (),
            "ui": None,
            "state": None,
        }
        
        module.__dict__.update(app_builtins)
        spec.loader.exec_module(module)
        
        app_obj = module.__dict__.get("app")
        if app_obj is None:
            raise RuntimeError("Source must define an 'app' using dsl.app.app()")
        
        app_spec = app_obj.run(
            application_id=application_id,
            min_sdk=min_sdk,
            target_sdk=target_sdk,
            uninstall_first=uninstall,
        )
        
        echo(f"✓ App installed and running")
        
    except Exception as e:
        import traceback
        echo(f"✗ Run failed: {e}", error=True)
        traceback.print_exc()
        sys.exit(1)