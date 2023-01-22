import concurrent.futures
import functools
import os

import click

from . import ThumbnailFactory
from . import Video
from .cli import cli


def worker(video, base, format_):
    """Generate thumbnails for a single video."""
    video.extract_frames()
    thumbnail = ThumbnailFactory.create_thumbnail(format_, video, base)
    thumbnail.prepare_frames()
    thumbnail.generate()


@cli
def main(compress, interval, base, inputs, output, skip, **kwargs):
    """TODO: This section will be completed after fixing the issue #26."""
    if not any([
        all(map(os.path.isfile, inputs)),
        all(map(os.path.isdir, inputs)),
    ]):
        exit("The inputs must be all files or all directories.")

    if not skip and any(map(os.path.exists, inputs)):
        skip = click.confirm("Are you agree to override?", default=False)

    click.echo("skip %s" % skip)
    click.echo("output %s" % output)

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
                format_=format_,
            ),
            videos,
        )


if __name__ == "__main__":
    main()
