import asyncio
import concurrent.futures
import math

from PIL import Image

from ffmpeg import Ffmpeg

width, height = 300, 200
interval = 20
columns = 3

files = ["valerian-1080p.avi", "valerian-1080p.mkv", "valerian-1080p.mov", "valerian-1080p.mp4",
         "valerian-1080p.webm", "valerian-1080p.wmv", "valerian-1080p.mpeg", "valerian-1080p.mpg"]


def worker(video):
    line, column = 0, 0
    frames_count = len(range(0, int(video.duration), interval))
    master_width = width * columns
    master_height = height * int(math.ceil(float(frames_count) / columns))

    try:
        master = Image.new(mode="RGBA", size=(master_width, master_height))
    except IOError:
        master = Image.new(mode="RGB", size=(master_width, master_height))

    for moment in range(0, int(video.duration), interval):
        x, y = width * column, height * line
        image = video.get_frame_buffer(moment)
        image = image.resize((width, height), Image.ANTIALIAS)
        master.paste(image, (x, y))

        column += 1

        if column == columns:
            line += 1
            column = 0

    master.save(video.filename + ".png")


async def main():
    fps = [Ffmpeg(fp) for fp in files]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(worker, fps)

    for fp in fps:
        fp.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
