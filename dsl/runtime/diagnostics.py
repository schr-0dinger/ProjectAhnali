from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DiagnosticMessage:
    level: str
    code: str
    message: str
    hint: str = ""

    def as_plain_text(self) -> str:
        base = f"[{self.level}] {self.code}: {self.message}"
        if self.hint:
            return f"{base} Fix: {self.hint}"
        return base


class DiagnosticReporter:
    """Deterministic diagnostics wrapper.

    Uses Rich if available, otherwise returns plain-text rendering.
    """

    def __init__(self, *, use_rich: bool | None = None):
        self._console = None
        self._panel = None
        self._text = None

        if use_rich is False:
            return

        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.text import Text
        except Exception:
            return

        self._console = Console(record=True)
        self._panel = Panel
        self._text = Text

    def render(self, msg: DiagnosticMessage) -> str:
        if self._console is None:
            return msg.as_plain_text()

        style = {
            "error": "bold red",
            "warning": "yellow",
            "info": "cyan",
        }.get(msg.level.lower(), "white")
        body = msg.message
        if msg.hint:
            body = f"{body}\n\nFix: {msg.hint}"

        panel = self._panel(
            self._text(body, style=style),
            title=f"{msg.level.upper()} {msg.code}",
            border_style=style,
        )
        self._console.print(panel)
        text = self._console.export_text(clear=True)
        return text.rstrip("\n")
