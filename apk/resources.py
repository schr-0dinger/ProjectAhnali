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


def _escape_android_string(value: str) -> str:
    # Android string resources require apostrophes to be backslash-escaped.
    # Backslashes must also be escaped to preserve literal content.
    text = str(value).replace("\\", "\\\\").replace("'", "\\'")
    return html.escape(text, quote=False)


@dataclass
class AndroidResources:
    strings: dict[str, str] = field(default_factory=dict)
    string_ids: dict[str, int] = field(default_factory=dict)
    colors: dict[str, str] = field(default_factory=dict)
    color_ids: dict[str, int] = field(default_factory=dict)
    dimens: dict[str, str] = field(default_factory=dict)
    dimen_ids: dict[str, int] = field(default_factory=dict)
    styles: dict[str, dict[str, str]] = field(default_factory=dict)
    style_ids: dict[str, int] = field(default_factory=dict)

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

    def add_color(self, name: str, value: str) -> str:
        key = _sanitize_name(name)
        base = key
        i = 2
        while key in self.colors and self.colors[key] != value:
            key = f"{base}_{i}"
            i += 1
        self.colors[key] = value
        return key

    def ensure_color(self, name: str, value: str) -> str:
        key = _sanitize_name(name)
        if key not in self.colors:
            self.colors[key] = value
        return key

    def add_dimen(self, name: str, value: str) -> str:
        key = _sanitize_name(name)
        base = key
        i = 2
        while key in self.dimens and self.dimens[key] != value:
            key = f"{base}_{i}"
            i += 1
        self.dimens[key] = value
        return key

    def ensure_dimen(self, name: str, value: str) -> str:
        key = _sanitize_name(name)
        if key not in self.dimens:
            self.dimens[key] = value
        return key

    def add_style(self, name: str, items: dict[str, str]) -> str:
        key = _sanitize_name(name)
        base = key
        i = 2
        while key in self.styles and self.styles[key] != items:
            key = f"{base}_{i}"
            i += 1
        self.styles[key] = dict(items)
        return key

    def render_strings_xml(self) -> str:
        lines = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>"]
        for name in sorted(self.strings.keys()):
            value = _escape_android_string(self.strings[name])
            lines.append(f'    <string name="{name}">{value}</string>')
        lines.append("</resources>")
        return "\n".join(lines) + "\n"

    def render_colors_xml(self) -> str:
        lines = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>"]
        for name in sorted(self.colors.keys()):
            value = html.escape(self.colors[name], quote=False)
            lines.append(f'    <color name="{name}">{value}</color>')
        lines.append("</resources>")
        return "\n".join(lines) + "\n"

    def render_dimens_xml(self) -> str:
        lines = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>"]
        for name in sorted(self.dimens.keys()):
            value = html.escape(self.dimens[name], quote=False)
            lines.append(f'    <dimen name="{name}">{value}</dimen>')
        lines.append("</resources>")
        return "\n".join(lines) + "\n"

    def render_styles_xml(self) -> str:
        lines = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>"]
        for name in sorted(self.styles.keys()):
            lines.append(f'    <style name="{name}">')
            for item_name, item_value in sorted(self.styles[name].items()):
                value = html.escape(str(item_value), quote=False)
                lines.append(f'        <item name="{item_name}">{value}</item>')
            lines.append("    </style>")
        lines.append("</resources>")
        return "\n".join(lines) + "\n"

    def write_to_dir(self, out_dir: str | Path) -> Path:
        out_dir = Path(out_dir)
        values_dir = out_dir / "res" / "values"
        values_dir.mkdir(parents=True, exist_ok=True)
        strings_path = values_dir / "strings.xml"
        strings_path.write_text(self.render_strings_xml(), encoding="utf-8")
        if self.colors:
            (values_dir / "colors.xml").write_text(self.render_colors_xml(), encoding="utf-8")
        if self.dimens:
            (values_dir / "dimens.xml").write_text(self.render_dimens_xml(), encoding="utf-8")
        if self.styles:
            (values_dir / "styles.xml").write_text(self.render_styles_xml(), encoding="utf-8")
        return strings_path

    def ensure_string_id(self, name: str, value: int) -> int:
        self.string_ids[name] = int(value)
        return self.string_ids[name]

    def ensure_color_id(self, name: str, value: int) -> int:
        self.color_ids[name] = int(value)
        return self.color_ids[name]

    def ensure_dimen_id(self, name: str, value: int) -> int:
        self.dimen_ids[name] = int(value)
        return self.dimen_ids[name]

    def ensure_style_id(self, name: str, value: int) -> int:
        self.style_ids[name] = int(value)
        return self.style_ids[name]

    def render_stable_ids(self, application_id: str) -> str:
        lines = []
        for name in sorted(self.string_ids.keys()):
            rid = self.string_ids[name]
            lines.append(f"{application_id}:string/{name} = 0x{rid:08x}")
        for name in sorted(self.color_ids.keys()):
            rid = self.color_ids[name]
            lines.append(f"{application_id}:color/{name} = 0x{rid:08x}")
        for name in sorted(self.dimen_ids.keys()):
            rid = self.dimen_ids[name]
            lines.append(f"{application_id}:dimen/{name} = 0x{rid:08x}")
        for name in sorted(self.style_ids.keys()):
            rid = self.style_ids[name]
            lines.append(f"{application_id}:style/{name} = 0x{rid:08x}")
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
    for k, v in (getattr(program, "resource_colors", None) or {}).items():
        res.add_color(k, str(v))
    for k, v in (getattr(program, "resource_dimens", None) or {}).items():
        res.add_dimen(k, str(v))
    for k, v in (getattr(program, "resource_styles", None) or {}).items():
        if isinstance(v, dict):
            res.add_style(k, {str(ik): str(iv) for ik, iv in v.items()})
    for k, v in (getattr(program, "resource_color_ids", None) or {}).items():
        res.ensure_color_id(k, int(v))
    for k, v in (getattr(program, "resource_dimen_ids", None) or {}).items():
        res.ensure_dimen_id(k, int(v))
    for k, v in (getattr(program, "resource_style_ids", None) or {}).items():
        res.ensure_style_id(k, int(v))
    return res
