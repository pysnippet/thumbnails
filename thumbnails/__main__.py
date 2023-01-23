import concurrent.futures
import functools
import itertools
import os

import click

from . import Thumbnail
from . import ThumbnailExistsError
from . import ThumbnailFactory
from . import Video
from .cli import cli


def worker(video, fmt, base, skip, output):
    """Generate thumbnails for a single video."""
    try:
        thumbnail = ThumbnailFactory.create_thumbnail(fmt, video, base, skip, output)
    except ThumbnailExistsError:
        return print("Skipping '%s'" % video.filepath)
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
        inputs = set(map(os.path.abspath, inputs))
    elif all(map(os.path.isdir, inputs)):
        inputs = set(itertools.chain(*map(listdir, inputs)))
    else:
        exit("Inputs must be all files or all directories.")

    fmt = kwargs.pop("format")
    inputs = dict(zip(map(lambda i: Thumbnail.metadata_path(i, output, fmt), inputs), inputs))

    if not skip and any(map(os.path.exists, inputs.keys())):
        skip = not click.confirm("Do you want to overwrite already existing files?")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        videos = executor.map(
            functools.partial(
                Video,
                compress=compress,
                interval=interval,
            ),
            inputs.values(),
        )

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(
            functools.partial(
                worker,
                fmt=fmt,
                base=base,
                skip=skip,
                output=output,
            ),
            videos,
        )


if __name__ == "__main__":
    main()
