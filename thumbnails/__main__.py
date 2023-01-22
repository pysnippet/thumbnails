import concurrent.futures
import functools
import os

import click

from . import DEFAULT_BASE
from . import DEFAULT_COMPRESS
from . import DEFAULT_FORMAT
from . import DEFAULT_INTERVAL
from . import DEFAULT_OUTPUT
from . import DEFAULT_SKIP
from . import ThumbnailFactory
from . import Video
from . import __version__


def worker(video, base, format_):
    """Generate thumbnails for a single video."""
    video.extract_frames()
    thumbnail = ThumbnailFactory.create_thumbnail(format_, video, base)
    thumbnail.prepare_frames()
    thumbnail.generate()


# This defines a set of supported values for the particular option of the CLI.
_type = click.Choice(ThumbnailFactory.thumbnails.keys(), case_sensitive=False)


@click.command()
@click.option("--compress", "-C", default=DEFAULT_COMPRESS, help="The image scale coefficient. A number from 0 to 1.")
@click.option("--interval", "-I", default=DEFAULT_INTERVAL, help="The interval between neighbor thumbnails in seconds.")
@click.option("--base", "-B", default=DEFAULT_BASE, help="The prefix of the thumbnails path can be customized.")
@click.option("--skip", "-S", default=DEFAULT_SKIP, help="Skip the existing thumbnails. Default is not set.")
@click.option("--output", "-O", default=DEFAULT_OUTPUT, type=click.Path(), help="The output directory. Default is the current directory.")
@click.option("--format", "-F", default=DEFAULT_FORMAT, type=_type, help="Output format. Default is %s." % DEFAULT_FORMAT)
@click.argument("inputs", required=True, type=click.Path(), nargs=-1)
@click.version_option(__version__, "-V", "--version")
@click.help_option("-h", "--help")
def thumbnails_cli(compress, interval, base, inputs, output, skip, **kwargs):
    """TODO: This section will be completed after fixing the issue #26."""
    if not any([
        all(map(os.path.isfile, inputs)),
        all(map(os.path.isdir, inputs)),
    ]):
        exit("The inputs must be all files or all directories.")

    if not skip and any(map(os.path.exists, inputs)):
        skip = click.confirm("Are you agree to override?", default=False)

    print(skip)
    return

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
    thumbnails_cli()
