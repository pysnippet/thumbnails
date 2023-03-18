# Thumbnails <img src="https://github.com/pysnippet.png" align="right" height="64" />

[![PyPI](https://img.shields.io/pypi/v/thumbnails.svg)](https://pypi.org/project/thumbnails/)
[![Tests Ubuntu | MacOS](https://github.com/pysnippet/thumbnails/actions/workflows/tests.yml/badge.svg)](https://github.com/pysnippet/thumbnails/actions/workflows/tests.yml)
[![Tests Windows](https://img.shields.io/circleci/build/gh/pysnippet/thumbnails?token=c63e2b94c69393ab3e47a0f20de802fe6265ecf4&label=Tests%20Windows&logo=circleci&logoColor=959da5&labelColor=3e464f)](https://app.circleci.com/pipelines/github/pysnippet/thumbnails)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/ab5414af4c9546fe97ad64365e2a66f0)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=pysnippet/thumbnails&amp;utm_campaign=Badge_Grade)
[![License](https://img.shields.io/pypi/l/thumbnails.svg)](https://github.com/pysnippet/thumbnails/blob/master/LICENSE)

This tool stands out for its unparalleled optimization for lightning-fast thumbnail generation. By utilizing minimal
resources, you can generate more in less time. And with a user-friendly CLI and a convenient Python API, this tool is
the ultimate solution for efficient and streamlined thumbnail creation.

## Compatible with Major Video Players

Modern web video players use the **WebVTT** formatted files to preview thumbnails at a pointed time.
[WebVTT](https://www.w3.org/TR/webvtt1/) is a format for displaying timed text tracks (such as subtitles or captions).
Open-source video players such as [Plyr](https://github.com/sampotts/plyr), [Video.js](https://github.com/videojs/video.js),
[Flowplayer](https://github.com/flowplayer/flowplayer), [Fluid Player](https://github.com/fluid-player/fluid-player),
and more, use this format for showing the thumbnails. And, with the use of [external plugins](https://github.com/brightcove/videojs-thumbnails),
Video.js even has the capability to handle **JSON** formatted thumbnail metadata. This is where our tool comes in,
offering the ability to generate the perfect thumbnails to match your needs.

## Features

- Wide-ranging video format compatibility, accommodating all major video formats as input files. (mp4, mkv, avi, mov, ogv, webm, mpeg, mpg, wmv, etc.)
- Flexible output options, supporting both WebVTT and JSON formats.
- Generating video thumbnails through the CLI and the Python API.
- Customize your thumbnail creation to fit your specific needs with various options.
- Image compression technology, ensuring optimized file sizes for quick and efficient loading times.

## How to Use?

### CLI Tool Usage

The CLI is a convenient way to generate thumbnails for a video file. And it accepts files or directories as arguments.
For the complete list of options, run `thumbnails --help`.

```bash
thumbnails --base /media/ --output /var/www/movie.com/media/thumbnails/ --interval 5 ~Videos/movies
```

### Python API Usage

The Python API provides a flexible way to integrate video thumbnail generation into your existing applications.
Both the CLI and the Python API share the same set of options.

```python
from thumbnails import Generator

inputs = (
    "~Downloads/movie.mp4",
    "~Videos/movies/1.avi",
    "~Videos/movies/2.ogv",
)

generator = Generator(inputs)
generator.base = "/media/"
generator.skip = True  # skip existing thumbnails
generator.output = "/var/www/movie.com/media/thumbnails/"
generator.interval = 5
generator.generate()
```

## Development

Run the following command in the package's root directory to install it in editable mode.
```bash
python3 -m pip install -e .
```
This command will install the package in your local environment and allow you to make changes to the code and see the
updates immediately. It will also install all the required dependencies.

## Contribute

Everyone is welcome to contribute to this project. Please read and follow the [contribution guidelines](CONTRIBUTING.md)
before you start. Contributions can be considered:
- Reporting an issue
- Opening a pull-request
- Suggesting an idea at [discussions](https://github.com/pysnippet/thumbnails/discussions)
- Starring the repository if you like it

Before you open a PR, please run the unit tests in the local environment to ensure everything is working. You need to
install [tox](https://github.com/tox-dev/tox) and run the tests for configured environments.
```bash
python3 -m pip install tox && tox
```

If you want to run tests only for the current environment with your local Python interpreter, you can use the following
commands.

```bash
python3 -m pip install -r tests/requirements.txt
python3 -m pytest
```

## License

Copyright (C) 2023 Artyom Vancyan. [Apache 2.0](https://github.com/pysnippet/thumbnails/blob/master/LICENSE)
