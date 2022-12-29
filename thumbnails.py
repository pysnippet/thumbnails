import asyncio
import concurrent.futures
import math

from PIL import Image

from ffmpeg import FFMpeg

width, height = 300, 200
interval = 20
columns = 3

files = ["valerian-1080p.avi", "valerian-1080p.mkv", "valerian-1080p.mov", "valerian-1080p.mp4",
         "valerian-1080p.webm", "valerian-1080p.wmv", "valerian-1080p.mpeg", "valerian-1080p.mpg", "valerian-1080p.ogv"]


def worker(video):
    line, column = 0, 0
    frames_count = len(range(0, int(video.duration), interval))
    master_width = width * columns
    master_height = height * int(math.ceil(float(frames_count) / columns))

    try:
        master = Image.new(mode="RGBA", size=(master_width, master_height))
    except IOError:
        master = Image.new(mode="RGB", size=(master_width, master_height))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        frames = executor.map(video.get_frame, range(0, int(video.duration), interval))

    for frame in frames:
        x, y = width * column, height * line
        image = video.frame_to_buffer(frame)
        image = image.resize((width, height), Image.ANTIALIAS)
        master.paste(image, (x, y))

        column += 1

        if column == columns:
            line += 1
            column = 0

    master.save(video.filename + ".png")


async def main():
    fps = [FFMpeg(fp) for fp in files]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(worker, fps)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
