from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    instagram_user_id: str
    instagram_access_token: str
    instagram_api_base: str
    instagram_api_version: str
    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    post_times: tuple[str, str]
    timezone: str
    dry_run: bool
    database_path: Path
    queue_dir: Path

    @property
    def graph_base(self) -> str:
        return f"{self.instagram_api_base.rstrip('/')}/{self.instagram_api_version}"


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        instagram_user_id=os.getenv("INSTAGRAM_USER_ID", ""),
        instagram_access_token=os.getenv("INSTAGRAM_ACCESS_TOKEN", ""),
        instagram_api_base=os.getenv("INSTAGRAM_API_BASE", "https://graph.instagram.com"),
        instagram_api_version=os.getenv("INSTAGRAM_API_VERSION", "v24.0"),
        cloudinary_cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", ""),
        cloudinary_api_key=os.getenv("CLOUDINARY_API_KEY", ""),
        cloudinary_api_secret=os.getenv("CLOUDINARY_API_SECRET", ""),
        post_times=(os.getenv("POST_TIME_1", "10:00"), os.getenv("POST_TIME_2", "20:00")),
        timezone=os.getenv("TIMEZONE", "Europe/Sofia"),
        dry_run=os.getenv("DRY_RUN", "true").lower() in {"1", "true", "yes", "on"},
        database_path=Path(os.getenv("DATABASE_PATH", "data/retrogram.db")),
        queue_dir=Path(os.getenv("QUEUE_DIR", "assets/queue")),
    )


def validate_live_settings(settings: Settings) -> None:
    required = {
        "INSTAGRAM_USER_ID": settings.instagram_user_id,
        "INSTAGRAM_ACCESS_TOKEN": settings.instagram_access_token,
    }
    missing = [key for key, value in required.items() if not value]
    if missing:
        raise RuntimeError("Missing live configuration: " + ", ".join(missing))
