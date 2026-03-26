"""
Seedance 2.0 API Client — MuAPI Wrapper

Provides programmatic access to ByteDance Seedance 2.0 video generation
via the MuAPI.ai proxy. Supports T2V, I2V, Video Edit, and Video Extension.

Usage:
    from seedance_api import SeedanceAPI

    api = SeedanceAPI()  # reads MUAPI_API_KEY from env
    result = api.text_to_video(prompt="...", aspect_ratio="16:9", duration=5)
    video = api.wait_for_completion(result["request_id"])
"""

import os
import time
import json
import requests
from typing import Optional


class SeedanceAPI:
    """Client for Seedance 2.0 via MuAPI.ai."""

    BASE_URL = "https://api.muapi.ai/api/v1"

    ENDPOINTS = {
        "t2v": "/seedance-v2.0-t2v",
        "i2v": "/seedance-v2.0-i2v",
        "edit": "/seedance-v2.0-video-edit",
        "extend": "/seedance-v2.0-extend",
    }

    VALID_ASPECTS = {"16:9", "9:16", "4:3", "3:4", "21:9", "1:1"}
    VALID_DURATIONS = {5, 10}
    VALID_QUALITIES = {"basic", "high"}

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("MUAPI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "MUAPI_API_KEY not found. Set it as an environment variable "
                "or pass api_key to the constructor."
            )
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
        }

    def _post(self, endpoint: str, payload: dict) -> dict:
        """Send a POST request to MuAPI."""
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.post(url, headers=self.headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    def text_to_video(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        duration: int = 5,
        quality: str = "basic",
    ) -> dict:
        """Generate video from text prompt."""
        self._validate_params(aspect_ratio, duration, quality)
        return self._post(
            self.ENDPOINTS["t2v"],
            {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "duration": duration,
                "quality": quality,
            },
        )

    def image_to_video(
        self,
        prompt: str,
        images_list: list[str],
        aspect_ratio: str = "16:9",
        duration: int = 5,
        quality: str = "basic",
    ) -> dict:
        """Generate video from images + text prompt."""
        self._validate_params(aspect_ratio, duration, quality)
        return self._post(
            self.ENDPOINTS["i2v"],
            {
                "prompt": prompt,
                "images_list": images_list,
                "aspect_ratio": aspect_ratio,
                "duration": duration,
                "quality": quality,
            },
        )

    def video_edit(
        self,
        prompt: str,
        video_urls: list[str],
        images_list: Optional[list[str]] = None,
        aspect_ratio: str = "16:9",
        quality: str = "basic",
        remove_watermark: bool = False,
    ) -> dict:
        """Edit an existing video with a text prompt."""
        self._validate_params(aspect_ratio, quality=quality)
        payload = {
            "prompt": prompt,
            "video_urls": video_urls,
            "aspect_ratio": aspect_ratio,
            "quality": quality,
            "remove_watermark": remove_watermark,
        }
        if images_list:
            payload["images_list"] = images_list
        return self._post(self.ENDPOINTS["edit"], payload)

    def extend_video(
        self,
        request_id: str,
        prompt: Optional[str] = None,
        duration: int = 5,
        quality: str = "basic",
    ) -> dict:
        """Extend a previously generated video."""
        payload = {
            "request_id": request_id,
            "duration": duration,
            "quality": quality,
        }
        if prompt:
            payload["prompt"] = prompt
        return self._post(self.ENDPOINTS["extend"], payload)

    def get_result(self, request_id: str) -> dict:
        """Check the status/result of a generation task."""
        url = f"{self.BASE_URL}/predictions/{request_id}/result"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def wait_for_completion(
        self,
        request_id: str,
        poll_interval: int = 5,
        timeout: int = 600,
    ) -> dict:
        """Poll until generation completes or times out."""
        start = time.time()
        while time.time() - start < timeout:
            result = self.get_result(request_id)
            status = result.get("status")
            if status == "completed":
                return result
            if status == "failed":
                raise RuntimeError(
                    f"Generation failed: {result.get('error', 'Unknown error')}"
                )
            time.sleep(poll_interval)
        raise TimeoutError(
            f"Generation timed out after {timeout}s (request_id: {request_id})"
        )

    def _validate_params(
        self,
        aspect_ratio: Optional[str] = None,
        duration: Optional[int] = None,
        quality: Optional[str] = None,
    ):
        """Validate common parameters."""
        if aspect_ratio and aspect_ratio not in self.VALID_ASPECTS:
            raise ValueError(
                f"Invalid aspect_ratio '{aspect_ratio}'. "
                f"Must be one of: {self.VALID_ASPECTS}"
            )
        if duration is not None and duration not in self.VALID_DURATIONS:
            raise ValueError(
                f"Invalid duration '{duration}'. Must be one of: {self.VALID_DURATIONS}"
            )
        if quality and quality not in self.VALID_QUALITIES:
            raise ValueError(
                f"Invalid quality '{quality}'. "
                f"Must be one of: {self.VALID_QUALITIES}"
            )
