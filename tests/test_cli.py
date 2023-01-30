# import os
# import subprocess
#
#
# def execute_cli(*args, must_fail=False):
#     stdout = subprocess.run(("thumbnails", *args), capture_output=True)
#     assert stdout.returncode == must_fail
#     return stdout.stdout.decode()
#
#
# def test_cli_help():
#     execute_cli("-h")
#     execute_cli("--help")
#
#
# def test_cli_version():
#     execute_cli("-V")
#     execute_cli("--version")
#
#
# def test_cli_input_validation():
#     execute_cli(
#         os.path.join("tests", "data", "avi", "video.avi"),
#         os.path.join("tests", "data", "ogv"),
#         must_fail=True,
#     )
#
#
# def test_cli_only_files(tmp_media):
#     print("avi:", os.listdir(os.path.join(tmp_media, "avi")))
#     print("ogv:", os.listdir(os.path.join(tmp_media, "ogv")))
#     execute_cli(
#         os.path.join(tmp_media, "avi", "video.avi"),
#         os.path.join(tmp_media, "ogv", "video.ogv"),
#         "-I",
#         "10",
#     )
#     print("avi:", os.listdir(os.path.join(tmp_media, "avi")))
#     print("ogv:", os.listdir(os.path.join(tmp_media, "ogv")))
#     assert os.path.exists(os.path.join(tmp_media, "avi", "video.png"))
#     assert os.path.exists(os.path.join(tmp_media, "avi", "video.vtt"))
#
#
# def test_cli_only_directories(tmp_media):
#     print("avi:", os.listdir(os.path.join(tmp_media, "avi")))
#     print("ogv:", os.listdir(os.path.join(tmp_media, "ogv")))
#     execute_cli(
#         os.path.join(tmp_media, "avi"),
#         os.path.join(tmp_media, "ogv"),
#         "-I",
#         "10",
#     )
#     print("avi:", os.listdir(os.path.join(tmp_media, "avi")))
#     print("ogv:", os.listdir(os.path.join(tmp_media, "ogv")))
#     assert os.path.exists(os.path.join(tmp_media, "avi", "video.png"))
#     assert os.path.exists(os.path.join(tmp_media, "avi", "video.vtt"))
#     assert os.path.exists(os.path.join(tmp_media, "ogv", "video.png"))
#     assert os.path.exists(os.path.join(tmp_media, "ogv", "video.vtt"))
