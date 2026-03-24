"""Smoke test — package is importable and version is set."""

from __future__ import annotations


def test_version_is_set() -> None:
    from td import __version__

    assert __version__
    assert isinstance(__version__, str)
