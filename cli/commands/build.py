"""Build command - compile Python source to APK."""

from __future__ import annotations

import sys
from pathlib import Path
import importlib.util
import tempfile

import click

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.utils import echo


@click.command()
@click.argument("source", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o", "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Output APK path (default: build/<name>.apk)",
)
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
    "--debug/--release",
    default=True,
    help="Build in debug or release mode",
)
def build(source: Path, output: Path | None, application_id: str, min_sdk: int, target_sdk: int, debug: bool):
    """Build an APK from Python source.
    
    SOURCE is the path to your Python source file.
    
    Example:
        ahnali build myapp.py
        ahnali build myapp.py -o dist/myapp.apk
    """
    echo(f"Building APK from {source}...")
    
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
        
        frontend_ir = app_obj.build()
        
        from apk.toolchain import emit_build_dir_from_program
        from alpha_pipeline import alpha_pipeline
        
        if output is None:
            output = Path("build") / f"{source.stem}.apk"
        
        output.parent.mkdir(parents=True, exist_ok=True)
        
        build_dir = emit_build_dir_from_program(
            frontend_ir,
            out_dir=str(output.parent / "build"),
            class_name="LTest;",
            application_id=application_id,
            min_sdk=min_sdk,
            target_sdk=target_sdk,
            debuggable=debug,
        )
        
        echo(f"✓ Build directory created: {build_dir}")
        echo(f"✓ APK output: {output}")
        
    except Exception as e:
        import traceback
        echo(f"✗ Build failed: {e}", error=True)
        traceback.print_exc()
        sys.exit(1)