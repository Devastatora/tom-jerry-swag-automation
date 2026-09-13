from pathlib import Path

import pytest

from retrogram.db import QueueDB
from retrogram.worker import parse_time


def test_queue_is_fifo_and_idempotent(tmp_path: Path):
    db = QueueDB(tmp_path / "queue.db")
    assert db.enqueue("one.png", "one") is True
    assert db.enqueue("one.png", "duplicate") is False
    assert db.enqueue("two.png", "two") is True
    assert db.next().image_path == "one.png"


def test_mark_published_moves_to_next(tmp_path: Path):
    db = QueueDB(tmp_path / "queue.db")
    db.enqueue("one.png", "one")
    db.enqueue("two.png", "two")
    first = db.next()
    db.mark_published(first.id, "ig-123")
    assert db.next().image_path == "two.png"
    assert db.counts() == {"queued": 1, "failed": 0, "published": 1}


@pytest.mark.parametrize("value, expected", [("10:00", (10, 0)), ("23:59", (23, 59))])
def test_parse_time(value, expected):
    assert parse_time(value) == expected


@pytest.mark.parametrize("value", ["24:00", "12:60", "bad"])
def test_invalid_time(value):
    with pytest.raises((ValueError, AttributeError)):
        parse_time(value)

