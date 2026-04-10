"""Result caching for numbered references and name resolution."""

from __future__ import annotations

import contextlib
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any


def atomic_write(path: Path, data: str) -> None:
    """Write data to path atomically via temp file + rename.

    Uses mkstemp in the same directory so os.rename() is atomic on POSIX.
    On failure, the temp file is cleaned up and the original is untouched.
    """
    fd = -1
    tmp = ""
    try:
        fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        os.write(fd, data.encode())
        os.close(fd)
        fd = -1
        os.rename(tmp, path)
    except BaseException:
        if fd >= 0:
            os.close(fd)
        if tmp:
            with contextlib.suppress(OSError):
                os.unlink(tmp)
        raise


def get_cache_dir() -> Path:
    """Resolve cache directory, respecting XDG_CACHE_HOME."""
    xdg = os.environ.get("XDG_CACHE_HOME", "")
    base = Path(xdg) if xdg else Path.home() / ".cache"
    return base / "td"


# --- Result cache (numbered references) ---


def save_result_cache(task_ids: list[str]) -> None:
    """Save task ID mapping from last list command."""
    cache_dir = get_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "ids": {str(i + 1): tid for i, tid in enumerate(task_ids)},
        "timestamp": time.time(),
    }
    atomic_write(cache_dir / "last_results.json", json.dumps(data))


def _default_result_ttl() -> int:
    """Get result cache TTL from config, defaulting to 600s."""
    from td.core.config import load_config

    return load_config().cache_ttl_results


def _default_name_ttl() -> int:
    """Get name cache TTL from config, defaulting to 300s."""
    from td.core.config import load_config

    return load_config().cache_ttl_names


def load_result_cache(max_age: int | None = None) -> dict[str, str]:
    """Load cached row-number-to-task-ID mapping.

    Returns empty dict if cache is missing or stale. TTL defaults to
    cache_ttl_results from config (10 min default).
    """
    if max_age is None:
        max_age = _default_result_ttl()
    path = get_cache_dir() / "last_results.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        if time.time() - data.get("timestamp", 0) > max_age:
            return {}
        ids: dict[str, str] = data.get("ids", {})
        return ids
    except (json.JSONDecodeError, KeyError, OSError):
        return {}


def resolve_task_ref(ref: str) -> str:
    """Resolve a task reference: row number → task ID, or pass through.

    Tries cached row number first, then returns ref as-is (assumed task ID).
    """
    if ref.isdigit():
        cache = load_result_cache()
        if ref in cache:
            return cache[ref]
    return ref


# --- Name cache (project/label/section resolution) ---


def save_name_cache(
    projects: list[dict[str, Any]] | None = None,
    labels: list[dict[str, Any]] | None = None,
    sections: list[dict[str, Any]] | None = None,
) -> None:
    """Cache project/label/section name mappings."""
    cache_dir = get_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / "names.json"

    # Merge with existing cache
    existing: dict[str, Any] = {}
    if path.exists():
        import contextlib

        with contextlib.suppress(json.JSONDecodeError):
            existing = json.loads(path.read_text())

    if projects is not None:
        existing["projects"] = projects
    if labels is not None:
        existing["labels"] = labels
    if sections is not None:
        existing["sections"] = sections
    existing["timestamp"] = time.time()

    atomic_write(path, json.dumps(existing))


def load_name_cache(max_age: int | None = None) -> dict[str, Any]:
    """Load cached name mappings. Returns empty dict if stale.

    TTL defaults to cache_ttl_names from config (5 min default).
    """
    if max_age is None:
        max_age = _default_name_ttl()
    path = get_cache_dir() / "names.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        if time.time() - data.get("timestamp", 0) > max_age:
            return {}
        result: dict[str, Any] = data
        return result
    except (json.JSONDecodeError, KeyError, OSError):
        return {}
