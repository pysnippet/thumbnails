# import asyncio

import imageio
from PIL import Image


class Ffmpeg:

    def __init__(self, filename):
        self.filename = filename
        self.reader = imageio.get_reader(filename)
        self.meta = self.reader.get_meta_data()
        self.duration = self.meta.get("duration")
        self.fps = self.meta.get("fps")

    def get_frame(self, t):
        pos = int(self.fps * t + 0.00001) + 1
        return self.reader.get_data(pos)

    def get_frame_buffer(self, t=0):
        image = self.get_frame(t)
        image = image.astype("uint8")
        return Image.fromarray(image)

    def close(self):
        self.reader.close()

    def __del__(self):
        self.close()

# class Ffmpeg:
#
#     def __init__(self, filename):
#         self.filename = filename
#
#     def get_frame(self, t):
#         pos = int(self.fps * t + 0.00001) + 1
#         return self.reader.get_data(pos)
#
#     def get_frame_buffer(self, t=0):
#         # image = await asyncio.to_thread(self.get_frame, t)
#         image = self.get_frame(t)
#         image = image.astype("uint8")
#         return Image.fromarray(image)
#
#     async def __aenter__(self):
#         self.reader = await asyncio.to_thread(
#             imageio.get_reader, self.filename)
#         self.meta = self.reader.get_meta_data()
#         self.duration = self.meta.get("duration")
#         self.fps = self.meta.get("fps")
#         return self
#
#     async def __aexit__(self, *_):
#         self.close()
#
#     def close(self):
#         self.reader.close()
#
#     def __del__(self):
#         self.close()
