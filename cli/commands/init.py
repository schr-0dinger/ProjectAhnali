"""Init command - scaffold a new project."""

from __future__ import annotations

import sys
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.utils import echo


@click.command()
@click.argument("name")
@click.option(
    "-o", "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Output directory (default: current directory)",
)
@click.option(
    "--minimal",
    is_flag=True,
    help="Create minimal project without example code",
)
def init(name: str, output: Path | None, minimal: bool):
    """Initialize a new Ahnali project.
    
    NAME is the name of your project.
    
    Example:
        ahnali init myapp
        ahnali init myapp -o ./projects/myapp
    """
    target_dir = output or Path.cwd() / name
    target_dir.mkdir(parents=True, exist_ok=True)
    
    echo(f"Creating project '{name}' in {target_dir}...")
    
    (target_dir / "app.py").write_text(_TEMPLATE_MINIMAL if minimal else _TEMPLATE_DEFAULT, encoding="utf-8")
    (target_dir / "requirements.txt").write_text(_REQUIREMENTS, encoding="utf-8")
    (target_dir / "README.md").write_text(_README_TEMPLATE.format(name=name), encoding="utf-8")
    
    echo(f"✓ Project created!")
    echo(f"  Run: cd {target_dir}")
    echo(f"  Then: ahnali build app.py")


_REQUIREMENTS = """ahnali>=0.1.0
"""

_TEMPLATE_MINIMAL = """from dsl.app import app, activity, ui, text, button, on_click

app(
    activity("MainActivity",
        ui(
            text("Hello, World!", id="label"),
            button("Click me", id="btn"),
        ),
    ),
)
"""

_TEMPLATE_DEFAULT = """from dsl.app import app, activity, ui, text, button, on_click, state

# Example counter app
app(
    activity("Counter",
        state("count", 0),
        ui(
            text("Count: 0", id="label"),
            button("Increment", id="inc_btn"),
            button("Decrement", id="dec_btn"),
            button("Reset", id="reset_btn"),
        ),
        # Increment button
        on_click("inc_btn", [
            # TODO: Add increment logic
        ]),
        # Decrement button
        on_click("dec_btn", [
            # TODO: Add decrement logic
        ]),
        # Reset button
        on_click("reset_btn", [
            # TODO: Add reset logic
        ]),
    ),
)
"""

_README_TEMPLATE = """# {name}

An Ahnali project.

## Run

```bash
ahnali run app.py
```

## Build

```bash
ahnali build app.py -o dist/{name}.apk
```
"""