from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class Post:
    id: int
    image_path: str
    caption: str
    status: str
    attempts: int


class QueueDB:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.init()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def init(self) -> None:
        with self.connect() as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_path TEXT NOT NULL UNIQUE,
                    caption TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'queued',
                    attempts INTEGER NOT NULL DEFAULT 0,
                    remote_media_id TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    published_at TEXT
                )
                """
            )

    def enqueue(self, image_path: str, caption: str) -> bool:
        with self.connect() as db:
            cursor = db.execute(
                """INSERT OR IGNORE INTO posts(image_path, caption, created_at)
                   VALUES (?, ?, ?)""",
                (image_path, caption, datetime.now(timezone.utc).isoformat()),
            )
            return cursor.rowcount == 1

    def next(self) -> Post | None:
        with self.connect() as db:
            row = db.execute(
                """SELECT id, image_path, caption, status, attempts
                   FROM posts WHERE status IN ('queued', 'failed') AND attempts < 3
                   ORDER BY id LIMIT 1"""
            ).fetchone()
        return Post(**dict(row)) if row else None

    def mark_published(self, post_id: int, remote_media_id: str) -> None:
        with self.connect() as db:
            db.execute(
                """UPDATE posts SET status='published', remote_media_id=?,
                   published_at=?, error=NULL WHERE id=?""",
                (remote_media_id, datetime.now(timezone.utc).isoformat(), post_id),
            )

    def mark_failed(self, post_id: int, error: str) -> None:
        with self.connect() as db:
            db.execute(
                """UPDATE posts SET status='failed', attempts=attempts+1,
                   error=? WHERE id=?""",
                (error[:1000], post_id),
            )

    def counts(self) -> dict[str, int]:
        with self.connect() as db:
            rows = db.execute("SELECT status, COUNT(*) count FROM posts GROUP BY status").fetchall()
        result = {"queued": 0, "failed": 0, "published": 0}
        result.update({row["status"]: row["count"] for row in rows})
        return result

