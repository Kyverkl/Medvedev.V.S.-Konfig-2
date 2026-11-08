"""CLI entry point (stage 3: full graph, DFS, cycles)."""

from __future__ import annotations

import argparse
import sys

from depvis.cargo import CargoError, fetch_direct_deps
from depvis.config import Config, ConfigError, dump_config, load_config
from depvis.graph import build_transitive_graph, find_cycles
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
        return _run(config, args.direct_only)
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
    parser.add_argument(
        "--direct-only",
        action="store_true",
        help="print direct dependencies only",
    )
    return parser.parse_args(argv)


def _run(config: Config, direct_only: bool) -> int:
    """Execute selected operating mode."""
    get_deps = _make_get_deps(config)
    if direct_only:
        return _print_direct(config.package, get_deps)
    graph = build_transitive_graph(config.package, get_deps)
    cycles = find_cycles(graph)
    if cycles:
        print("Cycles detected:")
        for cycle in cycles:
            print("  " + " -> ".join(cycle))
        print()
    print("Dependency graph:")
    for src, deps in sorted(graph.items()):
        joined = ", ".join(deps) if deps else "(none)"
        print(f"  {src} -> {joined}")
    return EXIT_OK


def _print_direct(package: str, get_deps) -> int:
    """Print direct dependencies list."""
    deps = get_deps(package)
    print(f"Direct dependencies of {package}:")
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
