from abc import ABCMeta, abstractmethod


class FileFormatter(metaclass=ABCMeta):
    """Any thumbnail describing format should implement the base Formatter."""

    extension = None

    def __init__(self, video):
        self.video = video

    def __getattr__(self, item):
        """Delegate all other attributes to the video."""
        return getattr(self.video, item)

    @property
    def thumbnail_file(self):
        """Return the name of the thumbnail file."""
        return "%s.%s" % (self.filename, self.extension)

    @abstractmethod
    def prepare_thumbnails(self):
        """Prepare the thumbnails before generating the output."""

    @abstractmethod
    def generate(self):
        """Generate the thumbnails for the given video."""


class FormatterFactory:
    """A factory for creating thumbnail formatter."""

    thumbnails = {}

    @classmethod
    def create_formatter(cls, typename, *args, **kwargs) -> FileFormatter:
        """Create a new thumbnail formatter by the given typename."""
        try:
            return cls.thumbnails[typename](*args, **kwargs)
        except KeyError:
            raise ValueError("The formatter type '%s' is not registered." % typename)
