"""
Veryfy same behavior of original and redone examples.

Test if the redone examples using this library has the same behavior of the original
examples from ortools by comparing the outputs of the functions.
"""
from unittest import TestCase
from functools import partialmethod
from ort_simpleroute._examples._capture_output import capture_lines
from ort_simpleroute._examples._examples_importer import import_examples_main


EXAMPLES_PKG = "ort_simpleroute._examples"
ORIGINAL_SUB = "original"
REDONE_SUB = "redone"
EXAMPLE_NAMES = ["vrp_capacity", "vrp_pickup_delivery"]

ORIGINAL_MAINS, REDONE_MAINS = import_examples_main(
    EXAMPLES_PKG, ORIGINAL_SUB, REDONE_SUB, EXAMPLE_NAMES
)


class CompareOutputsTestCase(TestCase):
    """Verify that original and redone examples have same output."""


def compare_outputs(test_case: TestCase, callable_0, callable_1):
    """
    Verify that the output of two functions is the same.

    This is intended to be used as a method of a TestCase subclass.
    """
    c0_lines = capture_lines(callable_0)
    c1_lines = capture_lines(callable_1)
    test_case.assertEqual(c0_lines, c1_lines)


for name, original_main, redone_main in zip(
    EXAMPLE_NAMES, ORIGINAL_MAINS, REDONE_MAINS
):
    method = partialmethod(
        compare_outputs, callable_0=original_main, callable_1=redone_main
    )
    setattr(CompareOutputsTestCase, "test_" + name, method)
