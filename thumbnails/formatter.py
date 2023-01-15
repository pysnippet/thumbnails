class ThumbnailFormat:
    extension = None

    def __init__(self, video):
        self.video = video

    def __getattr__(self, item):
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


class ThumbnailFactory:
    thumbnails = {}

    @classmethod
    def get_thumbnail(cls, typename, *args, **kwargs) -> ThumbnailFormat:
        try:
            return cls.thumbnails[typename](*args, **kwargs)
        except KeyError:
            raise ValueError("Thumbnail type '%s' is not supported." % typename)
