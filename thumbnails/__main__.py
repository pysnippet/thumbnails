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
from . import FormatterFactory
from . import Thumbnails
from . import __version__


def worker(video, format_):
    """Generate thumbnails for a single video."""
    video.extract_frames()
    formatter = FormatterFactory.create_formatter(format_, video)
    formatter.prepare_thumbnails()
    formatter.generate()


class _ThumbnailsCLI(click.Command):
    """This class overrides the usages section of the help message."""

    def format_usage(self, ctx, formatter):
        usages = (
            "[OPTIONS] INPUT_DIR",
            "[OPTIONS] INPUT_FILE",
            "[OPTIONS] INPUT_FILES...",
        )
        formatter.write_usage(ctx.command_path, "\n\t\t\t".join(usages), prefix="Usages: ")


# This defines a set of supported values for the particular option of the CLI.
_type = click.Choice(FormatterFactory.thumbnails.keys(), case_sensitive=False)


@click.command(cls=_ThumbnailsCLI)
@click.option("--compress", "-C", default=DEFAULT_COMPRESS, help="The image scale coefficient. A number from 0 to 1.")
@click.option("--interval", "-I", default=DEFAULT_INTERVAL, help="The interval between neighbor thumbnails in seconds.")
@click.option("--base", "-B", default=DEFAULT_BASE, help="The prefix of the thumbnails path can be customized.")
@click.option("--skip", "-S", default=DEFAULT_SKIP, help="Skip the existing thumbnails. Default is False.")
@click.option("--output", "-O", default=DEFAULT_OUTPUT, type=click.Path(), help="The output directory. Default is the current directory.")
@click.option("--format", "-F", default=DEFAULT_FORMAT, type=_type, help="Output format. Default is %s." % DEFAULT_FORMAT)
@click.argument("inputs", required=True, type=click.Path(), nargs=-1)
@click.version_option(__version__, "-V", "--version")
@click.help_option("-h", "--help")
def thumbnails_cli(compress, interval, base, inputs, output, skip, **kwargs):
    """TODO: This section will be completed after fixing the issue #26."""
    format_ = kwargs.pop("format")
    output_is_directory = all((len(inputs) > 1, *map(os.path.isfile, inputs))) or os.path.isdir(inputs[0])

    with concurrent.futures.ThreadPoolExecutor() as executor:
        videos = executor.map(
            functools.partial(
                Thumbnails,
                compress=compress,
                interval=interval,
                basepath=base
            ),
            inputs,
        )

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(functools.partial(worker, format_=format_), videos)


if __name__ == "__main__":
    thumbnails_cli()
