#!/usr/bin/env python3
"""skills/skillctl.py — минимальный менеджер skill-packs (git → copy)."""
from __future__ import annotations

import argparse
import shutil
import subprocess
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import List, Optional

try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover
    raise SystemExit(
        "PyYAML не найден. Установите: pip install pyyaml\n"
        f"Оригинальная ошибка импорта: {e}"
    )


@dataclass(frozen=True)
class SkillSource:
    repo: str
    ref: str
    path: str


@dataclass(frozen=True)
class SkillInstall:
    mode: str
    target: str


@dataclass(frozen=True)
class SkillSpec:
    id: str
    source: SkillSource
    install: SkillInstall


def _run(cmd: List[str], cwd: Optional[Path] = None) -> None:
    p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=False, text=True)
    if p.returncode != 0:
        raise SystemExit(f"[ERR] command failed ({p.returncode}): {' '.join(cmd)}")


def _repo_cache_dir(cache_root: Path, repo: str, ref: str) -> Path:
    key = sha256(f"{repo}::{ref}".encode("utf-8")).hexdigest()[:16]
    return cache_root / key


def _ensure_repo_checked_out(cache_dir: Path, repo: str, ref: str) -> Path:
    if not cache_dir.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        _run(["git", "clone", "--no-tags", "--depth", "1", repo, "."], cwd=cache_dir)
    _run(["git", "fetch", "--depth", "1", "origin", ref], cwd=cache_dir)
    _run(["git", "checkout", "--force", "FETCH_HEAD"], cwd=cache_dir)
    return cache_dir


def _load_lock(lock_path: Path) -> List[SkillSpec]:
    data = yaml.safe_load(lock_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "skills" not in data:
        raise SystemExit("[ERR] skills.lock.yaml должен содержать верхний ключ `skills`")
    skills_raw = data["skills"]
    if not isinstance(skills_raw, list):
        raise SystemExit("[ERR] `skills` должен быть списком")

    specs: List[SkillSpec] = []
    for item in skills_raw:
        if not isinstance(item, dict):
            raise SystemExit("[ERR] элемент `skills` должен быть объектом")
        sid = str(item.get("id", "")).strip()
        if not sid:
            raise SystemExit("[ERR] у skill отсутствует `id`")

        src = item.get("source", {})
        inst = item.get("install", {})
        try:
            source = SkillSource(
                repo=str(src["repo"]),
                ref=str(src.get("ref", "main")),
                path=str(src["path"]),
            )
            install = SkillInstall(
                mode=str(inst.get("mode", "copy")),
                target=str(inst.get("target", f"tools/skills/{sid}")),
            )
        except KeyError as e:
            raise SystemExit(f"[ERR] отсутствует обязательное поле в lock: {e}")

        specs.append(SkillSpec(id=sid, source=source, install=install))
    return specs


def _install_copy(project: Path, src_dir: Path, target_rel: str) -> None:
    target = (project / target_rel).resolve()
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src_dir, target)
    print(f"[OK] installed -> {target_rel}")


def apply(project: Path, lock_path: Path) -> None:
    project = project.resolve()
    lock_path = (project / lock_path).resolve() if not lock_path.is_absolute() else lock_path.resolve()
    if not lock_path.exists():
        raise SystemExit(f"[ERR] lock not found: {lock_path}")

    cache_root = project / ".skills_cache"
    cache_root.mkdir(parents=True, exist_ok=True)

    specs = _load_lock(lock_path)
    print(f"[INFO] skills: {len(specs)}")

    for spec in specs:
        cache_dir = _repo_cache_dir(cache_root, spec.source.repo, spec.source.ref)
        _ensure_repo_checked_out(cache_dir, spec.source.repo, spec.source.ref)

        pack_dir = (cache_dir / spec.source.path).resolve()
        if not pack_dir.exists():
            raise SystemExit(f"[ERR] pack not found: {pack_dir}")

        if spec.install.mode != "copy":
            raise SystemExit(f"[ERR] unsupported install mode: {spec.install.mode}")

        _install_copy(project, pack_dir, spec.install.target)

    print("[DONE] apply finished")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_apply = sub.add_parser("apply", help="Install skills into a project")
    ap_apply.add_argument("--project", type=str, default=".", help="Path to target project")
    ap_apply.add_argument("--lock", type=str, default="skills.lock.yaml", help="Path to lock file (relative to project)")

    args = ap.parse_args()
    if args.cmd == "apply":
        apply(Path(args.project), Path(args.lock))


if __name__ == "__main__":
    main()
