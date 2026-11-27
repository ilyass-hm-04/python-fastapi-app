import sys


def test_break():
    assert sys.platform != "win32"  # fails only on Windows
