"""Tests for test repository parser."""

from pathlib import Path

import pytest

from depvis.test_repo import RepoFormatError, load_test_repo


def test_load_fixture() -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / "fixtures" / "graph_simple.txt"
    graph = load_test_repo(path)
    assert graph["A"] == ["B", "C"]
    assert graph["D"] == []


def test_bad_name(tmp_path: Path) -> None:
    path = tmp_path / "g.txt"
    path.write_text("a: B\n", encoding="utf-8")
    with pytest.raises(RepoFormatError):
        load_test_repo(path)
