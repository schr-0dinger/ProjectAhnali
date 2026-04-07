#!/usr/bin/env python3
"""Ahnali CLI - Build and run Android apps from Python."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from cli.commands import build, run, analyze, init, install, list_pkgs, publish


@click.group()
@click.version_option(version="0.1.0", prog_name="ahnali")
def cli():
    """Ahnali - Python to Android compiler."""
    pass


cli.add_command(build.build)
cli.add_command(run.run)
cli.add_command(analyze.analyze)
cli.add_command(init.init)
cli.add_command(install.install)
cli.add_command(list_pkgs.list_packages)
cli.add_command(publish.publish)


def main():
    cli()


if __name__ == "__main__":
    main()