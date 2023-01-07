import math


class _ThumbnailMixin:
    def __init__(self, size):
        self._w = None
        self._h = None

        width, height = size
        _min_width = 300
        _min_height = math.ceil(_min_width * height / width)

        self._width = width / 10
        self._height = height / 10
        self._min_width = _min_width
        self._min_height = _min_height

    def get_compress(self):
        raise NotImplementedError

    @property
    def width(self):
        if not self._w:
            self._w = max(self._min_width, self._width * self.get_compress())
        return self._w

    @property
    def height(self):
        if not self._h:
            self._h = max(self._min_height, self._height * self.get_compress())
        return self._h
