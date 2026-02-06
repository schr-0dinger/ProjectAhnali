# apk/toolchain.py

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

from alpha_pipeline import alpha_pipeline


def _class_desc_from_smali(smali_text: str) -> str:
    for line in smali_text.splitlines():
        line = line.strip()
        if line.startswith(".class "):
            parts = line.split()
            return parts[-1]
    raise RuntimeError("Could not find .class descriptor in Smali")


def _class_desc_to_path(desc: str) -> Path:
    if desc.startswith("L") and desc.endswith(";"):
        desc = desc[1:-1]
    return Path(*desc.split("/"))


def emit_build_dir(smali_text: str, out_dir: str | Path = "build", class_name: str | None = None) -> Path:
    out_dir = Path(out_dir)
    smali_dir = out_dir / "smali"
    smali_dir.mkdir(parents=True, exist_ok=True)

    if class_name is None:
        class_name = _class_desc_from_smali(smali_text)

    class_path = _class_desc_to_path(class_name)
    smali_path = smali_dir / class_path
    smali_path = smali_path.with_suffix(".smali")
    smali_path.parent.mkdir(parents=True, exist_ok=True)
    smali_path.write_text(smali_text, encoding="utf-8")

    return out_dir


def emit_build_dir_from_program(frontend_ir, out_dir: str | Path = "build", class_name: str = "LTest;") -> Path:
    result = alpha_pipeline(frontend_ir)
    smali_text = result["smali_class"]
    return emit_build_dir(smali_text, out_dir=out_dir, class_name=class_name)


def run_smali(smali_dir: str | Path, out_dir: str | Path | None = None, smali_jar: str | None = None) -> Path:
    smali_dir = Path(smali_dir)
    if out_dir is None:
        out_dir = smali_dir.parent / "classes.dex"
    out_dir = Path(out_dir)

    if smali_jar:
        cmd = ["java", "-jar", smali_jar, "assemble", str(smali_dir), "-o", str(out_dir)]
    else:
        if shutil.which("smali") is None:
            raise RuntimeError("smali not found on PATH and smali_jar not provided")
        cmd = ["smali", "assemble", str(smali_dir), "-o", str(out_dir)]

    subprocess.run(cmd, check=True)
    return out_dir


def run_baksmali(dex_path: str | Path, out_dir: str | Path, baksmali_jar: str | None = None) -> Path:
    dex_path = Path(dex_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if baksmali_jar:
        cmd = ["java", "-jar", baksmali_jar, "disassemble", str(dex_path), "-o", str(out_dir)]
    else:
        if shutil.which("baksmali") is None:
            raise RuntimeError("baksmali not found on PATH and baksmali_jar not provided")
        cmd = ["baksmali", "disassemble", str(dex_path), "-o", str(out_dir)]

    subprocess.run(cmd, check=True)
    return out_dir
