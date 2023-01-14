class ThumbnailFormat:
    def generate(self, video):
        """Generate the thumbnails for the given video."""
        raise NotImplementedError


class ThumbnailFactory:
    thumbnails = {}

    @classmethod
    def get_thumbnail(cls, typename) -> ThumbnailFormat:
        try:
            return cls.thumbnails[typename]()
        except KeyError:
            raise ValueError("Thumbnail type '%s' is not supported." % typename)
