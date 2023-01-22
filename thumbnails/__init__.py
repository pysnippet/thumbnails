from .thumbnail import JSONThumbnail
from .thumbnail import Thumbnail
from .thumbnail import ThumbnailFactory
from .thumbnail import VTTThumbnail
from .thumbnail import register_thumbnail
from .video import Video

DEFAULT_BASE = ""
DEFAULT_SKIP = False
DEFAULT_OUTPUT = "."
DEFAULT_FORMAT = "vtt"
DEFAULT_COMPRESS = 1.0
DEFAULT_INTERVAL = 1.0

__version__ = "v1.0"
__all__ = (
    "register_thumbnail",
    "ThumbnailFactory",
    "JSONThumbnail",
    "VTTThumbnail",
    "Thumbnail",
    "Video",
)
