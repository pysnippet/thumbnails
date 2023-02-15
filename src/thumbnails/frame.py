import math


class _Frame:
    """This class is used to calculate the optimal size of a thumbnail frame."""

    def __init__(self, size):
        # Original size of the frame
        self._width, self._height = size

        # Minimum size of the frame
        self._min_width = 30
        self._min_height = math.ceil(self._min_width * self._height / self._width)

        # Maximum size of the frame
        self._max_width = 7680 // self.columns_count  # 7680 is the width of 8K
        self._max_height = math.ceil(self._max_width * self._height / self._width)

        # Final size of the frame
        self.__width = None
        self.__height = None

    @property
    def compress(self):
        """Defines an interface for the compress property."""
        raise NotImplementedError

    @property
    def frames_count(self):
        """Defines an interface for the frames_count property."""
        raise NotImplementedError

    @property
    def columns_count(self):
        """Defines an interface for the columns_count property."""
        raise NotImplementedError

    @property
    def width(self):
        """Calculates and caches the frame width."""
        if not self.__width:
            self.__width = round(self._width * self.compress)
            self.__width = max(self.__width, self._min_width)
            self.__width = min(self.__width, self._max_width)
        return self.__width

    @property
    def height(self):
        """Calculates and caches the frame height."""
        if not self.__height:
            self.__height = round(self._height * self.compress)
            self.__height = max(self.__height, self._min_height)
            self.__height = min(self.__height, self._max_height)
        return self.__height
