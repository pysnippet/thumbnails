# Thumbnails <img src="https://github.com/pysnippet.png" align="right" height="64" />

[![PyPI](https://img.shields.io/pypi/v/thumbnails.svg)](https://pypi.org/project/thumbnails/)
[![Tests Ubuntu | MacOS](https://github.com/pysnippet/thumbnails/actions/workflows/tests.yml/badge.svg)](https://github.com/pysnippet/thumbnails/actions/workflows/tests.yml)
[![Tests Windows](https://img.shields.io/circleci/build/gh/pysnippet/thumbnails?token=c63e2b94c69393ab3e47a0f20de802fe6265ecf4&label=Tests%20Windows&logo=circleci)](https://app.circleci.com/pipelines/github/pysnippet/thumbnails)
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

## Goals

[//]: # (TODO: replace this whole section with a "Why use this tool?" section by describing the below clauses.)

- [x] Support multiple video formats as an input file
- [x] Support WebVTT/json output formats
- [x] Set an interval, etc (options).
- [ ] [Image compression opportunity.](https://github.com/pysnippet/thumbnails/issues/29)
- [ ] [Provide a well documented python API.](https://github.com/pysnippet/thumbnails/issues/11)
- [ ] [Use like a linux command or as a python library.](https://github.com/pysnippet/thumbnails/issues/18)
- [x] Deliver a high performance result.

## Usage

```bash
thumbnails --help
```

[//]: # (TODO: usage for CLI and python API)

## Development

### Install the package in editable mode
This will install the package in the local environment and will allow you to make changes to the code and see the
changes immediately. Also, this command will install all the required dependencies of the `requirements.txt` list.
```bash
python3 -m pip install -e .
```

## Contribute

Everyone is welcome to contribute to this project. Please read and follow the [contribution guidelines](https://github.com/pysnippet/instructions#readme)
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

## License

Copyright (C) 2023 Artyom Vancyan. [Apache 2.0](LICENSE)
