import os
import re
import subprocess as sp

import imageio_ffmpeg
import numpy as np
from PIL import Image

FFMPEG_BINARY = imageio_ffmpeg.get_ffmpeg_exe()


def convert_to_seconds(time):
    factors = (1, 60, 3600)

    if isinstance(time, str):
        time = [float(part.replace(",", ".")) for part in time.split(":")]

    if not isinstance(time, (tuple, list)):
        return time

    return sum(mult * part for mult, part in zip(factors, reversed(time)))


def cross_platform_popen_params(popen_params):
    if os.name == "nt":
        popen_params["creationflags"] = 0x08000000
    return popen_params


class Ffmpeg:

    def __init__(self, filename, bufsize=None, pixel_format="rgba"):

        self.filename = filename
        self.proc = None
        infos = ffmpeg_parse_infos(filename)
        self.fps = infos["video_fps"]
        self.size = infos["video_size"]
        self.duration = infos["video_duration"]
        self.ffmpeg_duration = infos["duration"]
        self.n_frames = infos["video_n_frames"]
        self.bitrate = infos["video_bitrate"]

        self.infos = infos

        self.pixel_format = pixel_format
        self.depth = 4 if pixel_format[-1] == "a" else 3

        if bufsize is None:
            w, h = self.size
            bufsize = self.depth * w * h + 100

        self.bufsize = bufsize

    @staticmethod
    def frame_to_buffer(image):
        image = image.astype("uint8")
        return Image.fromarray(image)

    def get_frame(self, start_time=0):
        if start_time != 0:
            offset = min(1, start_time)
            i_arg = [
                "-ss",
                "%.06f" % (start_time - offset),
                "-i",
                self.filename,
                "-ss",
                "%.06f" % offset,
            ]
        else:
            i_arg = ["-i", self.filename]

        cmd = (
                [FFMPEG_BINARY]
                + i_arg
                + [
                    "-loglevel",
                    "error",
                    "-f",
                    "image2pipe",
                    "-vf",
                    "scale=%d:%d" % tuple(self.size),
                    "-sws_flags",
                    "bicubic",
                    "-pix_fmt",
                    "rgba",
                    "-vcodec",
                    "rawvideo",
                    "-",
                ]
        )
        popen_params = cross_platform_popen_params(
            {
                "bufsize": self.bufsize,
                "stdout": sp.PIPE,
                "stderr": sp.PIPE,
                "stdin": sp.DEVNULL,
            }
        )

        proc = sp.Popen(cmd, **popen_params)

        w, h = self.size
        nbytes = self.depth * w * h
        s = proc.stdout.read(nbytes)

        if hasattr(np, "frombuffer"):
            result = np.frombuffer(s, dtype="uint8")
        else:
            result = np.fromstring(s, dtype="uint8")

        result.shape = (h, w, len(s) // (w * h))

        return result


class FFMPEGInfos:

    def __init__(
            self,
            infos,
            filename,
            fps_source="fps",
            decode_file=False,
            check_duration=True,
    ):
        self.infos = infos
        self.filename = filename
        self.check_duration = check_duration
        self.fps_source = fps_source
        self.duration_tag_separator = "time=" if decode_file else "Duration: "

        self._reset_state()

    def _reset_state(self):
        self._inside_file_metadata = False

        self._inside_output = False

        self._default_stream_found = False

        self._current_input_file = {"streams": []}
        self._current_stream = None
        self._current_chapter = None

        self.result = {
            "video_found": False,
            "metadata": {},
            "inputs": [],
        }

        self._last_metadata_field_added = None

    def parse(self):
        input_chapters = []

        for line in self.infos.splitlines()[1:]:
            if all([
                self.duration_tag_separator == "time=",
                self.check_duration,
                "time=" in line,
            ]):
                self.result["duration"] = self.parse_duration(line)
            elif self._inside_output or line[0] != " ":
                if self.duration_tag_separator == "time=" and not self._inside_output:
                    self._inside_output = True
            elif not self._inside_file_metadata and line.startswith("  Metadata:"):
                self._inside_file_metadata = True
            elif line.startswith("  Duration:"):
                self._inside_file_metadata = False
                if self.check_duration and self.duration_tag_separator == "Duration: ":
                    self.result["duration"] = self.parse_duration(line)

                bitrate_match = re.search(r"bitrate: (\d+) kb/s", line)
                self.result["bitrate"] = (
                    int(bitrate_match.group(1)) if bitrate_match else None
                )

                start_match = re.search(r"start: (\d+\.?\d+)", line)
                self.result["start"] = (
                    float(start_match.group(1)) if start_match else None
                )
            elif self._inside_file_metadata:
                field, value = self.parse_metadata_field_value(line)

                if field == "":
                    field = self._last_metadata_field_added
                    value = self.result["metadata"][field] + "\n" + value
                else:
                    self._last_metadata_field_added = field
                self.result["metadata"][field] = value
            elif line.lstrip().startswith("Stream "):
                if self._current_stream:
                    self._current_input_file["streams"].append(self._current_stream)

                main_info_match = re.search(
                    r"^Stream\s#(\d+):(\d+)(?:\[\w+\])?\(?(\w+)?\)?:\s(\w+):",
                    line.lstrip(),
                )
                (
                    input_number,
                    stream_number,
                    language,
                    stream_type,
                ) = main_info_match.groups()
                input_number = int(input_number)
                stream_number = int(stream_number)
                stream_type_lower = stream_type.lower()

                if language == "und":
                    language = None

                self._current_stream = {
                    "input_number": input_number,
                    "stream_number": stream_number,
                    "stream_type": stream_type_lower,
                    "language": language,
                    "default": not self._default_stream_found
                               or line.endswith("(default)"),
                }
                self._default_stream_found = True

                if self._current_stream["default"]:
                    self.result[
                        f"default_{stream_type_lower}_input_number"
                    ] = input_number
                    self.result[
                        f"default_{stream_type_lower}_stream_number"
                    ] = stream_number

                if self._current_chapter:
                    input_chapters[input_number].append(self._current_chapter)
                    self._current_chapter = None

                if "input_number" not in self._current_input_file:
                    self._current_input_file["input_number"] = input_number
                elif self._current_input_file["input_number"] != input_number:

                    if len(input_chapters) >= input_number + 1:
                        self._current_input_file["chapters"] = input_chapters[
                            input_number
                        ]

                    self.result["inputs"].append(self._current_input_file)
                    self._current_input_file = {"input_number": input_number}

                try:
                    global_data, stream_data = self.parse_data_by_stream_type(
                        stream_type, line
                    )
                except NotImplementedError:
                    pass
                else:
                    self.result.update(global_data)
                    self._current_stream.update(stream_data)
            elif line.startswith("    Metadata:"):
                continue
            elif self._current_stream:
                if "metadata" not in self._current_stream:
                    self._current_stream["metadata"] = {}

                field, value = self.parse_metadata_field_value(line)

                if self._current_stream["stream_type"] == "video":
                    field, value = self.video_metadata_type_casting(field, value)
                    if field == "rotate":
                        self.result["video_rotation"] = value

                if field == "":
                    field = self._last_metadata_field_added
                    value = self._current_stream["metadata"][field] + "\n" + value
                else:
                    self._last_metadata_field_added = field
                self._current_stream["metadata"][field] = value
            elif line.startswith("    Chapter"):
                if self._current_chapter:
                    if len(input_chapters) < self._current_chapter["input_number"] + 1:
                        input_chapters.append([])
                    input_chapters[self._current_chapter["input_number"]].append(
                        self._current_chapter
                    )

                chapter_data_match = re.search(
                    r"^    Chapter #(\d+):(\d+): start (\d+\.?\d+?), end (\d+\.?\d+?)",
                    line,
                )
                input_number, chapter_number, start, end = chapter_data_match.groups()

                self._current_chapter = {
                    "input_number": int(input_number),
                    "chapter_number": int(chapter_number),
                    "start": float(start),
                    "end": float(end),
                }
            elif self._current_chapter:
                if "metadata" not in self._current_chapter:
                    self._current_chapter["metadata"] = {}
                field, value = self.parse_metadata_field_value(line)

                if field == "":
                    field = self._last_metadata_field_added
                    value = self._current_chapter["metadata"][field] + "\n" + value
                else:
                    self._last_metadata_field_added = field
                self._current_chapter["metadata"][field] = value

        if self._current_input_file:
            self._current_input_file["streams"].append(self._current_stream)
            if len(input_chapters) == self._current_input_file["input_number"] + 1:
                self._current_input_file["chapters"] = input_chapters[
                    self._current_input_file["input_number"]
                ]
            self.result["inputs"].append(self._current_input_file)

        if self.result["video_found"] and self.check_duration:
            self.result["video_n_frames"] = int(
                self.result["duration"] * self.result["video_fps"]
            )
            self.result["video_duration"] = self.result["duration"]
        else:
            self.result["video_n_frames"] = 1
            self.result["video_duration"] = None

        result = self.result

        self._reset_state()

        return result

    def parse_data_by_stream_type(self, stream_type, line):
        try:
            return {
                "Video": self.parse_video_stream_data,
            }[stream_type](line)
        except KeyError:
            raise NotImplementedError(
                f"{stream_type} stream parsing is not supported by moviepy and"
                " will be ignored"
            )

    def parse_video_stream_data(self, line):
        global_data, stream_data = ({"video_found": True}, {})

        match_video_size = re.search(r" (\d+)x(\d+)[,\s]", line)
        if match_video_size:
            stream_data["size"] = [int(num) for num in match_video_size.groups()]

        match_bitrate = re.search(r"(\d+) kb/s", line)
        stream_data["bitrate"] = int(match_bitrate.group(1)) if match_bitrate else None

        if self.fps_source == "fps":
            try:
                fps = self.parse_fps(line)
            except (AttributeError, ValueError):
                fps = self.parse_tbr(line)
        elif self.fps_source == "tbr":
            try:
                fps = self.parse_tbr(line)
            except (AttributeError, ValueError):
                fps = self.parse_fps(line)
        else:
            raise ValueError(
                "fps source '%s' not supported parsing the video '%s'"
                % (self.fps_source, self.filename)
            )

        coef = 1000.0 / 1001.0
        for x in [23, 24, 25, 30, 50]:
            if (fps != x) and abs(fps - x * coef) < 0.01:
                fps = x * coef
        stream_data["fps"] = fps

        if self._current_stream["default"] or "video_size" not in self.result:
            global_data["video_size"] = stream_data.get("size", None)
        if self._current_stream["default"] or "video_bitrate" not in self.result:
            global_data["video_bitrate"] = stream_data.get("bitrate", None)
        if self._current_stream["default"] or "video_fps" not in self.result:
            global_data["video_fps"] = stream_data["fps"]

        return global_data, stream_data

    @staticmethod
    def parse_fps(line):
        return float(re.search(r" (\d+.?\d*) fps", line).group(1))

    @staticmethod
    def parse_tbr(line):
        s_tbr = re.search(r" (\d+.?\d*k?) tbr", line).group(1)

        if s_tbr[-1] == "k":
            tbr = float(s_tbr[:-1]) * 1000
        else:
            tbr = float(s_tbr)
        return tbr

    def parse_duration(self, line):
        time_raw_string = line.split(self.duration_tag_separator)[-1]
        match_duration = re.search(
            r"([0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9])",
            time_raw_string,
        )
        return convert_to_seconds(match_duration.group(1))

    @staticmethod
    def parse_metadata_field_value(line):
        raw_field, raw_value = line.split(":", 1)
        return raw_field.strip(" "), raw_value.strip(" ")

    @staticmethod
    def video_metadata_type_casting(field, value):
        if field == "rotate":
            return field, float(value)
        return field, value


def ffmpeg_parse_infos(
        filename,
        check_duration=True,
        fps_source="fps",
        decode_file=False,
):
    cmd = [FFMPEG_BINARY, "-hide_banner", "-i", filename]
    if decode_file:
        cmd.extend(["-f", "null", "-"])

    popen_params = cross_platform_popen_params(
        {
            "bufsize": 10 ** 5,
            "stdout": sp.PIPE,
            "stderr": sp.PIPE,
            "stdin": sp.DEVNULL,
        }
    )

    proc = sp.Popen(cmd, **popen_params)
    (output, error) = proc.communicate()
    infos = error.decode("utf8", errors="ignore")

    proc.terminate()
    del proc

    return FFMPEGInfos(
        infos,
        filename,
        fps_source=fps_source,
        decode_file=decode_file,
        check_duration=check_duration,
    ).parse()
