"""Compatibility entry point for the unified TKO command line."""

from tko.__main__ import app, main
from tko.cli.cli_task import app as task_app
from tko.cli.cli_tests import app as tests_app

__all__ = ["app", "main", "task_app", "tests_app"]


if __name__ == "__main__":
    main()
