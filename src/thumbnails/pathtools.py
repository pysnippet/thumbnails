import os
from distutils.dir_util import create_tree


def listdir(directory):
    """Lists all files in the given directory with absolute paths."""
    for basedir, _, files in os.walk(directory):
        files = [os.path.join(basedir, file) for file in files]
        for filepath in filter(os.path.isfile, files):
            yield os.path.abspath(filepath)


def metadata_path(path, out, fmt):
    """Calculates the thumbnail metadata output path."""
    out = os.path.abspath(out or os.path.dirname(path))
    return os.path.join(out, "%s.%s" % (extract_name(path), fmt))


def extract_name(path):
    """Extracts the name of the file from the path."""
    return os.path.splitext(os.path.basename(path))[0]


def ensure_tree(basedir, isdir=False, *args, **kwargs):
    """Ensures the existence of basedir and returns."""
    basedir, file = os.path.abspath(basedir), ""
    if not isdir:
        basedir, file = os.path.split(basedir)
    create_tree(basedir, [file], *args, **kwargs)
    return basedir
