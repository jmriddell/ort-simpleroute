"""
Veryfy same behavior of original and redone examples.

Test if the redone examples using this library have the same behavior of the original
examples from ortools by comparing the outputs of the functions.
"""
from unittest import TestCase
from functools import partialmethod
from ort_simpleroute.test_examples_same_output._capture_output import capture_lines
from ort_simpleroute.test_examples_same_output._examples_importer import (
    import_examples_main,
)


# The paths where the importer has to find the examples
EXAMPLES_PKG = "ort_simpleroute.test_examples_same_output._examples"
ORIGINAL_SUB = "original"
REDONE_SUB = "redone"
# The examples to import
EXAMPLE_NAMES = ["vrp_capacity", "vrp_pickup_delivery", "vrp_drop_nodes"]

ORIGINAL_MAINS, REDONE_MAINS = import_examples_main(
    EXAMPLES_PKG, ORIGINAL_SUB, REDONE_SUB, EXAMPLE_NAMES
)

TEST_CASES_DATA = zip(EXAMPLE_NAMES, ORIGINAL_MAINS, REDONE_MAINS)


# Make empty TestCase class and add test methods programatically.
class CompareOutputsTestCase(TestCase):
    """Verify that original and redone examples have same output."""


def compare_outputs(test_case: TestCase, callable_0, callable_1):
    """
    Verify that the outputs of two functions are the same.

    This is intended to be used as a method of a TestCase subclass.
    """
    c0_lines = capture_lines(callable_0)
    c1_lines = capture_lines(callable_1)
    test_case.assertEqual(c0_lines, c1_lines)


# Add test methods programatically to CompareOutputsTestCase.
for name, original_main, redone_main in TEST_CASES_DATA:
    # Make method
    method = partialmethod(
        compare_outputs, callable_0=original_main, callable_1=redone_main
    )
    # Add method
    setattr(CompareOutputsTestCase, "test_" + name, method)
