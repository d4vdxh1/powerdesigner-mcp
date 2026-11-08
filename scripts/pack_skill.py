#!/usr/bin/env python3
"""Build and inspect a minimal PowerDesigner agent-skill ZIP (stdlib only)."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "powerdesigner"
EXPECTED = (
    "SKILL.md",
    "LICENSE",
    "references/workflows.md",
    "references/setup.md",
    "references/compatibility.md",
    "examples/example-session.md",
)
DEFAULT_OUTPUT = ROOT / "dist" / "powerdesigner-mcp-skill.zip"
MAX_UNCOMPRESSED = 1_000_000
TOOLS = (
    "consultar_modelo_activo", "listar_coleccion", "leer_propiedades",
    "inspeccionar_diagrama", "editar_propiedad", "crear_objeto",
    "mostrar_en_diagrama", "mover_paquetes", "enderezar_flechas",
    "insertar_codo_flecha", "guardar_modelo",
)
SENSITIVE = (
    re.compile(r"sk-(?:proj-|svcacct-)?[a-zA-Z0-9_-]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def validate() -> list[tuple[str, bytes]]:
    """Fail closed: only explicitly approved text files may be shipped."""
    if not SKILL_DIR.is_dir():
        raise ValueError("Skill folder missing")
    actual = {
        p.relative_to(SKILL_DIR).as_posix()
        for p in SKILL_DIR.rglob("*")
        if p.is_file() or p.is_symlink()
    }
    expected = set(EXPECTED)
    if actual != expected:
        raise ValueError(f"Unexpected/missing files: extra={sorted(actual-expected)}, missing={sorted(expected-actual)}")
    checked: list[tuple[str, bytes]] = []
    total = 0
    for rel in EXPECTED:
        path = SKILL_DIR / rel
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Invalid regular file: {rel}")
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        if "\x00" in text:
            raise ValueError(f"Binary/NUL content: {rel}")
        for pattern in SENSITIVE:
            if pattern.search(text):
                raise ValueError(f"Possible credential in {rel}")
        for dest in LINK.findall(text):
            if dest.startswith(("#", "https://", "http://", "mailto:")):
                continue
            target = dest.split("#", 1)[0]
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.is_relative_to(SKILL_DIR.resolve()) or not resolved.is_file():
                raise ValueError(f"Broken or escaping relative link: {rel} -> {dest}")
        checked.append((rel, raw))
        total += len(raw)
    if total > MAX_UNCOMPRESSED:
        raise ValueError("Skill larger than conservative 1MB budget")
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", content, re.S)
    if not match:
        raise ValueError("SKILL.md YAML frontmatter missing")
    yaml = match.group(1)
    for key in ("name", "description"):
        hit = re.search(rf"(?m)^{key}:\s*(.+)\s*$", yaml)
        if not hit or not hit.group(1).strip():
            raise ValueError(f"Missing {key} frontmatter")
    if not re.search(r"(?m)^name:\s*powerdesigner-mcp\s*$", yaml):
        raise ValueError("Incorrect skill name")
    missing = [name for name in TOOLS if name not in content]
    if missing:
        raise ValueError(f"SKILL.md missing server tool names: {missing}")
    return checked


def build(output: Path) -> None:
    contents = validate()
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for rel, data in contents:
            meta = ZipInfo(rel, date_time=(2026, 11, 8, 0, 0, 0))
            meta.compress_type = ZIP_DEFLATED
            meta.external_attr = 0o644 << 16
            archive.writestr(meta, data, compress_type=ZIP_DEFLATED, compresslevel=9)
    with ZipFile(output) as archive:
        if archive.namelist() != list(EXPECTED) or archive.testzip() is not None:
            raise ValueError("ZIP verification failed")
    print(f"Valid skill ZIP: {output} ({output.stat().st_size} bytes, {len(contents)} files)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Only verify skill source files")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        if args.check:
            print(f"Skill validated: {len(validate())} permitted text files")
        else:
            build(args.output)
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"Skill packaging FAILED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
