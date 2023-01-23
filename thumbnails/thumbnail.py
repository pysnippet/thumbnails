import functools
import json
import os
from abc import ABCMeta
from abc import abstractmethod
from datetime import timedelta
from distutils.dir_util import copy_tree
from distutils.dir_util import create_tree
from distutils.dir_util import remove_tree

from PIL import Image


def register_thumbnail(typename):
    """Register a new thumbnail formatter to the factory."""

    def _register_factory(cls):
        if not issubclass(cls, Thumbnail):
            raise ValueError("The formatter must implement the Thumbnail interface.")

        cls.extension = typename
        ThumbnailFactory.thumbnails[typename] = cls
        return cls

    return _register_factory


class ThumbnailExistsError(Exception):
    """The thumbnail already exists."""


class Thumbnail(metaclass=ABCMeta):
    """Any thumbnail describing format should implement the base Formatter."""

    extension = None

    def __init__(self, video, base, skip, output):
        self.video = video
        self.base = base
        self.skip = skip
        self.output = output
        self._perform_skip()
        self.extract_frames()

    def _perform_skip(self):
        """Raises ThumbnailExistsError to skip."""
        if os.path.exists(self.get_metadata_path()) and self.skip:
            raise ThumbnailExistsError
        basedir, file = os.path.split(self.get_metadata_path())
        create_tree(basedir, [file])

    def __getattr__(self, item):
        """Delegate all other attributes to the video."""
        return getattr(self.video, item)

    def get_metadata_path(self):
        """Return the name of the thumbnail file."""
        return self.metadata_path(self.filepath, self.output, self.extension)

    @staticmethod
    @functools.cache
    def metadata_path(path, out, fmt):
        """Calculate the thumbnail metadata output path."""
        out = os.path.abspath(out or os.path.dirname(path))
        filename = os.path.splitext(os.path.basename(path))[0]
        return os.path.join(out, "%s.%s" % (filename, fmt))

    @abstractmethod
    def thumbnail_dir(self):
        """Creates and returns the thumbnail's output directory."""

    @abstractmethod
    def prepare_frames(self):
        """Prepare the thumbnails before generating the output."""

    @abstractmethod
    def generate(self):
        """Generate the thumbnails for the given video."""


class ThumbnailFactory:
    """A factory for creating thumbnail formatter."""

    thumbnails = {}

    @classmethod
    def create_thumbnail(cls, typename, *args, **kwargs) -> Thumbnail:
        """Create a new thumbnail formatter by the given typename."""
        try:
            return cls.thumbnails[typename](*args, **kwargs)
        except KeyError:
            raise ValueError("The formatter type '%s' is not registered." % typename)


@register_thumbnail("vtt")
class ThumbnailVTT(Thumbnail):
    """Implements the methods for generating thumbnails in the WebVTT format."""

    def thumbnail_dir(self):
        basedir = self.output or os.path.dirname(self.filepath)
        create_tree(os.path.abspath(basedir), [self.filepath])
        return os.path.abspath(basedir)

    def prepare_frames(self):
        thumbnails = self.thumbnails(True)
        master = Image.new(mode="RGBA", size=next(thumbnails))
        master_name = os.path.splitext(os.path.basename(self.filepath))[0]
        master_path = os.path.join(self.thumbnail_dir(), master_name + ".png")

        for frame, *_, x, y in self.thumbnails():
            with Image.open(frame) as image:
                image = image.resize((self.width, self.height), Image.ANTIALIAS)
                master.paste(image, (x, y))

        master.save(master_path)
        self.tempdir.cleanup()

    def generate(self):
        def format_time(secs):
            delta = timedelta(seconds=secs)
            return ("0%s.000" % delta)[:12]

        metadata = ["WEBVTT\n\n"]
        prefix = self.base or os.path.relpath(self.thumbnail_dir())
        route = os.path.join(prefix, os.path.basename(self.filepath))

        for _, start, end, x, y in self.thumbnails():
            thumbnail_data = "%s --> %s\n%s#xywh=%d,%d,%d,%d\n\n" % (
                format_time(start), format_time(end),
                route, x, y, self.width, self.height,
            )
            metadata.append(thumbnail_data)

        with open(self.get_metadata_path(), "w") as fp:
            fp.writelines(metadata)


@register_thumbnail("json")
class ThumbnailJSON(Thumbnail):
    """Implements the methods for generating thumbnails in the JSON format."""

    def thumbnail_dir(self):
        basedir = os.path.abspath(self.output or os.path.dirname(self.filepath))
        subdir = os.path.splitext(os.path.basename(self.filepath))[0]
        basedir = os.path.join(basedir, subdir)
        create_tree(basedir, [self.filepath])
        return basedir

    def prepare_frames(self):
        thumbnail_dir = self.thumbnail_dir()
        if os.path.exists(thumbnail_dir):
            remove_tree(thumbnail_dir)
        copy_tree(self.tempdir.name, thumbnail_dir)
        self.tempdir.cleanup()

    def generate(self):
        metadata = {}

        for frame, start, *_ in self.thumbnails():
            frame = os.path.join(self.thumbnail_dir(), os.path.basename(frame))
            with Image.open(frame) as image:
                image.resize((self.width, self.height), Image.ANTIALIAS).save(frame)
                thumbnail_data = {
                    "src": self.base + frame,
                    "width": "%spx" % self.width,
                }
                metadata[int(start)] = thumbnail_data

        with open(self.get_metadata_path(), "w") as fp:
            json.dump(metadata, fp, indent=2)
