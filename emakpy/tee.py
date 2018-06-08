import sys


class Tee:
    def __init__(self, filename, mode="a"):
        self._filename = filename
        self._mode = mode

    def __enter__(self):
        self._file = open(self._filename, self._mode)
        self._stream = sys.stdout
        sys.stdout = self

    def __exit__(self, exc_type, exc_value, traceback):
        self._file.close()
        sys.stdout = self._stream

    def write(self, s):
        self._file.write(s)
        self._stream.write(s)
