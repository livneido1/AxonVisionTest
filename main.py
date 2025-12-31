import argparse
import multiprocessing as mp
import os
import threading
import time

import cv2

from Detector import Detector
from Presenter import Presenter
from Streamer import Streamer


def streamer_worker(path: str, produce_queue, kill_event):
    streamer = Streamer(path)
    for frame in streamer.yield_frames():
        if kill_event.is_set():
            break
        produce_queue.put(frame)
    # notifies for the end of the queue
    produce_queue.put(None)


def detector_worker(consume_queue, produce_queue, kill_event):
    detector = Detector()
    while not kill_event.is_set():
        frame = consume_queue.get(timeout=1)
        if frame is None:
            break

        original_frame, cnts = detector.detect(frame)
        produce_queue.put((original_frame, cnts))
    # notifies for the end of the queue
    produce_queue.put(None)


def presenter_worker(consume_queue, fps: float, kill_event, use_blur):
    presenter = Presenter(use_blurring=use_blur)
    frame_required_duration_ms = 1.0 / fps
    video_actual_start_time = time.time()
    frames_displayed = 0
    while not kill_event.is_set():
        data = consume_queue.get(timeout=1)
        if data is None:
            break

        image, cnts = data
        presenter.draw_and_show(image, cnts)

        frames_displayed += 1

        sleep_time_ms = get_next_frame_sleeping_time(frame_required_duration_ms, frames_displayed,
                                                     video_actual_start_time)

        # waits until the next frame should be presented as calculated above
        if cv2.waitKey(max(1, sleep_time_ms)) & 0xFF == ord('q'):
            break
    _end_video(kill_event)


def get_next_frame_sleeping_time(frame_required_duration_ms: float, frames_displayed: int,
                                 video_actual_start_time: float) -> int:
    target_time_present = video_actual_start_time + (frames_displayed * frame_required_duration_ms)
    current_time = time.time()
    sleep_time_ms = int((target_time_present - current_time) * 1000)
    return sleep_time_ms


def _end_video(kill_event):
    cv2.destroyAllWindows()
    kill_event.set()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Multi-process Video Motion Detector")

    parser.add_argument("path", help="The full path to the video file")
    parser.add_argument("use_blur", help="set Y/N whether to use blurring")

    # 3. Parse the arguments from the CMD
    args = parser.parse_args()
    video_path = args.path
    use_blur = args.use_blur is not None and args.use_blur.lower() == "y"

    # 4. Check if the file actually exists before starting processes
    if not os.path.exists(video_path):
        print(f"Error: The file '{video_path}' does not exist.")
        exit(1)
    kill_procs = mp.Event()
    # common queues to communication between processes
    frames_queue = mp.Queue(maxsize=30)  # prevent streamer to overload and filling up the RAM
    frames_with_detections_queue = mp.Queue(maxsize=30)  # prevent the detector to overload and filling up the RAM

    video_fps: float = Streamer.get_video_fps(video_path)
    # defines the processes
    streamer_proc = mp.Process(target=streamer_worker, args=(video_path, frames_queue, kill_procs))
    detector_proc = mp.Process(target=detector_worker, args=(frames_queue, frames_with_detections_queue, kill_procs))
    presenter_proc = mp.Process(target=presenter_worker, args=(frames_with_detections_queue, video_fps, kill_procs, use_blur))

    streamer_proc.start()
    detector_proc.start()
    presenter_proc.start()

    presenter_proc.join()
    kill_procs.set()
    streamer_proc.terminate()
    detector_proc.terminate()

    # cleaning memory
    streamer_proc.join()
    detector_proc.join()
    print("killed all processes gracefully")
