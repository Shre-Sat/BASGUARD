"""
Perception Layer — Object Detection Module
============================================
YOLOv8-nano for general object detection + HSV color-based
filtering to identify red, yellow, and outer boxes specifically.
"""

import cv2
import numpy as np
import logging
import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """Represents a single detected object."""
    class_name: str          # e.g., "red_box", "yellow_box", "outer_box", "person"
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float
    color_label: str = ""    # Color classification from HSV analysis
    center: Tuple[int, int] = (0, 0)
    area: int = 0
    track_id: int = -1       # For future tracking integration

    def __post_init__(self):
        x1, y1, x2, y2 = self.bbox
        self.center = ((x1 + x2) // 2, (y1 + y2) // 2)
        self.area = (x2 - x1) * (y2 - y1)


class ObjectDetector:
    """
    Object detection combining YOLOv8-nano with HSV color filtering.
    
    Strategy:
    - YOLO detects general objects (boxes, containers)
    - HSV color analysis on detected regions classifies red vs yellow boxes
    - Fallback: pure color-based detection if YOLO misses objects
    """

    def __init__(self, config: dict):
        self.confidence_threshold = config.get("confidence_threshold", 0.45)
        self.iou_threshold = config.get("iou_threshold", 0.5)
        self.color_filters = config.get("color_filters", {})
        self._model = None
        self._yolo_available = False
        self._inference_time = 0.0

        self._load_model(config.get("yolo_model", "yolov8n.pt"))

    def _load_model(self, model_path: str):
        """Load YOLOv8 model. Falls back to color-only detection if unavailable."""
        try:
            from ultralytics import YOLO
            self._model = YOLO(model_path)
            self._yolo_available = True
            logger.info(f"YOLOv8 model loaded: {model_path}")
        except Exception as e:
            logger.warning(f"Could not load YOLO model ({e}). "
                         f"Falling back to color-based detection only.")
            self._yolo_available = False

    def detect(self, frame: np.ndarray) -> List[Detection]:
        """
        Run object detection on a frame.
        
        Returns list of Detection objects for all recognized items.
        """
        start_time = time.monotonic()
        detections = []

        # Phase 1: YOLO detection (if available)
        if self._yolo_available:
            yolo_detections = self._run_yolo(frame)
            detections.extend(yolo_detections)

        # Phase 2: Color-based detection for specific boxes
        color_detections = self._run_color_detection(frame)

        # Merge: prefer YOLO detections, add color-only if no overlap
        detections = self._merge_detections(detections, color_detections)

        self._inference_time = (time.monotonic() - start_time) * 1000  # ms
        return detections

    def _run_yolo(self, frame: np.ndarray) -> List[Detection]:
        """Run YOLOv8 inference and return detections."""
        detections = []
        try:
            results = self._model(
                frame,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                verbose=False
            )

            for r in results:
                if r.boxes is None:
                    continue
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    cls_name = self._model.names[cls_id]

                    # We care about certain COCO classes that might be our boxes
                    # Classes: "suitcase", "handbag", "backpack", "book",
                    # "cell phone" etc. could match box-like objects
                    # Also detect "person" for astronaut tracking
                    relevant_classes = {
                        "suitcase", "handbag", "backpack", "book",
                        "box", "cell phone", "laptop", "tvmonitor",
                        "bottle", "cup", "bowl", "person"
                    }

                    if cls_name in relevant_classes or conf > 0.7:
                        # Analyze the color of the detected region
                        roi = frame[max(0, y1):y2, max(0, x1):x2]
                        color_label = self._classify_color(roi) if roi.size > 0 else ""

                        # Reclassify based on color
                        if color_label == "red":
                            final_name = "red_box"
                        elif color_label == "yellow":
                            final_name = "yellow_box"
                        elif cls_name == "person":
                            final_name = "person"
                        else:
                            final_name = cls_name

                        detections.append(Detection(
                            class_name=final_name,
                            bbox=(x1, y1, x2, y2),
                            confidence=conf,
                            color_label=color_label
                        ))
        except Exception as e:
            logger.error(f"YOLO inference error: {e}")

        return detections

    def _run_color_detection(self, frame: np.ndarray) -> List[Detection]:
        """
        Detect objects purely by HSV color analysis.
        This is the fallback/supplement to YOLO.
        """
        detections = []
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Detect RED objects
        red_cfg = self.color_filters.get("red", {})
        if red_cfg:
            red_mask = self._create_red_mask(hsv, red_cfg)
            red_bboxes = self._find_contour_bboxes(
                red_mask,
                min_area=red_cfg.get("min_area", 2000)
            )
            for bbox in red_bboxes:
                detections.append(Detection(
                    class_name="red_box",
                    bbox=bbox,
                    confidence=0.75,
                    color_label="red"
                ))

        # Detect YELLOW objects
        yellow_cfg = self.color_filters.get("yellow", {})
        if yellow_cfg:
            lower = np.array(yellow_cfg.get("lower", [20, 100, 100]))
            upper = np.array(yellow_cfg.get("upper", [35, 255, 255]))
            yellow_mask = cv2.inRange(hsv, lower, upper)
            yellow_mask = self._clean_mask(yellow_mask)
            yellow_bboxes = self._find_contour_bboxes(
                yellow_mask,
                min_area=yellow_cfg.get("min_area", 2000)
            )
            for bbox in yellow_bboxes:
                detections.append(Detection(
                    class_name="yellow_box",
                    bbox=bbox,
                    confidence=0.75,
                    color_label="yellow"
                ))

        # Detect OUTER BOX (brown/cardboard)
        outer_cfg = self.color_filters.get("outer_box", {})
        if outer_cfg:
            lower = np.array(outer_cfg.get("lower", [10, 50, 50]))
            upper = np.array(outer_cfg.get("upper", [25, 200, 200]))
            outer_mask = cv2.inRange(hsv, lower, upper)
            outer_mask = self._clean_mask(outer_mask)
            outer_bboxes = self._find_contour_bboxes(
                outer_mask,
                min_area=outer_cfg.get("min_area", 5000)
            )
            for bbox in outer_bboxes:
                detections.append(Detection(
                    class_name="outer_box",
                    bbox=bbox,
                    confidence=0.6,
                    color_label="brown"
                ))

        return detections

    def _create_red_mask(self, hsv: np.ndarray, red_cfg: dict) -> np.ndarray:
        """Create a mask for red objects (handles hue wraparound)."""
        lower1 = np.array(red_cfg.get("lower_1", [0, 100, 100]))
        upper1 = np.array(red_cfg.get("upper_1", [10, 255, 255]))
        lower2 = np.array(red_cfg.get("lower_2", [160, 100, 100]))
        upper2 = np.array(red_cfg.get("upper_2", [180, 255, 255]))

        mask1 = cv2.inRange(hsv, lower1, upper1)
        mask2 = cv2.inRange(hsv, lower2, upper2)
        combined = cv2.bitwise_or(mask1, mask2)
        return self._clean_mask(combined)

    @staticmethod
    def _clean_mask(mask: np.ndarray) -> np.ndarray:
        """Morphological operations to clean up noise in mask."""
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        return mask

    @staticmethod
    def _find_contour_bboxes(
        mask: np.ndarray, min_area: int = 2000
    ) -> List[Tuple[int, int, int, int]]:
        """Find bounding boxes of contours in a binary mask."""
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        bboxes = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= min_area:
                x, y, w, h = cv2.boundingRect(contour)
                bboxes.append((x, y, x + w, y + h))
        return bboxes

    def _classify_color(self, roi: np.ndarray) -> str:
        """Classify the dominant color of an ROI as red, yellow, or unknown."""
        if roi.size == 0:
            return ""

        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv_roi)

        # Check if enough saturation (ignore very dark/bright regions)
        sat_mask = s > 80
        if np.sum(sat_mask) < roi.shape[0] * roi.shape[1] * 0.1:
            return ""

        mean_h = np.mean(h[sat_mask]) if np.any(sat_mask) else 0
        mean_s = np.mean(s[sat_mask]) if np.any(sat_mask) else 0

        # Red: hue near 0 or near 180
        if (mean_h < 12 or mean_h > 165) and mean_s > 80:
            return "red"
        # Yellow: hue 20-35
        elif 18 < mean_h < 38 and mean_s > 80:
            return "yellow"
        # Brown/outer box: hue 10-25, lower saturation
        elif 8 < mean_h < 28 and 40 < mean_s < 120:
            return "brown"

        return ""

    def _merge_detections(
        self,
        yolo_dets: List[Detection],
        color_dets: List[Detection]
    ) -> List[Detection]:
        """
        Merge YOLO and color detections, avoiding duplicates.
        YOLO detections take priority if overlapping.
        """
        if not yolo_dets:
            return color_dets
        if not color_dets:
            return yolo_dets

        merged = list(yolo_dets)

        for cd in color_dets:
            is_duplicate = False
            for yd in yolo_dets:
                iou = self._compute_iou(cd.bbox, yd.bbox)
                if iou > 0.3:
                    is_duplicate = True
                    break
            if not is_duplicate:
                merged.append(cd)

        return merged

    @staticmethod
    def _compute_iou(
        box1: Tuple[int, int, int, int],
        box2: Tuple[int, int, int, int]
    ) -> float:
        """Compute Intersection over Union of two bounding boxes."""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection

        return intersection / union if union > 0 else 0.0

    @property
    def inference_time_ms(self) -> float:
        return self._inference_time

    @property
    def is_yolo_available(self) -> bool:
        return self._yolo_available
