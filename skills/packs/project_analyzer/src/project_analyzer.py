#!/usr/bin/env python3
"""project_analyzer.py — MVP сканера проекта (Python AST + индекс файлов)."""
from __future__ import annotations

import argparse
import ast
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_EXCLUDES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
    ".skills_cache",
    ".idea",
}


@dataclass(frozen=True)
class Symbol:
    kind: str
    name: str
    file: str
    lineno: int
    end_lineno: int


@dataclass(frozen=True)
class ImportRec:
    module: str
    name: Optional[str]
    file: str
    lineno: int


def iter_files(root: Path, excludes: Iterable[str]) -> Iterable[Path]:
    ex = set(excludes)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ex]
        for fn in filenames:
            yield Path(dirpath) / fn


def parse_python(path: Path) -> Tuple[List[Symbol], List[ImportRec]]:
    try:
        src = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        src = path.read_text(encoding="latin-1")

    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError:
        return [], []

    symbols: List[Symbol] = []
    imports: List[ImportRec] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append(Symbol(
                kind="function",
                name=node.name,
                file=str(path),
                lineno=int(getattr(node, "lineno", 0) or 0),
                end_lineno=int(getattr(node, "end_lineno", 0) or (getattr(node, "lineno", 0) or 0)),
            ))
        elif isinstance(node, ast.ClassDef):
            symbols.append(Symbol(
                kind="class",
                name=node.name,
                file=str(path),
                lineno=int(getattr(node, "lineno", 0) or 0),
                end_lineno=int(getattr(node, "end_lineno", 0) or (getattr(node, "lineno", 0) or 0)),
            ))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(ImportRec(
                    module=alias.name,
                    name=None,
                    file=str(path),
                    lineno=int(getattr(node, "lineno", 0) or 0),
                ))
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for alias in node.names:
                imports.append(ImportRec(
                    module=mod,
                    name=alias.name,
                    file=str(path),
                    lineno=int(getattr(node, "lineno", 0) or 0),
                ))

    symbols.sort(key=lambda s: (s.file, s.kind, s.name, s.lineno))
    imports.sort(key=lambda i: (i.file, i.module, i.name or "", i.lineno))
    return symbols, imports


def build_index(root: Path, excludes: Iterable[str]) -> Dict[str, Any]:
    root = root.resolve()
    files: List[Dict[str, Any]] = []
    symbols: List[Symbol] = []
    imports: List[ImportRec] = []

    for p in iter_files(root, excludes):
        if p.is_dir():
            continue
        rel = str(p.resolve().relative_to(root))
        files.append({"path": rel, "suffix": p.suffix.lower(), "size": p.stat().st_size})

        if p.suffix.lower() == ".py":
            s, im = parse_python(p)
            for x in s:
                symbols.append(Symbol(x.kind, x.name, rel, x.lineno, x.end_lineno))
            for x in im:
                imports.append(ImportRec(x.module, x.name, rel, x.lineno))

    files.sort(key=lambda r: r["path"])
    symbols_sorted = sorted(symbols, key=lambda s: (s.file, s.kind, s.name, s.lineno))
    imports_sorted = sorted(imports, key=lambda i: (i.file, i.module, i.name or "", i.lineno))

    return {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "root": str(root),
            "excludes": sorted(set(excludes)),
            "version": "0.1.0",
        },
        "files": files,
        "symbols": [
            {"kind": s.kind, "name": s.name, "file": s.file, "lineno": s.lineno, "end_lineno": s.end_lineno}
            for s in symbols_sorted
        ],
        "imports": [
            {"module": i.module, "name": i.name, "file": i.file, "lineno": i.lineno}
            for i in imports_sorted
        ],
        "stats": {
            "files_total": len(files),
            "py_files": sum(1 for f in files if f["suffix"] == ".py"),
            "symbols_total": len(symbols_sorted),
            "imports_total": len(imports_sorted),
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=str, default=".", help="Project root to scan")
    ap.add_argument("--out", type=str, default="plan/project_architecture.json", help="Output JSON path")
    ap.add_argument("--exclude", action="append", default=[], help="Extra exclude dir name (repeatable)")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out_path = Path(args.out)
    excludes = sorted(DEFAULT_EXCLUDES.union(set(args.exclude)))

    data = build_index(root, excludes)
    out_full = (root / out_path) if not out_path.is_absolute() else out_path
    out_full.parent.mkdir(parents=True, exist_ok=True)
    out_full.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] wrote {out_full}")


if __name__ == "__main__":
    main()
