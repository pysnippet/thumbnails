class ThumbnailFormat:
    """The interface of the thumbnails' final output format generator."""

    extension = None

    def __init__(self, video):
        self.video = video

    def __getattr__(self, item):
        """Delegate all other attributes to the video."""
        return getattr(self.video, item)

    @property
    def output_format(self):
        return "%s.%s" % (self.filename, self.extension)

    def prepare_thumbnails(self):
        """Prepare the thumbnails before generating the output."""
        raise NotImplementedError

    def generate(self):
        """Generate the thumbnails for the given video."""
        raise NotImplementedError


class FormatterFactory:
    """A factory for creating thumbnail formatter."""

    thumbnails = {}

    @classmethod
    def create_formatter(cls, typename, *args, **kwargs) -> ThumbnailFormat:
        """Create a new thumbnail formatter by the given typename."""
        try:
            return cls.thumbnails[typename](*args, **kwargs)
        except KeyError:
            raise ValueError("Thumbnail format '%s' is not supported." % typename)
