# Thumbnails

WebVTT is a format for displaying timed text tracks (such as subtitles or captions). This format is mainly used for
showing subtitles on video. But there are some popular open source video players such as Plyr, Video.js, Flowplayer, and
Fluid Player that use this format for showing the thumbnail preview.

## Similar Projects

- https://github.com/mutschler/mt
- https://github.com/anshulkharb/thumbnail
- https://github.com/kevinyang372/py-thumbnail
- https://github.com/Revan654/movie-thumbnailer-mtn
- https://github.com/estliberitas/node-thumbnails-webvtt
- https://github.com/flavioribeiro/video-thumbnail-generator

## NOTES

_The following notes are thought based
on [this](https://stackoverflow.com/questions/52900022/how-to-generate-video-preview-thumbnails-for-use-in-videojs)
StackOverflow answer_

[moviethumbnail](https://moviethumbnail.sourceforge.net/) is the coolest one that is available on linux as well. This
one must show the highest performance and support various output customization options.

- Support multiple video formats as an input file
- Support WebVTT/json output formats
- Set an interval, etc (options).
- Image compression opportunity.
- Provide a well documented python API.
- Use like a linux command or as a python library.
- Deliver a high performance result.

## Good single page documentation example

- http://blog.raphaelmutschler.de/mt/

## Usage

```bash
thumbnails [options]
```

| Option      | Default | Description                                                                                   |
|-------------|:-------:|-----------------------------------------------------------------------------------------------|
| `as`        |  `vtt`  | Output as either `VTT` or `JSON` format.                                                      |
| `interval`  |    1    | The interval between two thumbnails in seconds.                                               |
| `compress`  |    1    | The image compression coefficient is a number from 0 to 1 where 1 means _no compression_.     |
| `basepath`  |    -    | In case the relative path does not work, the prefix of the thumbnails path can be customized. |
