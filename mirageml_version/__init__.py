# Copyright Mirage ML Inc 2023
"""Specifies the `mirageml.__version__` number for the client package."""

from ._version_generated import build_number

# As long as we're on 0.*, all versions are published automatically
major_number = 1

# Bump this manually on any major changes
minor_number = 1

# TODO set the patch number (the 3rd field) to the job run number in GitHub
__version__ = f"{major_number}.{minor_number}.{build_number}"
