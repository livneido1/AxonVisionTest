import cv2
import threading
import queue
import numpy as np
from typing import Iterator


class Streamer:
    def __init__(self, video_path: str, queue_size: int = 128):
        self.video_path = video_path
        self.frame_queue = queue.Queue(maxsize=queue_size)
        self.stop_event = threading.Event()

    def _producer(self):
        """
        creates a thread to produce frames into the queue
        :return:
        """
        cap = cv2.VideoCapture(self.video_path)
        while not self.stop_event.is_set():
            success, frame = cap.read()
            if not success:
                break

            # This will block if the queue is full, preventing RAM overflow
            self.frame_queue.put(frame)

        # Signal that the video is finished
        self.frame_queue.put(None)
        cap.release()

    def yield_images(self) -> Iterator[np.ndarray]:
        """
        consumer task (main thread) - yields images upon request to allow a smooth video
        :return:
        """

        producer_thread = threading.Thread(target=self._producer, daemon=True)
        producer_thread.start()
        # Todo need to set a waiting time to promise a smooth processing

        try:
            while True:
                frame = self.frame_queue.get()

                if frame is None:
                    break

                yield frame
        finally:
            # Ensure the producer stops if the generator is closed early
            self.stop_event.set()
            # shuts down gracefully and prevents zombie threads
            producer_thread.join(timeout=1.0)