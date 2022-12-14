# Thumbnails (WebVTT/JSON)

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

## TODO List

- Implement thumbnail preview feature using following kinds of video players.
    - Plyr (https://github.com/sampotts/plyr)
    - Video.js (https://github.com/videojs/video.js)
    - JW Player (https://github.com/jwplayer/jwplayer)
    - Flowplayer (https://github.com/flowplayer/flowplayer)
    - Fluid Player (https://github.com/fluid-player/fluid-player)

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
- Use `aiofiles` and `multiprocessing.Pool.map` to process the media-files with high performance.

## Examples

- Video.js
   ```js
   var player = videojs('my-video', {
     thumbs: [
       {
         time: 5,
         image: 'path/to/thumbnail-1.jpg'
       },
       {
         time: 10,
         image: 'path/to/thumbnail-2.jpg'
       },
       // Additional thumbnail preview objects...
     ]
   });
   ```
- JW Player
   ```js
     var player = jwplayer('my-player');
     player.setup({
       file: 'path/to/my-video.mp4',
       thumbnails: [
         {
           time: 5,
           image: 'path/to/thumbnail-1.jpg'
         },
         {
           time: 10,
           image: 'path/to/thumbnail-2.jpg'
         },
         // Additional thumbnail preview objects...
       ]
     });
     ```
- Video.js (with WebVTT)
  ```html
  <link href="https://unpkg.com/video.js@7.20.3/dist/video-js.css" rel="stylesheet">
  <script src="https://unpkg.com/video.js/dist/video.min.js"></script>
  <style>
  .vjs-thumbnail-preview {
    width: 120px;
    height: 90px;
    position: absolute;
    bottom: 5px;
    right: 5px;
  }
  </style>
  
  <video id="my-video" class="video-js" controls data-setup='{"textTracks": [{"src": "https://example.com/thumbnail-preview.vtt", "kind": "metadata", "default": true}]}'>
    <source src="https://example.com/video.mp4" type="video/mp4">
  </video>
  
  <script>
    videojs('my-video');
  </script>
  ```

## Good single page documentation example

- http://blog.raphaelmutschler.de/mt/

## Usage Examples

```bash
thumbnails [options]
```

| Option      | Default | Description                                                                                   |
|-------------|:-------:|-----------------------------------------------------------------------------------------------|
| `parallel`  | `false` | Process in parallel to make it faster.                                                        |
| `overwrite` | `false` | Overwrite the existing files with new ones.                                                   |
| `interval`  |   0.5   | The interval between two thumbnails in seconds.                                               |
| `compress`  |    1    | The image compression coefficient is a number from 0 to 1 where 1 means _no compression_.     |
| `as`        |  `vtt`  | Output as either `VTT` or `JSON` format.                                                      |
| `basepath`  |    -    | In case the relative path does not work, the prefix of the thumbnails path can be customized. |
