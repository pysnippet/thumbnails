import functools

import click

from . import ThumbnailFactory
from . import __version__

DEFAULT_BASE = ""
DEFAULT_SKIP = False
DEFAULT_OUTPUT = "."
DEFAULT_FORMAT = "vtt"
DEFAULT_COMPRESS = 1.0
DEFAULT_INTERVAL = 1.0

# This defines a set of supported values for the particular option of the CLI.
_type = click.Choice(ThumbnailFactory.thumbnails.keys(), case_sensitive=False)


def cli(func):
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
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
