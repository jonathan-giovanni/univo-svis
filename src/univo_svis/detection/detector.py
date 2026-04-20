"""YOLO model coordinator for multiple detectors."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np
from ultralytics import YOLO

from univo_svis.detection.entities import BBox, Detection

if TYPE_CHECKING:
    from univo_svis.detection.roboflow_resolver import RoboflowResolver
    from univo_svis.infrastructure.config.yaml_config_loader import AppConfig

logger = logging.getLogger(__name__)


class DualModelDetector:
    """Coordinater for person (YOLOv11) and vest detection."""

    def __init__(self, config: AppConfig, resolver: RoboflowResolver) -> None:
        self._config = config
        self._resolver = resolver

        # 1. Initialize Person Model (always local ultralytics)
        # Weights path is handled by ultralytics (relative to cwd or absolute)
        person_weights = config.person_model.weights
        logger.info("Initializing Person Model with: %s", person_weights)
        self._person_model = YOLO(person_weights)

        # 2. Initialize Vest Model (Local vs API)
        self._vest_mode = resolver.get_inference_mode()
        self._vest_model_local = None
        self._vest_model_api = None

        if self._vest_mode == "local":
            logger.info("Initializing Vest Model (Local) with: %s", resolver.get_local_path())
            self._vest_model_local = YOLO(resolver.get_local_path())
        elif self._vest_mode == "api":
            logger.info("Initializing Vest Model (API Fallback via Roboflow)")
            try:
                from roboflow import Roboflow

                rf = Roboflow(api_key=resolver._api_key)
                project = rf.workspace(resolver._workspace).project(resolver._project)
                self._vest_model_api = project.version(resolver._version).model
            except ImportError:
                logger.error("Roboflow package not installed. API fallback disabled.")
                self._vest_mode = "none"
            except Exception as e:
                logger.error("Failed to initialize Roboflow API: %s", e)
                self._vest_mode = "none"
        else:
            logger.warning("No vest model available (local or API)")

    @property
    def vest_mode(self) -> str:
        """Get the current vest deduction mode (local, api, none)."""
        return self._vest_mode

    @property
    def has_vest_model(self) -> bool:
        """Check if a functional safety vest model is available."""
        return self._vest_mode in ("local", "api")

    def detect_persons(self, image: np.ndarray, conf: float | None = None) -> list[Detection]:
        """Detect persons in image using YOLOv11."""
        confidence = conf if conf is not None else self._config.person_model.confidence_threshold

        results = self._person_model.predict(
            source=image,
            conf=confidence,
            classes=[0] if not self._config.person_model.class_filter else None,
            # 0 is 'person' in COCO
            verbose=False,
        )

        detections = []
        for result in results:
            for box in result.boxes:
                # box.xyxy[0] returns [x1, y1, x2, y2]
                coords = box.xyxy[0].tolist()
                detections.append(
                    Detection(
                        class_id=str(int(box.cls[0].item())),
                        class_name="person",
                        confidence=float(box.conf[0].item()),
                        bbox=BBox(*coords),
                    )
                )
        return detections

    def detect_vests(self, image: np.ndarray, conf: float | None = None) -> list[Detection]:
        """Detect safety vests in image."""
        confidence = conf if conf is not None else self._config.vest_model.confidence_threshold

        if self._vest_mode == "local":
            return self._detect_vests_local(image, confidence)
        if self._vest_mode == "api":
            return self._detect_vests_api(image, confidence)
        return []

    def _detect_vests_local(self, image: np.ndarray, conf: float) -> list[Detection]:
        """Inference using local YOLO weights."""
        results = self._vest_model_local.predict(
            source=image,
            conf=conf,
            verbose=False,
        )

        detections = []
        for result in results:
            for box in result.boxes:
                coords = box.xyxy[0].tolist()
                detections.append(
                    Detection(
                        class_id=str(int(box.cls[0].item())),
                        class_name="safety_vest",
                        confidence=float(box.conf[0].item()),
                        bbox=BBox(*coords),
                    )
                )
        return detections

    def _detect_vests_api(self, image: np.ndarray, conf: float) -> list[Detection]:
        """Inference using Roboflow API."""
        try:
            prediction = self._vest_model_api.predict(image, confidence=conf).json()
            detections = []
            for pred in prediction["predictions"]:
                # Roboflow returns x, y center, width, height
                x, y, w, h = pred["x"], pred["y"], pred["width"], pred["height"]
                x1, y1 = x - w / 2, y - h / 2
                x2, y2 = x + w / 2, y + h / 2
                detections.append(
                    Detection(
                        class_id=pred["class_id"],
                        class_name="safety_vest",
                        confidence=pred["confidence"],
                        bbox=BBox(x1, y1, x2, y2),
                    )
                )
            return detections
        except Exception as e:
            logger.error("Roboflow API inference failed: %s", e)
            return []
