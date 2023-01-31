import os
import pathlib

from thumbnails import Generator


def thumbnail_generation_with_default_output(tmp_media, inputs, fmt):
    generator = Generator(inputs)
    generator.interval = 10
    generator.format = fmt
    generator.generate()

    snapshot = open(os.path.join(tmp_media, "snapshots", "relative-base-%s" % fmt))
    avi_result = open(os.path.join(tmp_media, "avi", "video.%s" % fmt))
    ogv_result = open(os.path.join(tmp_media, "ogv", "video.%s" % fmt))

    snapshot_data = snapshot.read()
    avi_snapshot = snapshot_data % {
        "tmp_media": pathlib.Path(os.path.join(os.path.relpath(tmp_media), "avi")).as_posix()
    }
    ogv_snapshot = snapshot_data % {
        "tmp_media": pathlib.Path(os.path.join(os.path.relpath(tmp_media), "ogv")).as_posix()
    }
    if fmt == "json":
        assert len(os.listdir(os.path.join(tmp_media, "avi", "video"))) == 11
        assert len(os.listdir(os.path.join(tmp_media, "ogv", "video"))) == 11
    assert avi_snapshot == avi_result.read()
    assert ogv_snapshot == ogv_result.read()

    snapshot.close()
    avi_result.close()
    ogv_result.close()


def thumbnail_generation_with_with_extras(tmp_media, inputs, fmt):
    generator = Generator(inputs)
    generator.base = "/media/thumbnails/"
    generator.output = os.path.join(tmp_media, "thumbnails")
    generator.format = fmt
    generator.compress = 0.5
    generator.interval = 10
    generator.generate()

    snapshot = open(os.path.join(tmp_media, "snapshots", "specified-base-%s" % fmt))
    result = open(os.path.join(tmp_media, "thumbnails", "video.%s" % fmt))

    if fmt == "json":
        assert len(os.listdir(os.path.join(tmp_media, "thumbnails", "video"))) == 11
    assert snapshot.read() == result.read()

    snapshot.close()
    result.close()


def test_api_vtt_generation_directory_inputs_default_output(tmp_media):
    inputs = (os.path.join(tmp_media, "avi"), os.path.join(tmp_media, "ogv"))
    thumbnail_generation_with_default_output(tmp_media, inputs, "vtt")


def test_api_vtt_generation_file_inputs_default_output(tmp_media):
    inputs = (os.path.join(tmp_media, "avi", "video.avi"), os.path.join(tmp_media, "ogv", "video.ogv"))
    thumbnail_generation_with_default_output(tmp_media, inputs, "vtt")


def test_api_vtt_generation_with_extras(tmp_media):
    inputs = (os.path.join(tmp_media, "avi"), os.path.join(tmp_media, "ogv"))
    thumbnail_generation_with_with_extras(tmp_media, inputs, "vtt")


def test_api_json_generation_directory_inputs_default_output(tmp_media):
    inputs = (os.path.join(tmp_media, "avi"), os.path.join(tmp_media, "ogv"))
    thumbnail_generation_with_default_output(tmp_media, inputs, "json")


def test_api_json_generation_file_inputs_default_output(tmp_media):
    inputs = (os.path.join(tmp_media, "avi", "video.avi"), os.path.join(tmp_media, "ogv", "video.ogv"))
    thumbnail_generation_with_default_output(tmp_media, inputs, "json")


def test_api_json_generation_with_extras(tmp_media):
    inputs = (os.path.join(tmp_media, "avi"), os.path.join(tmp_media, "ogv"))
    thumbnail_generation_with_with_extras(tmp_media, inputs, "json")
