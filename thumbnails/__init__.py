from .formatter import ThumbnailFactory
from .formatter import ThumbnailFormat
from .thumbnails import Thumbnails

DEFAULT_COMPRESS = 1.
DEFAULT_INTERVAL = 1.
DEFAULT_BASEPATH = ""


def register_format(typename):
    def _registrator(cls: ThumbnailFormat):
        ThumbnailFactory.thumbnails[typename] = cls

    return _registrator


@register_format("vtt")
class VTT(ThumbnailFormat):
    def generate(self, video: Thumbnails):
        return "vtt"


@register_format("json")
class JSON(ThumbnailFormat):
    def generate(self, video: Thumbnails):
        return "json"


__version__ = "v1.0"
__all__ = (Thumbnails,)
