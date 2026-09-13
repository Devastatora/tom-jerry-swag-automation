from __future__ import annotations

import json
import os
from pathlib import Path

from .config import load_settings
from .instagram import InstagramPublisher


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "assets" / "queue" / "manifest.json"
STATE = ROOT / "data" / "state.json"


def load_state() -> dict:
    if not STATE.exists():
        return {"next_index": 0, "published": []}
    return json.loads(STATE.read_text(encoding="utf-8"))


def save_state(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def public_image_url(filename: str) -> str:
    custom_base = os.getenv("PUBLIC_IMAGE_BASE_URL", "").rstrip("/")
    if custom_base:
        return f"{custom_base}/{filename}"

    repository = os.getenv("GITHUB_REPOSITORY", "")
    revision = os.getenv("GITHUB_SHA", "main")
    if not repository:
        raise RuntimeError("GITHUB_REPOSITORY is missing; run this through GitHub Actions")
    return f"https://raw.githubusercontent.com/{repository}/{revision}/assets/queue/{filename}"


def main() -> None:
    settings = load_settings()
    posts = json.loads(MANIFEST.read_text(encoding="utf-8"))["posts"]
    state = load_state()
    index = int(state.get("next_index", 0))

    if index >= len(posts):
        print("QUEUE_EMPTY: add more approved posts to assets/queue/manifest.json")
        return

    post = posts[index]
    image_url = public_image_url(post["file"])
    if settings.dry_run:
        print(f"DRY_RUN: would publish {post['file']} from {image_url}")
        return

    media_id = InstagramPublisher(settings).publish_url(image_url, post["caption"])
    state.setdefault("published", []).append(
        {"file": post["file"], "instagram_media_id": media_id}
    )
    state["next_index"] = index + 1
    save_state(state)
    print(f"PUBLISHED: {post['file']} as {media_id}")


if __name__ == "__main__":
    main()
