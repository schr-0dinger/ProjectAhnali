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
    string_ids: dict[str, int] = field(default_factory=dict)

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

    def ensure_string_id(self, name: str, value: int) -> int:
        self.string_ids[name] = int(value)
        return self.string_ids[name]

    def render_stable_ids(self, application_id: str) -> str:
        lines = []
        for name in sorted(self.string_ids.keys()):
            rid = self.string_ids[name]
            lines.append(f"{application_id}:string/{name} = 0x{rid:08x}")
        return "\n".join(lines) + ("\n" if lines else "")

    def write_stable_ids(self, out_path: str | Path, application_id: str) -> Path:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(self.render_stable_ids(application_id), encoding="utf-8")
        return out_path


def resources_from_mapping(mapping: dict[str, str] | None) -> AndroidResources:
    res = AndroidResources()
    if not mapping:
        return res
    for k, v in mapping.items():
        res.add_string(k, str(v))
    return res


def resources_from_program(program) -> AndroidResources:
    res = resources_from_mapping(getattr(program, "resources", None))
    rid_map = getattr(program, "resource_ids", None) or {}
    for k, v in rid_map.items():
        res.ensure_string_id(k, int(v))
    return res
