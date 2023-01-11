import concurrent.futures

from thumbnails import Thumbnails

# Read from the program arguments.
compress = 1
interval = .5
basepath = "/stc/"

files = ["valerian-1080p.avi", "valerian-1080p.mkv", "valerian-1080p.mov", "valerian-1080p.mp4",
         "valerian-1080p.webm", "valerian-1080p.wmv", "valerian-1080p.mpeg", "valerian-1080p.mpg", "valerian-1080p.ogv"]


def worker(video):
    video.compress = compress
    video.interval = interval
    video.basepath = basepath
    video.extract_frames()
    video.join_frames()
    video.to_vtt()


def main():
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(worker, map(Thumbnails, files))


if __name__ == "__main__":
    main()
