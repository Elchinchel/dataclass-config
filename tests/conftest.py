import os

from tempfile import mktemp

import pytest


@pytest.fixture
def tmp_filename():
    filename = mktemp()

    yield filename

    try:
        os.remove(filename)
    except FileNotFoundError:
        pass
