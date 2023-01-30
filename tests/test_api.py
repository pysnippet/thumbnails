import os
import pathlib
import subprocess

from thumbnails import Generator


def thumbnail_generation_with_default_output(tmp_media, inputs, fmt):
    generator = Generator(inputs)
    generator.interval = 10
    generator.format = fmt
    generator.generate()

    print(subprocess.run(("ls", inputs[0]), capture_output=True))

    print("start test")

    snapshot = open(os.path.join(tmp_media, "snapshots", "relative-base-%s" % fmt))
    print("snapshot", snapshot)
    avi_result = open(os.path.join(tmp_media, "avi", "video.%s" % fmt))
    print("avi_result", avi_result)
    ogv_result = open(os.path.join(tmp_media, "ogv", "video.%s" % fmt))
    print("ogv_result", ogv_result)

    snapshot_data = snapshot.read()
    print("snapshot_data", snapshot_data)
    avi_snapshot = snapshot_data % {
        "tmp_media": pathlib.Path(os.path.join(os.path.relpath(tmp_media), "avi")).as_posix()
    }
    print("avi_snapshot", avi_snapshot)
    ogv_snapshot = snapshot_data % {
        "tmp_media": pathlib.Path(os.path.join(os.path.relpath(tmp_media), "ogv")).as_posix()
    }
    print("ogv_snapshot", ogv_snapshot)
    if fmt == "json":
        assert len(os.listdir(os.path.join(tmp_media, "avi", "video"))) == 11
        assert len(os.listdir(os.path.join(tmp_media, "ogv", "video"))) == 11
    assert avi_snapshot == avi_result.read()
    assert ogv_snapshot == ogv_result.read()

    snapshot.close()
    avi_result.close()
    ogv_result.close()

    print("end test")


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

# def test_api_vtt_generation_directory_inputs_default_output(tmp_media):
#     inputs = (os.path.join(tmp_media, "avi"), os.path.join(tmp_media, "ogv"))
#     thumbnail_generation_with_default_output(tmp_media, inputs, "vtt")
#
#
# def test_api_vtt_generation_file_inputs_default_output(tmp_media):
#     inputs = (os.path.join(tmp_media, "avi", "video.avi"), os.path.join(tmp_media, "ogv", "video.ogv"))
#     thumbnail_generation_with_default_output(tmp_media, inputs, "vtt")
#
#
# def test_api_vtt_generation_with_extras(tmp_media):
#     inputs = (os.path.join(tmp_media, "avi"), os.path.join(tmp_media, "ogv"))
#     thumbnail_generation_with_with_extras(tmp_media, inputs, "vtt")
#
#
# def test_api_json_generation_directory_inputs_default_output(tmp_media):
#     inputs = (os.path.join(tmp_media, "avi"), os.path.join(tmp_media, "ogv"))
#     thumbnail_generation_with_default_output(tmp_media, inputs, "json")
#
#
# def test_api_json_generation_file_inputs_default_output(tmp_media):
#     inputs = (os.path.join(tmp_media, "avi", "video.avi"), os.path.join(tmp_media, "ogv", "video.ogv"))
#     thumbnail_generation_with_default_output(tmp_media, inputs, "json")
#
#
# def test_api_json_generation_with_extras(tmp_media):
#     inputs = (os.path.join(tmp_media, "avi"), os.path.join(tmp_media, "ogv"))
#     thumbnail_generation_with_with_extras(tmp_media, inputs, "json")
