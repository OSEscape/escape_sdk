"""
Escape - OSRS Bot Development SDK

A Python SDK for Old School RuneScape bot development with an intuitive
structure that mirrors the game's interface.
"""

__version__ = "1.0.0"
__author__ = "Escape Team"

# Ensure generated files path is available for imports
from escape._internal.cache_manager import ensureGeneratedInPath

ensureGeneratedInPath()

from escape.client import Client  # noqa: E402

__all__ = ["Client"]
