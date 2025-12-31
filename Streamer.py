from pathlib import Path
import os
from typing import Iterator

import cv2
from openpyxl.drawing.image import Image

class Streamer:
    def __init__(self, video_path):
        self.video_path = video_path

    def yield_images(self)-> Iterator[Image]:
        # Open the video file
        video = cv2.VideoCapture(self.video_path)
        current_frame = 0

        while True:
            success, frame = video.read()

            if not success:
                break

            yield frame
        video.release()

