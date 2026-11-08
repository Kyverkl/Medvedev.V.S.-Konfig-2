"""Tests for configuration loading."""

from pathlib import Path

import pytest

from depvis.config import ConfigError, dump_config, load_config


def test_load_ok(tmp_path: Path) -> None:
    path = tmp_path / "c.toml"
    path.write_text(
        'package = "A"\n'
        'repository = "fixtures/x.txt"\n'
        "test_mode = true\n"
        "ascii_tree = false\n",
        encoding="utf-8",
    )
    cfg = load_config(path)
    assert cfg.package == "A"
    assert cfg.test_mode is True
    assert cfg.ascii_tree is False


def test_missing_file() -> None:
    with pytest.raises(ConfigError):
        load_config("no_such_file.toml")


def test_missing_key(tmp_path: Path) -> None:
    path = tmp_path / "bad.toml"
    path.write_text('package = "A"\n', encoding="utf-8")
    with pytest.raises(ConfigError, match="missing"):
        load_config(path)


def test_dump_config(tmp_path: Path) -> None:
    path = tmp_path / "c.toml"
    path.write_text(
        'package = "A"\n'
        'repository = "r"\n'
        "test_mode = true\n"
        "ascii_tree = true\n",
        encoding="utf-8",
    )
    text = dump_config(load_config(path))
    assert "package" in text
    assert "A" in text
