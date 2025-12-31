import cv2

from Streamer import Streamer
from Detector import Detector
from Presenter import Presenter

if __name__ == '__main__':
    streamer = Streamer(r'C:\Users\97250\Desktop\ido\axonVIsion\code\People - 6387.mp4')
    detector = Detector()
    presenter = Presenter()

    images = streamer.yield_frames()

    for frame in images:
        original_frame, cnts = detector.detect(frame)
        presenter.draw_and_show(original_frame, cnts)

        print(f"Detected {len(cnts)} moving objects")

        # Windows os adaptions
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


