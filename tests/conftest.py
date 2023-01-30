import os
from distutils.dir_util import copy_tree
from tempfile import TemporaryDirectory

import pytest


@pytest.fixture
def tmp_media():
    with TemporaryDirectory() as tempdir:
        copy_tree(os.path.join("tests", "data"), tempdir)
        yield tempdir
