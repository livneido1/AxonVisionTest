from datetime import datetime
from typing import List, Tuple

import cv2
import numpy as np


class Presenter:
    def __init__(self, use_blurring: bool = False):
        self._font = cv2.FONT_HERSHEY_SIMPLEX
        self._line_type = cv2.LINE_AA
        self._detection_color: Tuple[int, int, int] = (0, 255, 0)  # green
        self._detection_line_thickness: int = 2
        self._date_time_format: str = "%d-%m-%Y %H:%M:%S"
        self._font_scale = 0.7
        self._font_color = (0, 255, 255)
        self._font_thickness = 2
        self._date_position = (10, 30)  # top left corner
        self.use_blurring = use_blurring

    def draw_and_show(self, image: np.ndarray, cnts: List[np.ndarray]):

        self._draw_detections(cnts, image)

        self._write_current_time(image)

        cv2.imshow("Video With Detections", image)

    def _write_current_time(self, image: np.ndarray):
        timestamp = datetime.now().strftime(self._date_time_format)
        cv2.putText(image, timestamp, self._date_position, self._font, self._font_scale, self._font_color,
                    self._font_thickness, self._line_type)

    def _draw_detections(self, cnts: list[np.ndarray], image: np.ndarray):
        for c in cnts:
            (x, y, w, h) = cv2.boundingRect(c)

            if self.use_blurring:
                self._blur_detection(h, image, w, x, y)
            else:
                cv2.rectangle(image, (x, y), (x + w, y + h), self._detection_color, self._detection_line_thickness)

    def _blur_detection(self, h: int, image: np.ndarray, w: int, x: int, y: int):
        roi = image[y:y + h, x:x + w]
        blurred_roi = cv2.blur(roi, (51, 51))
        image[y:y + h, x:x + w] = blurred_roi
