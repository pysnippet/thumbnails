import concurrent.futures
import functools
import itertools
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

    def listdir(directory):
        """Lists all files in the given directory with absolute paths."""
        for basedir, _, files in os.walk(directory):
            for file in filter(os.path.isfile, files):
                yield os.path.abspath(os.path.join(basedir, file))

    if all(map(os.path.isfile, inputs)):
        inputs = tuple(map(os.path.abspath, inputs))
    elif all(map(os.path.isdir, inputs)):
        inputs = tuple(itertools.chain(*map(listdir, inputs)))
    else:
        exit("Inputs must be all files or all directories.")

    # TODO: Add validation and ask for override.

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
