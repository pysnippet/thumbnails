import json
import os
import pathlib
from abc import ABCMeta
from abc import abstractmethod
from datetime import timedelta
from distutils.dir_util import copy_tree
from distutils.dir_util import remove_tree

from PIL import Image

from .pathtools import ensure_tree
from .pathtools import extract_name
from .pathtools import metadata_path
from .progress import Progress


def register_thumbnail(typename):
    """Register a new type of thumbnail generator into the factory."""

    def _register_factory(cls):
        if not issubclass(cls, Thumbnail):
            raise ValueError("%s should be a Thumbnail." % cls.__name__)

        cls.extension = typename
        ThumbnailFactory.thumbnails[typename] = cls
        return cls

    return _register_factory


class ThumbnailExistsError(Exception):
    """The thumbnail already exists."""


class Thumbnail(metaclass=ABCMeta):
    """Any thumbnail describing format should implement the base Thumbnail."""

    extension = None

    def __init__(self, video, base, skip, output):
        self.video = video
        self.base = base
        self.skip = skip
        self.output = output
        self.thumbnail_dir = self.calc_thumbnail_dir()
        self.metadata_path = self._get_metadata_path()
        self._perform_skip()

        with Progress("Extracting the frames by the given interval"):
            self.extract_frames()

    def _get_metadata_path(self):
        """Initiates the name of the thumbnail metadata file."""
        return metadata_path(self.filepath, self.output, self.extension)

    def _perform_skip(self):
        """Checks the file existence and decide whether to skip or not."""
        if os.path.exists(self.metadata_path) and self.skip:
            raise ThumbnailExistsError
        ensure_tree(self.metadata_path)

    def __getattr__(self, item):
        """Delegates all other attributes to the video."""
        return getattr(self.video, item)

    @abstractmethod
    def calc_thumbnail_dir(self):
        """Calculates and returns the thumbnail's output directory."""

    @abstractmethod
    def prepare_frames(self):
        """Prepares the thumbnail frames before generating the output."""

    @abstractmethod
    def generate(self):
        """Generates the thumbnail metadata for the given video."""


class ThumbnailFactory:
    """A factory for creating a thumbnail for a particular format."""

    thumbnails = {}

    @classmethod
    def create_thumbnail(cls, typename, *args, **kwargs) -> Thumbnail:
        """Create a Thumbnail instance by the given typename."""
        try:
            return cls.thumbnails[typename](*args, **kwargs)
        except KeyError:
            raise ValueError("The thumbnail type '%s' is not registered." % typename)


@register_thumbnail("vtt")
class ThumbnailVTT(Thumbnail):
    """Implements the methods for generating thumbnails in the WebVTT format."""

    def calc_thumbnail_dir(self):
        return ensure_tree(self.output or os.path.dirname(self.filepath), True)

    def prepare_frames(self):
        thumbnails = self.thumbnails(True)
        master = Image.new(mode="RGBA", size=next(thumbnails))
        master_path = os.path.join(self.thumbnail_dir, extract_name(self.filepath) + ".png")

        with Progress("Preprocessing the frames before merging") as progress:
            for frame, *_, x, y in thumbnails:
                offset = extract_name(frame).replace("-", ":").split(".")[0]
                progress.update("Processing [bold]%s[/bold] frame" % offset)
                with Image.open(frame) as image:
                    master.paste(image, (x, y))

        with Progress("Saving the result at '%s'" % master_path):
            master.save(master_path)

    def generate(self):
        def format_time(secs):
            delta = timedelta(seconds=secs)
            return ("0%s.000" % delta)[:12]

        metadata = ["WEBVTT\n\n"]
        prefix = self.base if self.base is not None else os.path.relpath(self.thumbnail_dir)
        route = os.path.join(prefix, extract_name(self.filepath) + ".png")
        route = pathlib.Path(route).as_posix()

        with Progress("Saving thumbnail metadata at '%s'" % self.metadata_path):
            for _, start, end, x, y in self.thumbnails():
                thumbnail_data = "%s --> %s\n%s#xywh=%d,%d,%d,%d\n\n" % (
                    format_time(start), format_time(end),
                    route, x, y, self.width, self.height,
                )
                metadata.append(thumbnail_data)

        with open(self.metadata_path, "w") as fp:
            fp.writelines(metadata)

        self.tempdir.cleanup()


@register_thumbnail("json")
class ThumbnailJSON(Thumbnail):
    """Implements the methods for generating thumbnails in the JSON format."""

    def calc_thumbnail_dir(self):
        basedir = os.path.abspath(self.output or os.path.dirname(self.filepath))
        return ensure_tree(os.path.join(basedir, extract_name(self.filepath)), True)

    def prepare_frames(self):
        with Progress("Copying the frames to the output directory"):
            if os.path.exists(self.thumbnail_dir):
                remove_tree(self.thumbnail_dir)
            copy_tree(self.tempdir.name, self.thumbnail_dir)

    def generate(self):
        metadata = {}

        with Progress("Saving thumbnail metadata at '%s'" % self.metadata_path):
            for frame, start, *_ in self.thumbnails():
                frame = os.path.join(self.thumbnail_dir, os.path.basename(frame))
                base = os.path.join(self.base or "", os.path.basename(self.thumbnail_dir))
                prefix = base if self.base is not None else os.path.relpath(self.thumbnail_dir)
                route = os.path.join(prefix, os.path.basename(frame))
                route = pathlib.Path(route).as_posix()
                thumbnail_data = {
                    "src": route,
                    "width": "%spx" % self.width,
                }
                metadata[int(start)] = thumbnail_data

        with open(self.metadata_path, "w") as fp:
            json.dump(metadata, fp, indent=2)

        self.tempdir.cleanup()
