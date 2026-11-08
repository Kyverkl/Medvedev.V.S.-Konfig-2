"""CLI entry point."""

from __future__ import annotations

import argparse
import sys

from depvis.cargo import CargoError, fetch_direct_deps
from depvis.config import Config, ConfigError, dump_config, load_config
from depvis.graph import (
    build_transitive_graph,
    find_cycles,
    reverse_dependencies,
)
from depvis.test_repo import RepoFormatError, load_test_repo
from depvis.viz import to_ascii_tree, to_mermaid


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
        return _run(config, args.direct_only, args.reverse)
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
    parser.add_argument(
        "--reverse",
        action="store_true",
        help="print reverse dependencies",
    )
    return parser.parse_args(argv)


def _run(config: Config, direct_only: bool, reverse: bool) -> int:
    """Execute selected operating mode."""
    get_deps, roots = _make_source(config)
    if direct_only:
        return _print_direct(config.package, get_deps)
    graph = _build_full_graph(config.package, get_deps, roots, reverse)
    if reverse:
        return _print_reverse(graph, config.package)
    return _print_graph(graph, config)


def _print_direct(package: str, get_deps) -> int:
    """Print direct dependencies list."""
    deps = get_deps(package)
    print(f"Direct dependencies of {package}:")
    if not deps:
        print("  (none)")
    for name in deps:
        print(f"  - {name}")
    return EXIT_OK


def _print_reverse(graph: dict, package: str) -> int:
    """Print packages that depend on package."""
    parents = reverse_dependencies(graph, package)
    print(f"Reverse dependencies of {package}:")
    if not parents:
        print("  (none)")
    for name in parents:
        print(f"  - {name}")
    return EXIT_OK


def _print_graph(graph: dict, config: Config) -> int:
    """Print cycles, Mermaid and optional ASCII tree."""
    cycles = find_cycles(graph)
    if cycles:
        print("Cycles detected:")
        for cycle in cycles:
            print("  " + " -> ".join(cycle))
        print()
    print(to_mermaid(graph, config.package))
    print()
    if config.ascii_tree:
        print("ASCII tree:")
        print(to_ascii_tree(graph, config.package))
    return EXIT_OK


def _build_full_graph(package, get_deps, roots, reverse: bool):
    """
    Build transitive graph from package.

    For reverse mode with a known full root set, merge
    subgraphs so reverse edges outside the package subtree
    are visible.
    """
    if reverse and roots:
        merged: dict = {}
        for root in roots:
            part = build_transitive_graph(root, get_deps)
            for key, deps in part.items():
                merged.setdefault(key, deps)
        return merged
    return build_transitive_graph(package, get_deps)


def _make_source(config: Config):
    """Return (get_deps, all_roots_or_empty)."""
    if config.test_mode:
        repo = load_test_repo(config.repository)
        if config.package not in repo:
            raise RepoFormatError(
                f"package {config.package!r} not in test repo"
            )

        def from_test(name: str) -> list[str]:
            return list(repo.get(name, []))

        return from_test, list(repo.keys())

    def from_cargo(name: str) -> list[str]:
        return fetch_direct_deps(name, config.repository)

    return from_cargo, []
