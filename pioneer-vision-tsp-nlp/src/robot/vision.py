"""OpenCV-based detector for traffic lights and traffic signs.

The detector is *colour-and-shape* based, which is robust enough for the
simulated CoppeliaSim arena and keeps inference fast (~5-10 ms / frame on
a typical laptop CPU). The class exposes one entry point:

    ``TrafficVision.detect(bgr_image) -> list[Detection]``

Each detection carries the bounding box, a label and a confidence value
derived from area + circularity / vertex-count heuristics.

Supported labels:
    ``stop``                    - red octagon
    ``yield``                   - red/white triangle pointing down
    ``no_entry``                - red circle with white horizontal bar
    ``speed_limit_30/50/80``    - red-rimmed circle with digits
    ``mandatory_*``             - solid blue circle (forward/left/right arrow)
    ``traffic_light_red``       - red illuminated lamp
    ``traffic_light_yellow``    - amber lamp
    ``traffic_light_green``     - green lamp
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Sequence, Tuple

import cv2
import numpy as np


class LightState(str, Enum):
    """Traffic-light state enum."""

    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"
    UNKNOWN = "unknown"


@dataclass
class Detection:
    """A single object detection result."""

    label: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    extra: dict = None

    def center(self) -> Tuple[int, int]:
        x, y, w, h = self.bbox
        return x + w // 2, y + h // 2

    def area(self) -> int:
        return self.bbox[2] * self.bbox[3]


# ---------------------------------------------------------------------------
# HSV ranges. CoppeliaSim materials are usually saturated, so we use generous
# but still selective bands. RED wraps around hue=0, so it needs two ranges.
# ---------------------------------------------------------------------------
HSV_RED_1 = (np.array([0, 110, 110]),   np.array([10, 255, 255]))
HSV_RED_2 = (np.array([165, 110, 110]), np.array([180, 255, 255]))
HSV_YELLOW = (np.array([18, 130, 150]), np.array([34, 255, 255]))
HSV_GREEN = (np.array([40, 90, 110]),    np.array([85, 255, 255]))
HSV_BLUE = (np.array([95, 110, 70]),    np.array([130, 255, 255]))


def _mask(hsv: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    m = cv2.inRange(hsv, lo, hi)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return m


def _red_mask(hsv: np.ndarray) -> np.ndarray:
    return cv2.bitwise_or(
        _mask(hsv, *HSV_RED_1),
        _mask(hsv, *HSV_RED_2),
    )


def _circularity(contour: np.ndarray) -> float:
    a = cv2.contourArea(contour)
    p = cv2.arcLength(contour, closed=True)
    if p == 0:
        return 0.0
    return 4.0 * np.pi * a / (p * p)


class TrafficVision:
    """Detect traffic lights and signs from an OpenCV BGR frame.

    Args:
        min_area: Minimum contour area (px). Tune for the camera resolution.
        max_area_ratio: Reject contours covering more than this fraction of
            the frame (avoids walls / very close objects polluting results).
        debug: If True, ``detect`` will also annotate ``debug_frame``.
    """

    def __init__(
        self,
        min_area: int = 400,
        max_area_ratio: float = 0.45,
        debug: bool = True,
    ):
        self.min_area = min_area
        self.max_area_ratio = max_area_ratio
        self.debug = debug
        self.debug_frame: np.ndarray | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def detect(self, bgr: np.ndarray) -> List[Detection]:
        """Run the full detection pipeline on a BGR frame."""
        if bgr is None or bgr.size == 0:
            return []

        if self.debug:
            self.debug_frame = bgr.copy()

        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        H, W = bgr.shape[:2]
        max_area = self.max_area_ratio * H * W

        results: List[Detection] = []
        results += self._detect_red_signs(bgr, hsv, max_area)
        results += self._detect_blue_signs(bgr, hsv, max_area)
        results += self._detect_traffic_lights(bgr, hsv, max_area)

        results = self._non_max_suppress(results, iou_thresh=0.4)

        if self.debug and self.debug_frame is not None:
            for det in results:
                color = _label_color(det.label)
                x, y, w, h = det.bbox
                cv2.rectangle(self.debug_frame, (x, y), (x + w, y + h), color, 2)
                tag = f"{det.label} {det.confidence:.2f}"
                cv2.putText(
                    self.debug_frame,
                    tag,
                    (x, max(15, y - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    1,
                    cv2.LINE_AA,
                )

        return results

    # ------------------------------------------------------------------
    # Red signs: stop (octagon), yield (down-triangle), no_entry / speed limits (circle)
    # ------------------------------------------------------------------
    def _detect_red_signs(self, bgr, hsv, max_area) -> List[Detection]:
        mask = _red_mask(hsv)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        out: List[Detection] = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.min_area or area > max_area:
                continue
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
            verts = len(approx)
            circ = _circularity(cnt)
            x, y, w, h = cv2.boundingRect(cnt)
            aspect = w / h if h > 0 else 0

            # Area ratio vs the minimum enclosing circle - 1.0 is a perfect
            # circle, ~0.90 is a regular octagon, ~0.43 is a triangle.
            (_, _), enc_r = cv2.minEnclosingCircle(cnt)
            enc_area = np.pi * enc_r * enc_r
            ratio = area / enc_area if enc_area > 0 else 0.0

            label = None
            conf = 0.5

            is_triangle = verts == 3 and 0.40 <= ratio <= 0.65
            is_circle = ratio > 0.92
            is_octagon = 0.78 <= ratio <= 0.93 and verts >= 5

            if is_triangle and 0.6 < aspect < 1.6:
                label = "yield"
                conf = min(0.95, 0.6 + max(0.0, 1.0 - abs(aspect - 1.0)))
            elif is_octagon and 0.78 < aspect < 1.25:
                label = "stop"
                conf = min(0.95, 0.6 + circ * 0.35)
            elif is_circle and 0.82 < aspect < 1.2:
                roi = bgr[y:y + h, x:x + w]
                if self._has_horizontal_white_bar(roi):
                    label = "no_entry"
                    conf = 0.88
                else:
                    digit = self._read_speed_digits(roi)
                    label = f"speed_limit_{digit}" if digit else "speed_limit"
                    conf = 0.78

            if label is not None:
                out.append(Detection(
                    label=label,
                    confidence=float(conf),
                    bbox=(int(x), int(y), int(w), int(h)),
                    extra={"vertices": int(verts),
                           "circularity": float(circ),
                           "enclosing_ratio": float(ratio)},
                ))
        return out

    # ------------------------------------------------------------------
    # Blue mandatory signs (circle with arrow)
    # ------------------------------------------------------------------
    def _detect_blue_signs(self, bgr, hsv, max_area) -> List[Detection]:
        mask = _mask(hsv, *HSV_BLUE)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        out: List[Detection] = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.min_area or area > max_area:
                continue
            circ = _circularity(cnt)
            if circ < 0.7:
                continue
            x, y, w, h = cv2.boundingRect(cnt)
            aspect = w / h if h > 0 else 0
            if not 0.8 < aspect < 1.25:
                continue
            roi = bgr[y:y + h, x:x + w]
            direction = self._mandatory_direction(roi)
            label = f"mandatory_{direction}" if direction else "mandatory"
            out.append(Detection(
                label=label,
                confidence=float(min(0.9, circ)),
                bbox=(int(x), int(y), int(w), int(h)),
                extra={"circularity": float(circ)},
            ))
        return out

    # ------------------------------------------------------------------
    # Traffic lights: find a dark housing, then determine which lamp is bright.
    # ------------------------------------------------------------------
    def _detect_traffic_lights(self, bgr, hsv, max_area) -> List[Detection]:
        red_mask = _red_mask(hsv)
        yellow_mask = _mask(hsv, *HSV_YELLOW)
        green_mask = _mask(hsv, *HSV_GREEN)

        out: List[Detection] = []
        for color_name, mask in (
            ("red", red_mask), ("yellow", yellow_mask), ("green", green_mask),
        ):
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < self.min_area * 0.4 or area > max_area:
                    continue
                circ = _circularity(cnt)
                if circ < 0.65:
                    continue
                x, y, w, h = cv2.boundingRect(cnt)
                aspect = w / h if h > 0 else 0
                if not 0.7 < aspect < 1.4:
                    continue
                # A traffic light lamp is typically surrounded by dark housing.
                if not self._has_dark_surround(bgr, x, y, w, h):
                    continue
                out.append(Detection(
                    label=f"traffic_light_{color_name}",
                    confidence=float(min(0.95, circ + 0.05)),
                    bbox=(int(x), int(y), int(w), int(h)),
                    extra={"state": color_name, "circularity": float(circ)},
                ))
        return out

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _has_dark_surround(self, bgr, x, y, w, h, pad: int = 6) -> bool:
        H, W = bgr.shape[:2]
        x0 = max(0, x - pad); y0 = max(0, y - pad)
        x1 = min(W, x + w + pad); y1 = min(H, y + h + pad)
        outer = bgr[y0:y1, x0:x1].copy()
        if outer.size == 0:
            return False
        ix0 = max(0, x - x0); iy0 = max(0, y - y0)
        outer[iy0:iy0 + h, ix0:ix0 + w] = 0
        gray = cv2.cvtColor(outer, cv2.COLOR_BGR2GRAY)
        nonzero = gray[gray > 0]
        if nonzero.size == 0:
            return False
        return float(np.mean(nonzero)) < 90.0

    def _has_horizontal_white_bar(self, roi_bgr: np.ndarray) -> bool:
        """Distinguish no-entry (mostly red disk + narrow white bar) from a
        speed-limit sign (white disk inside red rim + black digits).
        """
        if roi_bgr.size == 0:
            return False
        h, w = roi_bgr.shape[:2]
        # Look at the inner area, well inside the red rim
        y0, y1 = int(h * 0.20), int(h * 0.80)
        x0, x1 = int(w * 0.20), int(w * 0.80)
        inner = roi_bgr[y0:y1, x0:x1]
        if inner.size == 0:
            return False
        gray = cv2.cvtColor(inner, cv2.COLOR_BGR2GRAY)
        white_frac = float(np.mean(gray > 200))
        # Speed limit signs have a predominantly white inner disk.
        if white_frac > 0.45:
            return False
        # No-entry: detect a narrow bright horizontal band crossing the centre.
        center_band = gray[int(gray.shape[0] * 0.42):int(gray.shape[0] * 0.58)]
        if center_band.size == 0:
            return False
        return float(np.mean(center_band > 200)) > 0.5

    def _read_speed_digits(self, roi_bgr: np.ndarray) -> str | None:
        """Discriminate 30 / 50 / 80 by counting topological holes in digits.

        ``"0"`` has 1 hole, ``"8"`` has 2, ``"3"`` and ``"5"`` have 0. We then
        separate ``"3"`` from ``"5"`` by checking ink in the upper-left vs
        upper-right of the leftmost digit. Returns ``None`` if shapes don't
        match any known template.
        """
        if roi_bgr.size == 0:
            return None
        gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
        # Threshold isolating the BLACK digits (pixel values < 80) - the red
        # rim has medium gray and the inner disk is near-white, so a fixed
        # threshold gives a clean digit mask.
        _, th = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)
        h, w = th.shape
        inner = th[int(h * 0.27):int(h * 0.82), int(w * 0.22):int(w * 0.78)]
        if inner.size == 0:
            return None

        # Find external contours = digits; hierarchy gives us holes.
        cnts, hierarchy = cv2.findContours(inner, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        if hierarchy is None:
            return None
        hierarchy = hierarchy[0]
        digits = []
        for i, c in enumerate(cnts):
            if cv2.contourArea(c) < 0.01 * inner.size:
                continue
            if hierarchy[i][3] != -1:
                continue  # this is a hole, skip
            holes = 0
            j = hierarchy[i][2]
            while j != -1:
                if cv2.contourArea(cnts[j]) > 0.003 * inner.size:
                    holes += 1
                j = hierarchy[j][0]
            x, y, ww, hh = cv2.boundingRect(c)
            digits.append((x, y, ww, hh, holes, c))

        if len(digits) < 2:
            return None
        digits.sort(key=lambda d: d[0])
        left = digits[0]
        right = digits[1]

        if left[4] == 2:
            return "80"
        if right[4] != 1:
            return None  # not "X0" pattern

        # Left digit is "3" or "5" - compare upper-left ink to lower-left ink.
        lx, ly, lw, lh = left[:4]
        d_roi = inner[ly:ly + lh, lx:lx + lw]
        if d_roi.size == 0:
            return "50"
        upper = float(np.mean(d_roi[:d_roi.shape[0] // 2, :d_roi.shape[1] // 2]))
        lower = float(np.mean(d_roi[d_roi.shape[0] // 2:, :d_roi.shape[1] // 2]))
        # "5" has a strong top-left ink (horizontal bar), "3" has very little.
        return "50" if upper > lower + 20 else "30"

    def _mandatory_direction(self, roi_bgr: np.ndarray) -> str | None:
        if roi_bgr.size == 0:
            return None
        gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
        _, th = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        h, w = th.shape
        cy, cx = h // 2, w // 2
        mask = np.zeros_like(th)
        cv2.circle(mask, (cx, cy), int(min(h, w) * 0.46), 255, -1)
        inner = cv2.bitwise_and(th, mask)
        ys, xs = np.where(inner > 0)
        if len(xs) < 20:
            return None
        # Centroid of the white arrow within the disk - displaced from center
        # toward the tip (since the tip extends further than the body).
        mean_x = (xs.mean() - cx) / w
        mean_y = (ys.mean() - cy) / h
        if abs(mean_x) > abs(mean_y) and abs(mean_x) > 0.02:
            return "right" if mean_x > 0 else "left"
        if abs(mean_y) > 0.02:
            return "forward" if mean_y < 0 else "back"
        return None

    def _non_max_suppress(
        self, dets: List[Detection], iou_thresh: float = 0.4
    ) -> List[Detection]:
        if not dets:
            return []
        dets = sorted(dets, key=lambda d: d.confidence, reverse=True)
        kept: List[Detection] = []
        for det in dets:
            keep = True
            for k in kept:
                if _iou(det.bbox, k.bbox) > iou_thresh:
                    keep = False
                    break
            if keep:
                kept.append(det)
        return kept


def _iou(a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ix0 = max(ax, bx); iy0 = max(ay, by)
    ix1 = min(ax + aw, bx + bw); iy1 = min(ay + ah, by + bh)
    iw = max(0, ix1 - ix0); ih = max(0, iy1 - iy0)
    inter = iw * ih
    if inter == 0:
        return 0.0
    union = aw * ah + bw * bh - inter
    return inter / union if union > 0 else 0.0


def _label_color(label: str) -> Tuple[int, int, int]:
    if label.startswith("traffic_light_red") or label == "stop" or label == "no_entry":
        return (0, 0, 255)
    if label.startswith("traffic_light_yellow") or label.startswith("speed_limit"):
        return (0, 200, 255)
    if label.startswith("traffic_light_green"):
        return (0, 220, 0)
    if label.startswith("mandatory"):
        return (255, 120, 0)
    if label == "yield":
        return (0, 100, 255)
    return (255, 255, 255)
