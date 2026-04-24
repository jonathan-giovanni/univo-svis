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

        # 2. Vest Model is lazy-initialized or initialized by set_vest_mode
        self._vest_model_local = None
        self._vest_model_api = None
        
        # Start by explicitly setting the mode based on resolver default
        self.set_vest_mode(resolver.get_inference_mode())

    def set_vest_mode(self, mode: str) -> None:
        """Force the vest mode to Local or API."""
        if mode == "local":
            if self._resolver.has_local_weights:
                if self._vest_model_local is None:
                    logger.info("Initializing Vest Model (Local) with: %s", self._resolver.get_local_path())
                    self._vest_model_local = YOLO(self._resolver.get_local_path())
                self._vest_mode = "local"
            else:
                logger.warning("Requested local mode but weights are missing.")
                self._vest_mode = "local_error"
        elif mode == "api":
            if self._resolver.can_use_api:
                if self._vest_model_api is None:
                    logger.info("Initializing Vest Model (API via Roboflow Serverless)")
                    try:
                        from inference_sdk import InferenceHTTPClient
                        self._vest_model_api = InferenceHTTPClient(
                            api_url="https://serverless.roboflow.com",
                            api_key=self._resolver._api_key
                        )
                        self._vest_mode = "api"
                    except ImportError:
                        logger.error("inference-sdk package not installed. Serverless fallback disabled.")
                        self._vest_mode = "api_error"
                    except Exception as e:
                        logger.error("Failed to initialize Roboflow Serverless: %s", e)
                        self._vest_mode = "api_error"
                else:
                    self._vest_mode = "api"
            else:
                logger.warning("Requested API mode but key is missing.")
                self._vest_mode = "api_error"
        else:
            self._vest_mode = "none"

    @property
    def vest_mode(self) -> str:
        """Get the current vest deduction mode (local, api, none, or error states)."""
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
        """Inference using Roboflow Serverless API."""
        try:
            model_id = f"{self._resolver._project}/{self._resolver._version}"
            prediction = self._vest_model_api.infer(image, model_id=model_id)
            
            detections = []
            if isinstance(prediction, list):
                prediction = prediction[0]
                
            for pred in prediction.get("predictions", []):
                if pred["confidence"] < conf:
                    continue
                # Roboflow returns x, y center, width, height
                x, y, w, h = pred["x"], pred["y"], pred["width"], pred["height"]
                x1, y1 = x - w / 2, y - h / 2
                x2, y2 = x + w / 2, y + h / 2
                detections.append(
                    Detection(
                        class_id=str(pred.get("class_id", "0")),
                        class_name="safety_vest",
                        confidence=pred["confidence"],
                        bbox=BBox(x1, y1, x2, y2),
                    )
                )
            return detections
        except Exception as e:
            logger.error("Roboflow Serverless API inference failed: %s", e)
            return []
