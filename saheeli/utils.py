"""Shared helper utilities for Saheeli."""

import uuid


def generate_id() -> str:
    """Return a random hex identifier."""
    return uuid.uuid4().hex
