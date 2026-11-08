"""CLI entry point (stage 2: direct dependencies)."""

from __future__ import annotations

import argparse
import sys

from depvis.cargo import CargoError, fetch_direct_deps
from depvis.config import Config, ConfigError, dump_config, load_config
from depvis.test_repo import RepoFormatError, load_test_repo


EXIT_OK = 0
EXIT_ERROR = 1


def main(argv: list[str] | None = None) -> int:
    """CLI main. Returns process exit code."""
    args = _parse_args(argv)
    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"config error: {exc}", file=sys.stderr)
        return EXIT_ERROR
    if args.dump_config:
        print(dump_config(config))
        return EXIT_OK
    try:
        return _run_direct(config)
    except (RepoFormatError, CargoError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERROR


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    """Build and parse CLI arguments."""
    parser = argparse.ArgumentParser(
        prog="depvis",
        description="Dependency graph visualizer (Cargo)",
    )
    parser.add_argument(
        "-c",
        "--config",
        required=True,
        help="path to TOML config file",
    )
    parser.add_argument(
        "--dump-config",
        action="store_true",
        help="print parameters and exit",
    )
    return parser.parse_args(argv)


def _run_direct(config: Config) -> int:
    """Print direct dependencies of the configured package."""
    get_deps = _make_get_deps(config)
    deps = get_deps(config.package)
    print(f"Direct dependencies of {config.package}:")
    if not deps:
        print("  (none)")
    for name in deps:
        print(f"  - {name}")
    return EXIT_OK


def _make_get_deps(config: Config):
    """Return function that lists direct dependencies."""
    if config.test_mode:
        repo = load_test_repo(config.repository)
        if config.package not in repo:
            raise RepoFormatError(
                f"package {config.package!r} not in test repo"
            )

        def from_test(name: str) -> list[str]:
            return list(repo.get(name, []))

        return from_test

    def from_cargo(name: str) -> list[str]:
        return fetch_direct_deps(name, config.repository)

    return from_cargo
