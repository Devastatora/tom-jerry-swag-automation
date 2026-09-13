from __future__ import annotations

import time
from pathlib import Path

import cloudinary
import cloudinary.uploader
import requests

from .config import Settings, validate_live_settings


class InstagramPublisher:
    def __init__(self, settings: Settings):
        self.settings = settings

    def upload_public_image(self, image_path: Path) -> str:
        cloudinary.config(
            cloud_name=self.settings.cloudinary_cloud_name,
            api_key=self.settings.cloudinary_api_key,
            api_secret=self.settings.cloudinary_api_secret,
            secure=True,
        )
        result = cloudinary.uploader.upload(
            str(image_path),
            folder="retrogram",
            resource_type="image",
            overwrite=False,
        )
        return result["secure_url"]

    def _post(self, url: str, data: dict[str, str]) -> dict:
        response = requests.post(url, data=data, timeout=60)
        response.raise_for_status()
        return response.json()

    def _get(self, url: str, params: dict[str, str]) -> dict:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        return response.json()

    def publish_url(self, image_url: str, caption: str) -> str:
        validate_live_settings(self.settings)
        token = self.settings.instagram_access_token

        container = self._post(
            f"{self.settings.graph_base}/{self.settings.instagram_user_id}/media",
            {"image_url": image_url, "caption": caption, "access_token": token},
        )
        creation_id = container["id"]

        for _ in range(12):
            status = self._get(
                f"{self.settings.graph_base}/{creation_id}",
                {"fields": "status_code,status", "access_token": token},
            )
            code = status.get("status_code")
            if code == "FINISHED":
                break
            if code in {"ERROR", "EXPIRED"}:
                raise RuntimeError(f"Instagram container failed: {status}")
            time.sleep(5)
        else:
            raise TimeoutError("Instagram media container was not ready after 60 seconds")

        published = self._post(
            f"{self.settings.graph_base}/{self.settings.instagram_user_id}/media_publish",
            {"creation_id": creation_id, "access_token": token},
        )
        return published["id"]

    def publish(self, image_path: Path, caption: str) -> str:
        return self.publish_url(self.upload_public_image(image_path), caption)
