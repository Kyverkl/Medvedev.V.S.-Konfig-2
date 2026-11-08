"""depvis package."""


def main(argv=None):
    """CLI entry point."""
    from depvis.cli import main as cli_main
    return cli_main(argv)
