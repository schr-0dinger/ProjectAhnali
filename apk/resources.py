# apk/resources.py

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import html


def _sanitize_name(name: str) -> str:
    out = []
    for ch in name:
        if ch.isalnum() or ch == "_":
            out.append(ch.lower())
        else:
            out.append("_")
    s = "".join(out).strip("_")
    if not s:
        s = "value"
    if s[0].isdigit():
        s = f"v_{s}"
    return s


@dataclass
class AndroidResources:
    strings: dict[str, str] = field(default_factory=dict)

    def add_string(self, name: str, value: str) -> str:
        key = _sanitize_name(name)
        base = key
        i = 2
        while key in self.strings and self.strings[key] != value:
            key = f"{base}_{i}"
            i += 1
        self.strings[key] = value
        return key

    def ensure_string(self, name: str, value: str) -> str:
        key = _sanitize_name(name)
        if key not in self.strings:
            self.strings[key] = value
        return key

    def render_strings_xml(self) -> str:
        lines = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>"]
        for name in sorted(self.strings.keys()):
            value = html.escape(self.strings[name], quote=False)
            lines.append(f'    <string name="{name}">{value}</string>')
        lines.append("</resources>")
        return "\n".join(lines) + "\n"

    def write_to_dir(self, out_dir: str | Path) -> Path:
        out_dir = Path(out_dir)
        values_dir = out_dir / "res" / "values"
        values_dir.mkdir(parents=True, exist_ok=True)
        strings_path = values_dir / "strings.xml"
        strings_path.write_text(self.render_strings_xml(), encoding="utf-8")
        return strings_path


def resources_from_mapping(mapping: dict[str, str] | None) -> AndroidResources:
    res = AndroidResources()
    if not mapping:
        return res
    for k, v in mapping.items():
        res.add_string(k, str(v))
    return res
