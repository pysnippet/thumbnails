import concurrent.futures
import functools
import os

import click

from . import DEFAULT_AS
from . import DEFAULT_BASEPATH
from . import DEFAULT_COMPRESS
from . import DEFAULT_INTERVAL
from . import ThumbnailFactory
from . import Thumbnails
from . import __version__


def worker(video, as_):
    print(ThumbnailFactory.get_thumbnail(as_).generate(video))
    # video.extract_frames()
    # video.join_frames()
    # video.to_vtt()


class _ThumbnailsCLI(click.Command):
    def format_usage(self, ctx, formatter):
        usages = (
            "[OPTIONS] INPUT_DIR OUTPUT_DIR",
            "[OPTIONS] INPUT_FILE OUTPUT_FILE",
            "[OPTIONS] INPUT_FILES... OUTPUT_DIR",
        )
        formatter.write_usage(ctx.command_path, "\n\t\t\t".join(usages), prefix="Usages: ")


@click.command(cls=_ThumbnailsCLI)
@click.option("--as", "-F", default=DEFAULT_AS, help="Output format. Default is %s." % DEFAULT_AS,
              type=click.Choice(ThumbnailFactory.thumbnails.keys(), case_sensitive=False))
@click.option("--compress", "-C", default=DEFAULT_COMPRESS, help="The image scale coefficient. A number from 0 to 1.")
@click.option("--interval", "-I", default=DEFAULT_INTERVAL, help="The interval between neighbor thumbnails in seconds.")
@click.option("--basepath", "-B", default=DEFAULT_BASEPATH, help="The prefix of the thumbnails path can be customized.")
@click.argument("inputs", required=True, type=click.Path(), nargs=-1)
@click.argument("output", required=True, type=click.Path(), nargs=1)
@click.version_option(__version__)
def thumbnails_cli(compress, interval, basepath, inputs, output, **kwargs):
    """TODO: Add more description about particular usages."""
    as_ = kwargs.pop("as")
    output_is_directory = all((len(inputs) > 1, *map(os.path.isfile, inputs))) or os.path.isdir(inputs[0])

    with concurrent.futures.ThreadPoolExecutor() as executor:
        videos = executor.map(
            functools.partial(
                Thumbnails,
                compress=compress,
                interval=interval,
                basepath=basepath
            ),
            inputs,
        )

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(functools.partial(worker, as_=as_), videos)


# @click.confirmation_option("--overwrite", "-y", prompt="Are you sure you want to overwrite the existing output files?")
# def overwrite():
#     print("overwritten")


if __name__ == "__main__":
    thumbnails_cli()
