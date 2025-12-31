from Streamer import Streamer
from Detector import Detector

if __name__ == '__main__':
    streamer = Streamer(r'C:\Users\97250\Desktop\ido\axonVIsion\code\People - 6387.mp4')
    detector = Detector()

    # yield_frames() returns the generator once
    images = streamer.yield_frames()

    for frame in images:
        original_frame, cnts = detector.detect(frame)
        print(f"Detected {len(cnts)} moving objects")


