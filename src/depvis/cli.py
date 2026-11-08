"""CLI entry point (stage 1: config dump)."""

from __future__ import annotations

import argparse
import sys

from depvis.config import ConfigError, dump_config, load_config


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
    print(dump_config(config))
    return EXIT_OK


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
    return parser.parse_args(argv)
