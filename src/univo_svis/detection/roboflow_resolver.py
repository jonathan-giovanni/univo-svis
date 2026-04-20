"""Roboflow model access strategy — Local weights first, API fallback second."""

from __future__ import annotations

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class RoboflowResolver:
    """Implements the Vest Model Access Strategy."""

    def __init__(
        self,
        local_weights: str,
        workspace: str,
        project: str,
        version: int,
        project_root: Path,
        api_key_env: str = "ROBOFLOW_API_KEY",
    ) -> None:
        self._local_weights = project_root / local_weights
        self._workspace = workspace
        self._project = project
        self._version = version
        self._api_key_env = api_key_env
        self._api_key = os.environ.get(api_key_env)

    @property
    def has_local_weights(self) -> bool:
        """Check if local weights exist on disk."""
        exists = self._local_weights.exists()
        if exists:
            logger.info("Found local vest model at: %s", self._local_weights)
        else:
            logger.warning("Local vest model weights NOT found at: %s", self._local_weights)
        return exists

    @property
    def can_use_api(self) -> bool:
        """Check if API fallback is configured and key is present."""
        if not self._api_key:
            logger.warning(
                "Roboflow API key missing in environment variable: %s", self._api_key_env
            )
            return False
        return True

    def get_inference_mode(self) -> str:
        """Determine the best available inference mode.

        Returns:
            "local", "api", or "none"
        """
        if self.has_local_weights:
            return "local"
        if self.can_use_api:
            return "api"
        return "none"

    def get_local_path(self) -> str | None:
        """Get absolute path to local weights if they exist."""
        return str(self._local_weights.resolve()) if self.has_local_weights else None

    def get_api_params(self) -> dict:
        """Get parameters for Roboflow API inference."""
        return {
            "workspace": self._workspace,
            "project": self._project,
            "version": self._version,
            "api_key": self._api_key,
        }
