from __future__ import annotations

import json
import logging
from pathlib import Path

from .config import Settings
from .db import QueueDB
from .instagram import InstagramPublisher

log = logging.getLogger(__name__)


def seed_queue(db: QueueDB, queue_dir: Path) -> int:
    manifest_path = queue_dir / "manifest.json"
    if not manifest_path.exists():
        return 0
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    added = 0
    for item in manifest["posts"]:
        image = queue_dir / item["file"]
        if not image.exists():
            log.warning("Missing image from manifest: %s", image)
            continue
        added += db.enqueue(str(image), item["caption"])
    return added


def run_once(settings: Settings) -> str:
    db = QueueDB(settings.database_path)
    seed_queue(db, settings.queue_dir)
    post = db.next()
    if post is None:
        log.warning("Queue is empty; add more approved images to %s", settings.queue_dir)
        return "empty"

    image_path = Path(post.image_path)
    if settings.dry_run:
        log.info("DRY RUN — would publish #%s: %s", post.id, image_path)
        return "dry-run"

    try:
        media_id = InstagramPublisher(settings).publish(image_path, post.caption)
        db.mark_published(post.id, media_id)
        log.info("Published #%s as Instagram media %s", post.id, media_id)
        return media_id
    except Exception as exc:
        db.mark_failed(post.id, str(exc))
        log.exception("Failed to publish #%s", post.id)
        raise

