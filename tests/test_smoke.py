"""The environment is the one the run records assume."""

from importlib.metadata import version

import polyhedral_functions


def test_package_imports():
    assert polyhedral_functions.__version__


def test_complexplorer_is_pinned_revision():
    # Baseline results and run records are only comparable on this exact revision.
    assert version("complexplorer") == "3.1.0"
