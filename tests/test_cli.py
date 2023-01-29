import subprocess


def execute_cli(*args, must_fail=False):
    stdout = subprocess.run(("thumbnails", *args), capture_output=True)
    assert stdout.returncode == must_fail
    return stdout.stdout.decode()


def test_cli_help():
    execute_cli("-h")
    execute_cli("--help")


def test_cli_version():
    execute_cli("-V")
    execute_cli("--version")


def test_cli_input_validation():
    execute_cli("tests/data/avi/video.avi", "tests/data/ogv", must_fail=True)


def test_cli_only_files(tmp_media):
    execute_cli("%s/avi/video.avi" % tmp_media, "%s/ogv/video.ogv" % tmp_media, "-I", "10")


def test_cli_only_directories(tmp_media):
    execute_cli("%s/avi" % tmp_media, "%s/ogv" % tmp_media, "-I", "10")
