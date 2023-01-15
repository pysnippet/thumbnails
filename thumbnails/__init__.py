from datetime import timedelta

from PIL import Image

from .formatter import ThumbnailFactory
from .formatter import ThumbnailFormat
from .thumbnails import Thumbnails
from .thumbnails import arange

DEFAULT_AS = "vtt"
DEFAULT_COMPRESS = 1.
DEFAULT_INTERVAL = 1.
DEFAULT_BASEPATH = ""


def register_format(typename):
    def _registrator(cls: ThumbnailFormat):
        cls.extension = typename
        ThumbnailFactory.thumbnails[typename] = cls

    return _registrator


@register_format("vtt")
class VTT(ThumbnailFormat):
    def __init__(self, video):
        super().__init__(video)
        self._master_name = self.filename + ".png"

    def prepare_thumbnails(self):
        _thumbnails = self.video.thumbnails(True)
        master = Image.new(mode="RGBA", size=next(_thumbnails))

        for frame, start, end, x, y in self.video.thumbnails():
            with Image.open(frame) as image:
                image = image.resize((self.width, self.height), Image.ANTIALIAS)
                master.paste(image, (x, y))

        master.save(self._master_name)
        self.tempdir.cleanup()

    def generate(self):
        def _format_time(secs):
            delta = timedelta(seconds=secs)
            return ("0%s.000" % delta)[:12]

        _lines = ["WEBVTT\n\n"]
        _img_src = self.basepath + self._master_name

        for frame, start, end, x, y in self.video.thumbnails():
            _thumbnail = "%s --> %s\n%s#xywh=%d,%d,%d,%d\n\n" % (
                _format_time(start), _format_time(end),
                _img_src, x, y, self.width, self.height
            )
            _lines.append(_thumbnail)

        with open(self.output_format, "w") as vtt:
            vtt.writelines(_lines)


@register_format("json")
class JSON(ThumbnailFormat):
    def prepare_thumbnails(self):
        raise NotImplementedError

    def generate(self):
        raise NotImplementedError


__version__ = "v1.0"
__all__ = (Thumbnails,)
