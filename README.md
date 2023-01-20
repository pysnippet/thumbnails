# Thumbnails <img src="https://github.com/pysnippet.png" align="right" height="64" />

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/ab5414af4c9546fe97ad64365e2a66f0)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=pysnippet/thumbnails&amp;utm_campaign=Badge_Grade)
[![License](https://img.shields.io/pypi/l/thumbnails.svg)](https://github.com/pysnippet/thumbnails/blob/master/LICENSE)

Modern web video players use the **WebVTT** formatted files to preview thumbnails at a pointed time.
[WebVTT](https://www.w3.org/TR/webvtt1/) is a format for displaying timed text tracks (such as subtitles or captions).
Open-source video players such as [Plyr](https://github.com/sampotts/plyr), [Video.js](https://github.com/videojs/video.js),
[Flowplayer](https://github.com/flowplayer/flowplayer), [Fluid Player](https://github.com/fluid-player/fluid-player),
etc. use this format for showing the thumbnails. Using [external plugins](https://github.com/brightcove/videojs-thumbnails),
Video.js also can handle **JSON** formatted thumbnails' metadata, and this tool can also generate the corresponding JSON.

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

## Contribute

Everyone is welcome to contribute to this project. Please read the [contribution guidelines](https://github.com/pysnippet/instructions#readme)
before you start. Contributions can be considered
 - Reporting an issue
 - Opening a pull-request
 - Suggesting an idea at discussions
 - Starring the repository if it was helpful

## License

Copyright (C) 2023 Artyom Vancyan. [Apache 2.0](LICENSE)
