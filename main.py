import multiprocessing as mp
import time
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


def presenter_worker(consume_queue, video_fps: float):
    presenter = Presenter(use_blurring=True)
    frame_required_duration_ms = 1.0 / video_fps
    video_actual_start_time = time.time()
    frames_displayed = 0
    while True:
        data = consume_queue.get()
        if data is None:
            break

        image, cnts = data
        presenter.draw_and_show(image, cnts)

        frames_displayed += 1

        target_time_present = video_actual_start_time + (frames_displayed * frame_required_duration_ms)
        current_time = time.time()
        sleep_time_ms = int((target_time_present - current_time) * 1000)

        # waits until the next frame should be presented as calculated above
        if cv2.waitKey(max(1, sleep_time_ms)) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()


if __name__ == '__main__':
    video_path = r'C:\Users\97250\Desktop\ido\axonVIsion\code\People - 6387.mp4'

    # common queues to communication between processes
    frames_queue = mp.Queue(maxsize=30)  # prevent streamer to overload and filling up the RAM
    frames_with_detections_queue = mp.Queue(maxsize=30)  # prevent the detector to overload and filling up the RAM

    video_fps: float = Streamer.get_video_fps(video_path)
    # defines the processes
    streamer_proc = mp.Process(target=streamer_worker, args=(video_path, frames_queue))
    detector_proc = mp.Process(target=detector_worker, args=(frames_queue, frames_with_detections_queue))
    presenter_proc = mp.Process(target=presenter_worker, args=(frames_with_detections_queue, video_fps))

    streamer_proc.start()
    detector_proc.start()
    presenter_proc.start()

    streamer_proc.join()
    detector_proc.join()
    presenter_proc.join()
