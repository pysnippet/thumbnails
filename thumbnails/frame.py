import functools
import math


class _Frame:
    """This mixin class is used to optimally calculate the size of a thumbnail frame."""

    def __init__(self, size):
        width, height = size
        _min_width = 300
        _min_height = math.ceil(_min_width * height / width)

        self._width = width / 10
        self._height = height / 10
        self._min_width = _min_width
        self._min_height = _min_height

    @property
    def compress(self):
        """Defines an interface for the compress property."""
        raise NotImplementedError

    @functools.cached_property
    def width(self):
        """Calculates and caches the width."""
        return max(self._min_width, self._width * self.compress)

    @functools.cached_property
    def height(self):
        """Calculates and caches the height."""
        return max(self._min_height, self._height * self.compress)
