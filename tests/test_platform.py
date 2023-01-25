import sys


def test_is_platform_linux():
    assert isinstance(sys.platform, str)
