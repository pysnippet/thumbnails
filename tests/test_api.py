import os

from thumbnails import Generator


def thumbnail_generation_with_default_output(tmp_media, inputs, fmt):
    generator = Generator(inputs)
    generator.interval = 10
    generator.format = fmt
    generator.generate()

    with (
        open("%s/snapshots/relative-base-%s" % (tmp_media, fmt)) as snapshot,
        open("%s/avi/video.%s" % (tmp_media, fmt)) as avi_result,
        open("%s/ogv/video.%s" % (tmp_media, fmt)) as ogv_result,
    ):
        snapshot = snapshot.read()
        avi_snapshot = snapshot % {"tmp_media": os.path.join(os.path.relpath(tmp_media), "avi")}
        ogv_snapshot = snapshot % {"tmp_media": os.path.join(os.path.relpath(tmp_media), "ogv")}
        if fmt == "json":
            assert len(os.listdir("%s/avi/video" % tmp_media)) == 11
            assert len(os.listdir("%s/ogv/video" % tmp_media)) == 11
        assert avi_snapshot == avi_result.read()
        assert ogv_snapshot == ogv_result.read()


def thumbnail_generation_with_with_extras(tmp_media, inputs, fmt):
    generator = Generator(inputs)
    generator.base = "/media/thumbnails/"
    generator.output = "%s/thumbnails" % tmp_media
    generator.format = fmt
    generator.compress = 0.5
    generator.interval = 10
    generator.generate()

    with (
        open("%s/snapshots/specified-base-%s" % (tmp_media, fmt)) as snapshot,
        open("%s/thumbnails/video.%s" % (tmp_media, fmt)) as result,
    ):
        if fmt == "json":
            assert len(os.listdir("%s/thumbnails/video" % tmp_media)) == 11
        assert snapshot.read() == result.read()


def test_api_vtt_generation_directory_inputs_default_output(tmp_media):
    inputs = ("%s/avi" % tmp_media, "%s/ogv" % tmp_media)
    thumbnail_generation_with_default_output(tmp_media, inputs, "vtt")


def test_api_vtt_generation_file_inputs_default_output(tmp_media):
    inputs = ("%s/avi/video.avi" % tmp_media, "%s/ogv/video.ogv" % tmp_media)
    thumbnail_generation_with_default_output(tmp_media, inputs, "vtt")


def test_api_vtt_generation_with_extras(tmp_media):
    inputs = ("%s/avi" % tmp_media, "%s/ogv" % tmp_media)
    thumbnail_generation_with_with_extras(tmp_media, inputs, "vtt")


def test_api_json_generation_directory_inputs_default_output(tmp_media):
    inputs = ("%s/avi" % tmp_media, "%s/ogv" % tmp_media)
    thumbnail_generation_with_default_output(tmp_media, inputs, "json")


def test_api_json_generation_file_inputs_default_output(tmp_media):
    inputs = ("%s/avi/video.avi" % tmp_media, "%s/ogv/video.ogv" % tmp_media)
    thumbnail_generation_with_default_output(tmp_media, inputs, "json")


def test_api_json_generation_with_extras(tmp_media):
    inputs = ("%s/avi" % tmp_media, "%s/ogv" % tmp_media)
    thumbnail_generation_with_with_extras(tmp_media, inputs, "json")
