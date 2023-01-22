import concurrent.futures
import functools
import os

from . import ThumbnailExistsError
from . import ThumbnailFactory
from . import Video
from .cli import cli


def worker(video, base, skip, output, typename):
    """Generate thumbnails for a single video."""
    try:
        thumbnail = ThumbnailFactory.create_thumbnail(typename, video, base, skip, output)
    except ThumbnailExistsError:
        return print("Skipping '%s'" % video.filename)
    thumbnail.prepare_frames()
    thumbnail.generate()


@cli
def main(compress=None, interval=None, base=None, inputs=None, output=None, skip=None, **kwargs):
    """TODO: This section will be completed after fixing the issue #26."""
    if not any([
        all(map(os.path.isfile, inputs)),
        all(map(os.path.isdir, inputs)),
    ]):
        exit("The inputs must be all files or all directories.")

    # in case of inputs are directories, convert inputs to a list of files

    format_ = kwargs.pop("format")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        videos = executor.map(
            functools.partial(
                Video,
                compress=compress,
                interval=interval,
            ),
            inputs,
        )

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(
            functools.partial(
                worker,
                base=base,
                skip=skip,
                output=output,
                typename=format_,
            ),
            videos,
        )


if __name__ == "__main__":
    main()
