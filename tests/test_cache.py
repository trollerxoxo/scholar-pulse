import json
import time
from datetime import date, timedelta
from pathlib import Path

import pytest

from pulse.service import _cache_key, _load_cache, _save_cache, _cleanup_stale_cache
from helpers import make_paper, make_query


# --- Cache key tests ---

def test_cache_key_is_stable():
    """Same query always produces the same key."""
    q = make_query(days=30)
    assert _cache_key(q, 30) == _cache_key(q, 30)


def test_cache_key_differs_by_days():
    """Different day ranges produce different cache keys."""
    q30 = make_query(days=30)
    q365 = make_query(days=365)
    assert _cache_key(q30, 30) != _cache_key(q365, 365)


def test_cache_key_differs_by_keywords():
    """Different keywords produce different cache keys."""
    q1 = make_query(keywords=["BIM"], days=30)
    q2 = make_query(keywords=["digital twin"], days=30)
    assert _cache_key(q1, 30) != _cache_key(q2, 30)


# --- Save / Load round-trip ---

def test_save_and_load_cache(tmp_path):
    """Papers saved to cache can be loaded back."""
    cache_file = tmp_path / "test_cache.json"
    papers = [make_paper("p1"), make_paper("p2")]

    _save_cache(cache_file, papers)
    loaded = _load_cache(cache_file)

    assert loaded is not None
    assert len(loaded) == 2
    assert loaded[0].id == "p1"
    assert loaded[1].id == "p2"


def test_load_cache_miss_on_no_file(tmp_path):
    """Returns None when cache file does not exist."""
    cache_file = tmp_path / "nonexistent.json"
    assert _load_cache(cache_file) is None


def test_load_cache_returns_none_on_corrupt_file(tmp_path):
    """Returns None (not a crash) when cache file is corrupt JSON."""
    cache_file = tmp_path / "corrupt.json"
    cache_file.write_text("not valid json {{{{")
    assert _load_cache(cache_file) is None


# --- Stale TTL ---

def test_load_cache_stale_after_cleanup(tmp_path):
    """After _cleanup_stale_cache removes old files, _load_cache returns None."""
    cache_file = tmp_path / "old.json"
    _save_cache(cache_file, [make_paper()])

    # Make it look an hour and a bit old
    old_mtime = time.time() - 3700
    import os
    os.utime(cache_file, (old_mtime, old_mtime))

    _cleanup_stale_cache(tmp_path)

    # File should be gone now
    assert not cache_file.exists()
    assert _load_cache(cache_file) is None


def test_cleanup_preserves_fresh_files(tmp_path):
    """Fresh cache files (under TTL) are NOT deleted during cleanup."""
    fresh_file = tmp_path / "fresh.json"
    _save_cache(fresh_file, [make_paper()])

    _cleanup_stale_cache(tmp_path)

    assert fresh_file.exists()


def test_cleanup_on_missing_dir():
    """Cleanup on a non-existent directory doesn't crash."""
    _cleanup_stale_cache(Path("/nonexistent/path/to/cache"))  # should not raise
