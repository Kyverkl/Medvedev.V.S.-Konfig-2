"""Reading test repository graph from a text file."""

from __future__ import annotations

from pathlib import Path


class RepoFormatError(Exception):
    """Error while parsing a test repository file."""


def load_test_repo(path: str | Path) -> dict[str, list[str]]:
    """
    Load graph from a text file.

    Line format: NAME: DEP1 DEP2 ...
    Package names are uppercase Latin letters and digits.
    """
    file_path = Path(path)
    if not file_path.is_file():
        raise RepoFormatError(f"file not found: {file_path}")
    graph: dict[str, list[str]] = {}
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise RepoFormatError(f"read error: {exc}") from exc
    for number, raw in enumerate(lines, 1):
        line = _strip_comment(raw)
        if not line:
            continue
        name, deps = _parse_line(line, number)
        graph[name] = deps
    if not graph:
        raise RepoFormatError("file contains no packages")
    return graph


def _strip_comment(raw: str) -> str:
    """Strip inline comment starting with hash character."""
    marker = chr(35)
    return raw.split(marker, 1)[0].strip()


def _parse_line(line: str, number: int) -> tuple[str, list[str]]:
    """Parse one line NAME: deps."""
    if ":" not in line:
        raise RepoFormatError(
            f"line {number}: expected NAME: deps"
        )
    left, right = line.split(":", 1)
    name = left.strip()
    if not name:
        raise RepoFormatError(
            f"line {number}: empty package name"
        )
    if not _is_package_name(name):
        raise RepoFormatError(
            f"line {number}: invalid name {name!r}"
        )
    deps = right.split()
    for dep in deps:
        if not _is_package_name(dep):
            raise RepoFormatError(
                f"line {number}: invalid dependency {dep!r}"
            )
    return name, deps


def _is_package_name(name: str) -> bool:
    """Name of uppercase Latin letters and digits."""
    return bool(name) and name.isalnum() and name.isupper()
