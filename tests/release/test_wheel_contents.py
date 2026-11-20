"""Verify an API Utils wheel with API_UTILS_WHEEL set to its path."""

from email.parser import BytesParser
import os
from pathlib import Path
import tomllib
from zipfile import ZipFile

import pytest


def test_api_utils_wheel_contents():
    wheel_path = os.environ.get("API_UTILS_WHEEL")
    if not wheel_path:
        pytest.skip("Set API_UTILS_WHEEL to a built or downloaded wheel")

    project_file = Path(__file__).resolve().parents[2] / "pyproject.toml"
    project = tomllib.loads(project_file.read_text(encoding="utf-8"))["project"]
    with ZipFile(wheel_path) as wheel:
        contents = set(wheel.namelist())
        assert {
            "api_utils/__init__.py",
            "api_utils/config/config.py",
            "api_utils/flask_utils/token.py",
            "api_utils/mongo_utils/mongo_io.py",
            "api_utils/services/__init__.py",
        } <= contents
        (metadata_path,) = (
            name for name in contents if name.endswith(".dist-info/METADATA")
        )
        metadata = BytesParser().parsebytes(wheel.read(metadata_path))

    assert metadata["Name"].replace("_", "-") == "api-utils"
    assert metadata["Version"] == project["version"]
    assert any(
        dependency.lower().startswith("pyjwt")
        for dependency in metadata.get_all("Requires-Dist", [])
    )
