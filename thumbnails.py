import concurrent.futures

from ffmpeg import FFMpeg

# Read from the program arguments.
compress = 1
interval = 20

files = ["valerian-1080p.avi", "valerian-1080p.mkv", "valerian-1080p.mov", "valerian-1080p.mp4",
         "valerian-1080p.webm", "valerian-1080p.wmv", "valerian-1080p.mpeg", "valerian-1080p.mpg", "valerian-1080p.ogv"]


def worker(video):
    video.set_compress(compress)
    video.set_interval(interval)
    video.extract_frames()
    video.join_frames()


def main():
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(worker, map(FFMpeg, files))


if __name__ == "__main__":
    main()
