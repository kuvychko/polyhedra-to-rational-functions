"""Shared test configuration."""

import os
import sys

import pytest


def pytest_collection_modifyitems(config, items):
    """Skip screenshot tests on Windows CI runners.

    GitHub's Windows runners have no GPU, and VTK's off-screen OpenGL crashes there with an
    access violation inside ``Plotter.screenshot``, which kills the whole test process. The
    tests still run locally and on the Linux runners (virtual display).
    """
    if sys.platform == "win32" and os.environ.get("CI"):
        skip = pytest.mark.skip(reason="no OpenGL on Windows CI runners")
        for item in items:
            if "render" in item.keywords:
                item.add_marker(skip)
