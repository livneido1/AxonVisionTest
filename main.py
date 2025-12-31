from Streamer import Streamer

if __name__ == '__main__':
    streamer = Streamer(r'C:\Users\97250\Desktop\ido\axonVIsion\code\People - 6387.mp4')
    while True:
        image = streamer.yield_images()
        x = 3
