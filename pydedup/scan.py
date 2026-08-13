from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator

DEFAULT_EXCLUDES = {".git", "__pycache__", ".venv", "dist", "build", "node_modules"}


@dataclass(frozen=True)
class Duplicate:
    hash: str
    path: str
    start: int
    end: int
    text: str
    lines: int = 0


@dataclass
class Report:
    min_lines: int = 6
    entries: list[dict] = field(default_factory=list)

    def add(self, duplicates: list[Duplicate]) -> None:
        same_groups: dict[str, list[Duplicate]] = {}
        for d in duplicates:
            same_groups.setdefault(d.hash, []).append(d)
        for block_same in same_groups.values():
            if len(block_same) < 2:
                continue
            for d in block_same:
                self.entries.append(
                    {
                        "hash": d.hash,
                        "path": d.path,
                        "start": d.start,
                        "end": d.end,
                        "lines": d.lines,
                    }
                )

    def as_dict(self) -> dict:
        return {"minLines": self.min_lines, "duplicateBlocks": self.entries}


def _normalize(text: str) -> str:
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def _hash(text: str) -> str:
    return hashlib.sha1(_normalize(text).encode("utf-8")).hexdigest()


def _iter_py_files(root: Path) -> Iterator[Path]:
    for path in sorted(root.rglob("*.py")):
        if any(part in DEFAULT_EXCLUDES for part in path.parts):
            continue
        yield path


def _blocks(path: Path, min_lines: int) -> Iterator[Duplicate]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    max_start = max(1, len(lines) - min_lines + 1)
    for i in range(max_start):
        j = i + min_lines
        while j <= len(lines):
            block_text = "\n".join(lines[i:j])
            hashed = _hash(block_text)
            yield Duplicate(
                hash=hashed,
                path=str(path),
                start=i + 1,
                end=j,
                text=block_text,
                lines=j - i,
            )
            j += 1


def find_duplicates(
    root: Path, min_lines: int = 6
) -> Report:
    report = Report(min_lines=min_lines)
    seen: set[str] = set()
    all_duplicates: list[Duplicate] = []
    for path in _iter_py_files(root):
        for dup in _blocks(path, min_lines):
            key = (dup.hash, dup.path, dup.start, dup.end)
            if key in seen:
                continue
            seen.add(key)
            all_duplicates.append(dup)
    report.add(all_duplicates)
    return report
