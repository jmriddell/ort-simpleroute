"""Capture the output to stdout of a function."""
import sys
from io import StringIO


class _Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio
        sys.stdout = self._stdout


def capture_lines(function):
    """Capture output of function and return as a list of lines."""
    with _Capturing() as output:
        function()
    return output
