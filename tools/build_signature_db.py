#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path


def _class_desc(name: str) -> str:
    return "L" + name.replace(".", "/") + ";"


def _parse_type_list(sig: str) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(sig):
        c = sig[i]
        if c in "ZBCSIFJDV":
            out.append(c)
            i += 1
            continue
        if c == "L":
            j = sig.find(";", i)
            out.append(sig[i : j + 1])
            i = j + 1
            continue
        if c == "[":
            start = i
            i += 1
            while i < len(sig) and sig[i] == "[":
                i += 1
            if i < len(sig) and sig[i] == "L":
                j = sig.find(";", i)
                out.append(sig[start : j + 1])
                i = j + 1
            else:
                out.append(sig[start : i + 1])
                i += 1
            continue
        raise ValueError(f"Unexpected type descriptor: {sig}")
    return out


def _parse_descriptor(desc: str) -> tuple[list[str], str]:
    if not desc.startswith("("):
        raise ValueError(f"Bad descriptor: {desc}")
    args_sig, ret_sig = desc.split(")", 1)
    args = _parse_type_list(args_sig[1:])
    ret = ret_sig
    return args, ret


def _read_u1(data: bytes, idx: int) -> tuple[int, int]:
    return data[idx], idx + 1


def _read_u2(data: bytes, idx: int) -> tuple[int, int]:
    return int.from_bytes(data[idx : idx + 2], "big"), idx + 2


def _read_u4(data: bytes, idx: int) -> tuple[int, int]:
    return int.from_bytes(data[idx : idx + 4], "big"), idx + 4


def _read_cp_entry(data: bytes, idx: int):
    tag, idx = _read_u1(data, idx)
    if tag == 1:  # Utf8
        length, idx = _read_u2(data, idx)
        value = data[idx : idx + length].decode("utf-8", errors="replace")
        return ("Utf8", value), idx + length, 1
    if tag == 7:  # Class
        name_index, idx = _read_u2(data, idx)
        return ("Class", name_index), idx, 1
    if tag == 8:  # String
        idx2, idx = _read_u2(data, idx)
        return ("String", idx2), idx, 1
    if tag in (9, 10, 11):  # Field/Method/InterfaceMethod ref
        idx = idx + 4
        return ("Ref", None), idx, 1
    if tag == 12:  # NameAndType
        idx = idx + 4
        return ("NameType", None), idx, 1
    if tag in (3, 4):  # Integer/Float
        idx = idx + 4
        return ("Num", None), idx, 1
    if tag in (5, 6):  # Long/Double (two slots)
        idx = idx + 8
        return ("Num2", None), idx, 2
    if tag == 15:  # MethodHandle
        idx = idx + 3
        return ("Handle", None), idx, 1
    if tag == 16:  # MethodType
        idx = idx + 2
        return ("MethodType", None), idx, 1
    if tag == 18:  # InvokeDynamic
        idx = idx + 4
        return ("InvokeDynamic", None), idx, 1
    if tag in (19, 20):  # Module, Package
        idx = idx + 2
        return ("Module", None), idx, 1
    raise ValueError(f"Unsupported constant pool tag {tag}")


