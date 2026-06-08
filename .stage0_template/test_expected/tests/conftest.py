"""
Pytest configuration for api_utils tests.

This file is automatically loaded by pytest before running tests.
It sets up necessary environment variables for testing.
"""
import os
import sys
from pathlib import Path

_config_py = Path(__file__).resolve().parent.parent / "api_utils" / "config" / "config.py"
if _config_py.is_file() and "{%" in _config_py.read_text(encoding="utf-8"):
    print(
        "This repository is a Stage0 template: merge product specifications before running tests.",
        file=sys.stderr,
    )
    print(
        "An unmerged clone is not a runnable Python project.",
        file=sys.stderr,
    )
    raise SystemExit(2)

# Set JWT_SECRET at module import time (before any tests run)
# This prevents ValueError when Config is initialized during test setup
# Individual tests can override this by setting JWT_SECRET before calling Config.get_instance()
if 'JWT_SECRET' not in os.environ:
    os.environ['JWT_SECRET'] = 'test-secret-for-testing'
