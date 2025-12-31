import multiprocessing as mp

import cv2

from Detector import Detector
from Presenter import Presenter
from Streamer import Streamer


def streamer_worker(path: str, produce_queue):
    streamer = Streamer(path)
    for frame in streamer.yield_frames():
        produce_queue.put(frame)
    # notifies for the end of the queue
    produce_queue.put(None)


def detector_worker(consume_queue, produce_queue):
    detector = Detector()
    while True:
        frame = consume_queue.get()
        if frame is None:
            break

        original_frame, cnts = detector.detect(frame)
        produce_queue.put((original_frame, cnts))
    # notifies for the end of the queue
    produce_queue.put(None)


def presenter_worker(consume_queue):
    presenter = Presenter(use_blurring=True)
    while True:
        data = consume_queue.get()
        if data is None:
            break

        image, cnts = data
        presenter.draw_and_show(image, cnts)

        # Windows os adaptations
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()


if __name__ == '__main__':
    video_path = r'C:\Users\97250\Desktop\ido\axonVIsion\code\People - 6387.mp4'

    # common queues to communication between processes
    frames_queue = mp.Queue(maxsize=30)  # prevent streamer to overload and filling up the RAM
    frames_with_detections_queue = mp.Queue(maxsize=30)  # prevent the detector to overload and filling up the RAM

    # defines the processes
    streamer_proc = mp.Process(target=streamer_worker, args=(video_path, frames_queue))
    detector_proc = mp.Process(target=detector_worker, args=(frames_queue, frames_with_detections_queue))
    presenter_proc = mp.Process(target=presenter_worker, args=(frames_with_detections_queue,))

    streamer_proc.start()
    detector_proc.start()
    presenter_proc.start()

    streamer_proc.join()
    detector_proc.join()
    presenter_proc.join()
