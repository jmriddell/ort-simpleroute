import sys
from io import StringIO
from unittest import TestCase

from ort_simpleroute._examples import re_capacity_constraint, re_pickup_delivery
from ort_simpleroute._examples.original import vrp_capacity, vrp_pickup_delivery


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


def capture_lines(function):
    with Capturing() as output:
        function()
    return output


class CompareOutputsTestCase(TestCase):
    def test_capacity_constraint(self):
        or_lines = capture_lines(vrp_capacity.main)
        re_lines = capture_lines(re_capacity_constraint.main)
        self.assertEqual(or_lines, re_lines)

    def test_vrp_pickup_delivery(self):
        or_lines = capture_lines(vrp_pickup_delivery.main)
        re_lines = capture_lines(re_pickup_delivery.main)
        self.assertEqual(or_lines, re_lines)
