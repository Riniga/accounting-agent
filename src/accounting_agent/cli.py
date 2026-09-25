"""Command line entry point: ``accounting-agent``."""

import argparse
import logging
from collections.abc import Sequence
from pathlib import Path

from accounting_agent import __version__
from accounting_agent.profile import ProfileError, load_profile

logger = logging.getLogger(__name__)

EXIT_OK = 0
EXIT_ERROR = 1


def main(argv: Sequence[str] | None = None) -> int:
    """Parse ``argv`` and run the selected command. Returns the process exit code."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = _build_parser().parse_args(argv)
    return args.handler(args)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="accounting-agent",
        description="Shared bookkeeping core for organisation projects.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    commands = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    run = commands.add_parser("run", help="Run the agent core for one organisation.")
    run.add_argument("organisation", help="Organisation id, e.g. 'hbg-judo'.")
    run.add_argument(
        "--config-dir",
        type=Path,
        required=True,
        help="The organisation's configuration directory (contains organisation.yaml).",
    )
    run.set_defaults(handler=_run)
    return parser


def _run(args: argparse.Namespace) -> int:
    try:
        profile = load_profile(args.config_dir)
    except ProfileError as error:
        logger.error("%s", error)
        return EXIT_ERROR

    if profile.organisation != args.organisation:
        logger.error(
            "Asked to run '%s', but %s belongs to '%s'.",
            args.organisation,
            args.config_dir,
            profile.organisation,
        )
        return EXIT_ERROR

    logger.info("Organisation '%s'", profile.organisation)
    logger.info("enabled features: %s", ", ".join(profile.enabled_features) or "(none)")
    logger.info(
        "disabled features: %s", ", ".join(profile.disabled_features) or "(none)"
    )
    return EXIT_OK