def _parse_classfile(data: bytes):
    idx = 0
    magic, idx = _read_u4(data, idx)
    if magic != 0xCAFEBABE:
        raise ValueError("Bad class file")
    _, idx = _read_u2(data, idx)
    _, idx = _read_u2(data, idx)
    cp_count, idx = _read_u2(data, idx)
    cp = [None] * cp_count
    i = 1
    while i < cp_count:
        entry, idx, slots = _read_cp_entry(data, idx)
        cp[i] = entry
        i += slots
    access_flags, idx = _read_u2(data, idx)
    this_class, idx = _read_u2(data, idx)
    _, idx = _read_u2(data, idx)
    interfaces_count, idx = _read_u2(data, idx)
    idx += interfaces_count * 2
    fields_count, idx = _read_u2(data, idx)
    for _ in range(fields_count):
        idx += 6
        attr_count, idx = _read_u2(data, idx)
        for _ in range(attr_count):
            _, idx = _read_u2(data, idx)
            length, idx = _read_u4(data, idx)
            idx += length
    methods = []
    methods_count, idx = _read_u2(data, idx)
    for _ in range(methods_count):
        m_access, idx = _read_u2(data, idx)
        name_index, idx = _read_u2(data, idx)
        desc_index, idx = _read_u2(data, idx)
        attr_count, idx = _read_u2(data, idx)
        for _ in range(attr_count):
            _, idx = _read_u2(data, idx)
            length, idx = _read_u4(data, idx)
            idx += length
        methods.append((m_access, name_index, desc_index))
    class_entry = cp[this_class]
    if class_entry is None or class_entry[0] != "Class":
        raise ValueError("Bad class name")
    name_index = class_entry[1]
    name_entry = cp[name_index]
    class_name = name_entry[1]
    return access_flags, class_name, cp, methods


def build_signatures(android_jar: Path, prefixes: list[str]) -> tuple[dict, dict]:
    method_sigs: dict[tuple[str, str, str], list[tuple[str | None, list[str]]]] = {}
    ctor_sigs: dict[str, list[str]] = {}

    with zipfile.ZipFile(android_jar, "r") as zf:
        for name in zf.namelist():
            if not name.endswith(".class"):
                continue
            if name.endswith("module-info.class"):
                continue
            class_name = name[:-6]
            dotted = class_name.replace("/", ".")
            if prefixes and not any(dotted.startswith(p) for p in prefixes):
                continue
            data = zf.read(name)
            try:
                access_flags, internal_name, cp, methods = _parse_classfile(data)
            except ValueError:
                continue
            is_interface = bool(access_flags & 0x0200)
            owner_desc = "L" + internal_name + ";"

            for m_access, name_index, desc_index in methods:
                if not (m_access & 0x0001):
                    continue
                name_entry = cp[name_index]
                desc_entry = cp[desc_index]
                if not name_entry or not desc_entry:
                    continue
                method_name = name_entry[1]
                desc = desc_entry[1]
                args, ret = _parse_descriptor(desc)
                is_ctor = method_name == "<init>"
                if is_ctor:
                    ctor_sigs.setdefault(owner_desc, args)
                    key = (owner_desc, "<init>", "direct")
                    method_sigs.setdefault(key, []).append((None, args))
                    continue
                is_static = bool(m_access & 0x0008)
                invoke_kind = "static" if is_static else ("interface" if is_interface else "virtual")
                key = (owner_desc, method_name, invoke_kind)
                method_sigs.setdefault(key, []).append((ret if ret != "V" else None, args))

    return method_sigs, ctor_sigs


def _serialize_method_sigs(method_sigs: dict) -> list[dict]:
    out = []
    for (owner, name, invoke_kind), sigs in sorted(method_sigs.items()):
        for ret, args in sigs:
            out.append(
                {
                    "owner": owner,
                    "name": name,
                    "invoke": invoke_kind,
                    "ret": ret,
                    "args": args,
                }
            )
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Build signature DB from android.jar")
    parser.add_argument("--jar", default="android.jar")
    parser.add_argument("--out", default="dsl/android/signatures_db.json")
    parser.add_argument(
        "--prefix",
        action="append",
        default=["android.", "java.", "javax."],
        help="Class name prefix to include (repeatable)",
    )
    args = parser.parse_args()

    android_jar = Path(args.jar)
    if not android_jar.exists():
        raise SystemExit(f"android.jar not found: {android_jar}")

    method_sigs, ctor_sigs = build_signatures(android_jar, args.prefix)

    payload = {
        "methods": _serialize_method_sigs(method_sigs),
        "ctors": [{"owner": k, "args": v} for k, v in sorted(ctor_sigs.items())],
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
