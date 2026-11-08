"""Load and validate configuration from TOML."""

from __future__ import annotations

import sys
from dataclasses import asdict, dataclass
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore


@dataclass
class Config:
    """User-configurable parameters."""

    package: str
    repository: str
    test_mode: bool
    ascii_tree: bool


REQUIRED_KEYS = ("package", "repository", "test_mode", "ascii_tree")


class ConfigError(Exception):
    """Configuration read or validation error."""


def load_config(path: str | Path) -> Config:
    """Read a TOML file and return Config."""
    file_path = Path(path)
    if not file_path.is_file():
        raise ConfigError(f"file not found: {file_path}")
    try:
        raw = file_path.read_text(encoding="utf-8")
        data = tomllib.loads(raw)
    except OSError as exc:
        raise ConfigError(f"cannot read: {exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"invalid TOML: {exc}") from exc
    return _parse_data(data)


def _parse_data(data: dict) -> Config:
    """Validate keys and value types."""
    _require_keys(data)
    package = _as_nonempty_str(data, "package")
    repository = _as_nonempty_str(data, "repository")
    test_mode = _as_bool(data, "test_mode")
    ascii_tree = _as_bool(data, "ascii_tree")
    return Config(
        package=package,
        repository=repository,
        test_mode=test_mode,
        ascii_tree=ascii_tree,
    )


def _require_keys(data: dict) -> None:
    """Ensure all required keys are present."""
    for key in REQUIRED_KEYS:
        if key not in data:
            raise ConfigError(f"missing parameter: {key}")


def _as_nonempty_str(data: dict, key: str) -> str:
    """Read a non-empty string field."""
    value = data[key]
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{key}: expected non-empty string")
    return value.strip()


def _as_bool(data: dict, key: str) -> bool:
    """Read a boolean field."""
    value = data[key]
    if not isinstance(value, bool):
        raise ConfigError(f"{key}: expected true/false")
    return value


def dump_config(config: Config) -> str:
    """Key-value dump for debug output."""
    lines = [
        f"{key} = {value!r}"
        for key, value in asdict(config).items()
    ]
    return "\n".join(lines)
