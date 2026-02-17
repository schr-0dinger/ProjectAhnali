from __future__ import annotations

from dataclasses import dataclass
import sys


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
        self._stderr_console = None
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
        self._stderr_console = Console(stderr=True)
        self._panel = Panel
        self._text = Text

    @property
    def rich_enabled(self) -> bool:
        return self._console is not None and self._panel is not None and self._text is not None

    def _panel_obj(self, msg: DiagnosticMessage):
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
        return panel

    def render(self, msg: DiagnosticMessage) -> str:
        if self._console is None:
            return msg.as_plain_text()

        panel = self._panel_obj(msg)
        self._console.print(panel)
        text = self._console.export_text(clear=True)
        return text.rstrip("\n")

    def emit(self, msg: DiagnosticMessage, *, stderr: bool = False):
        if self.rich_enabled:
            panel = self._panel_obj(msg)
            if stderr:
                self._stderr_console.print(panel)
            else:
                self._console.print(panel)
            return
        out = msg.as_plain_text()
        stream = sys.stderr if stderr else sys.stdout
        print(out, file=stream)


def _split_prefixed_code(raw_message: str) -> tuple[str | None, str]:
    text = str(raw_message or "").strip()
    if not text.startswith("["):
        return None, text
    end = text.find("]")
    if end <= 1:
        return None, text
    code = text[1:end].strip()
    rest = text[end + 1 :].strip()
    if not code:
        return None, text
    return code, rest or text


def emit_cli_info(
    message: str,
    *,
    code: str = "Info",
    hint: str = "",
    reporter: DiagnosticReporter | None = None,
):
    rep = reporter or DiagnosticReporter()
    rep.emit(
        DiagnosticMessage(
            level="info",
            code=code,
            message=str(message),
            hint=str(hint),
        ),
        stderr=False,
    )


def emit_cli_error(
    message: str,
    *,
    code: str = "Error",
    hint: str = "",
    reporter: DiagnosticReporter | None = None,
):
    rep = reporter or DiagnosticReporter()
    prefixed_code, stripped = _split_prefixed_code(str(message))
    rep.emit(
        DiagnosticMessage(
            level="error",
            code=prefixed_code or code,
            message=stripped,
            hint=str(hint),
        ),
        stderr=True,
    )


def emit_cli_exception(
    exc: BaseException,
    *,
    code: str = "CompilerError",
    hint: str = "",
    reporter: DiagnosticReporter | None = None,
):
    emit_cli_error(
        str(exc),
        code=code,
        hint=hint,
        reporter=reporter,
    )
