"""Analyze command - analyze Python source for feature usage."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from dataclasses import asdict

import click

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dsl.analyzer import analyze_features, select_runtime_modules
from cli.utils import echo


@click.command()
@click.argument("source", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o", "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Output JSON path (default: print to stdout)",
)
@click.option(
    "--modules/--no-modules",
    default=True,
    help="Show selected runtime modules",
)
def analyze(source: Path, output: Path | None, modules: bool):
    """Analyze Python source for feature usage and runtime selection.
    
    SOURCE is the path to your Python source file.
    
    Example:
        ahnali analyze myapp.py
        ahnali analyze myapp.py -o plan.json
    """
    source_text = source.read_text(encoding="utf-8")
    
    profile = analyze_features(source_text)
    result = {
        "file": str(source),
        "features": profile.to_dict(),
    }
    
    if modules:
        selected = select_runtime_modules(profile)
        result["runtime_modules"] = [asdict(m) for m in selected]
        result["module_names"] = [m.name for m in selected]
    
    json_output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json_output, encoding="utf-8")
        echo(f"✓ Analysis written to {output}")
    else:
        print(json_output, end="")