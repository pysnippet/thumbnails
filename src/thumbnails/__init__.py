"""
   Copyright 2023 Artyom Vancyan

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from .thumbnail import Thumbnail
from .thumbnail import ThumbnailExistsError
from .thumbnail import ThumbnailFactory
from .thumbnail import ThumbnailJSON
from .thumbnail import ThumbnailVTT
from .thumbnail import register_thumbnail

DEFAULT_BASE = ""
DEFAULT_SKIP = False
DEFAULT_OUTPUT = None
DEFAULT_FORMAT = "vtt"
DEFAULT_COMPRESS = 1.0
DEFAULT_INTERVAL = 1.0

__version__ = "0.1.0"
__all__ = (
    "DEFAULT_BASE",
    "DEFAULT_SKIP",
    "DEFAULT_OUTPUT",
    "DEFAULT_FORMAT",
    "DEFAULT_COMPRESS",
    "DEFAULT_INTERVAL",
    "__version__",
)
