from pathlib import Path

import pytest

from pydedup.scan import find_duplicates


def _write_py(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_duplicates_across_two_files(tmp_path: Path) -> None:
    _write_py(tmp_path / "a.py", "def one():\n    return 1\n\ndef two():\n    return 1\n")
    _write_py(
        tmp_path / "b.py",
        "def other():\n    x = 1\n    y = 1\n    return x + y\n",
    )
    report = find_duplicates(tmp_path, min_lines=2)
    assert report.min_lines == 2
    assert len(report.entries) >= 1
    assert Path(report.entries[0]["path"]).name != ""


def test_no_duplicates_when_unique(tmp_path: Path) -> None:
    _write_py(tmp_path / "a.py", "x = 1\ny = 2\n")
    _write_py(tmp_path / "b.py", "x = 10\ny = 20\n")
    report = find_duplicates(tmp_path, min_lines=2)
    assert report.entries == []


def test_min_lines_edge_case(tmp_path: Path) -> None:
    _write_py(tmp_path / "a.py", "x = 1\ny = 2\nz = 3\nw = 4\n")
    _write_py(tmp_path / "b.py", "x = 1\ny = 2\nz = 3\nw = 4\n")
    report = find_duplicates(tmp_path, min_lines=20)
    assert report.entries == []
    report = find_duplicates(tmp_path, min_lines=4)
    assert any(entry["lines"] >= 4 for entry in report.entries)


def test_json_output(tmp_path: Path) -> None:
    _write_py(tmp_path / "a.py", "x = 1\ny = 2\n")
    _write_py(tmp_path / "b.py", "x = 1\ny = 2\n")
    report = find_duplicates(tmp_path, min_lines=2)
    data = report.as_dict()
    assert data["minLines"] == 2
    assert isinstance(data["duplicateBlocks"], list)
    assert "hash" in data["duplicateBlocks"][0]
