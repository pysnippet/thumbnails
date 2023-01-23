import functools

import click

from . import ThumbnailFactory
from . import __version__

# Default values of the particular option of the CLI.
DEFAULT_BASE = ""
DEFAULT_SKIP = False
DEFAULT_OUTPUT = None
DEFAULT_FORMAT = "vtt"
DEFAULT_COMPRESS = 1.0
DEFAULT_INTERVAL = 1.0

# Help messages of the particular option of the CLI.
HELP_BASE = "The prefix of the thumbnails path can be customized."
HELP_SKIP = "Skip the existing thumbnails. Default is not set."
HELP_OUTPUT = "The output directory. Default is the current directory."
HELP_FORMAT = "Output format. Default is %s." % DEFAULT_FORMAT
HELP_COMPRESS = "The image scale coefficient. A number from 0 to 1."
HELP_INTERVAL = "The interval between neighbor thumbnails in seconds."

# This defines a choice of supported values for the '--format' option of the CLI.
format_choice = click.Choice(ThumbnailFactory.thumbnails.keys(), case_sensitive=False)


def cli(func):
    @click.command()
    @click.option("--compress", "-C", default=DEFAULT_COMPRESS, help=HELP_COMPRESS)
    @click.option("--interval", "-I", default=DEFAULT_INTERVAL, help=HELP_INTERVAL)
    @click.option("--base", "-B", default=DEFAULT_BASE, help=HELP_BASE)
    @click.option("--skip", "-S", default=DEFAULT_SKIP, help=HELP_SKIP, is_flag=True)
    @click.option("--output", "-O", default=DEFAULT_OUTPUT, type=click.Path(), help=HELP_OUTPUT)
    @click.option("--format", "-F", default=DEFAULT_FORMAT, type=format_choice, help=HELP_FORMAT)
    @click.argument("inputs", required=True, type=click.Path(), nargs=-1)
    @click.version_option(__version__, "-V", "--version")
    @click.help_option("-h", "--help")
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
