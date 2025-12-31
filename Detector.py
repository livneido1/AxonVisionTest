import cv2
import imutils
import numpy as np
from typing import Tuple, List


class Detector:
    def __init__(self):
        self.counter = 0
        self.prev_frame = None

    def detect(self, frame: np.ndarray) -> Tuple[np.ndarray, List[np.ndarray]]:
        # using given code to detect
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.counter == 0:
            self.prev_frame = gray_frame
            self.counter += 1
            # cannot detect anything in the first frame as it detects differences
            return frame, []
        else:
            diff = cv2.absdiff(gray_frame, self.prev_frame)
            thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            self.prev_frame = gray_frame
            self.counter += 1

            # Return the original image and the detections found
            return frame, cnts