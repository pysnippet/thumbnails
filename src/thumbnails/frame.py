import math


class _Frame:
    """This class is used to calculate the optimal size of a thumbnail frame."""

    def __init__(self, size):
        width, height = size
        _min_width = 300
        _min_height = math.ceil(_min_width * height / width)

        self.__width = None
        self.__height = None

        self._width = width / 10
        self._height = height / 10
        self._min_width = _min_width
        self._min_height = _min_height

    @property
    def compress(self):
        """Defines an interface for the compress property."""
        raise NotImplementedError

    @property
    def width(self):
        """Calculates and caches the frame width."""
        if not self.__width:
            self.__width = max(self._min_width, self._width * self.compress)
        return self.__width

    @property
    def height(self):
        """Calculates and caches the frame height."""
        if not self.__height:
            self.__height = max(self._min_height, self._height * self.compress)
        return self.__height
