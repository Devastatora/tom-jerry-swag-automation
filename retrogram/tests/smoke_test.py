"""Dependency-free checks for environments where pytest is unavailable."""

import json
import tempfile
from pathlib import Path

from retrogram.db import QueueDB


def main() -> None:
    with tempfile.TemporaryDirectory() as temp:
        db = QueueDB(Path(temp) / "queue.db")
        assert db.enqueue("one.jpg", "first")
        assert not db.enqueue("one.jpg", "duplicate")
        assert db.enqueue("two.jpg", "second")
        first = db.next()
        assert first and first.image_path == "one.jpg"
        db.mark_published(first.id, "ig-test")
        assert db.next().image_path == "two.jpg"

    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "assets/queue/manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["posts"]) == 6
    for post in manifest["posts"]:
        image = root / "assets/queue" / post["file"]
        assert image.exists() and image.stat().st_size > 100_000
        assert post["caption"].strip()
    print("Smoke checks passed: queue, manifest and 6 starter images")


if __name__ == "__main__":
    main()
