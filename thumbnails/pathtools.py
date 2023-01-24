import functools
import os
from distutils.dir_util import create_tree


def listdir(directory):
    """Lists all files in the given directory with absolute paths."""
    for basedir, _, files in os.walk(directory):
        for file in filter(os.path.isfile, files):
            yield os.path.abspath(os.path.join(basedir, file))


@functools.cache
def metadata_path(path, out, fmt):
    """Calculates the thumbnail metadata output path."""
    out = os.path.abspath(out or os.path.dirname(path))
    filename = os.path.splitext(os.path.basename(path))[0]
    return os.path.join(out, "%s.%s" % (filename, fmt))


def ensure_tree(basedir, files, *args, **kwargs):
    """Ensures the existence of basedir and returns."""
    create_tree(basedir, files, *args, **kwargs)
    return basedir
