"""
Veryfy same behavior of original and redone examples.

Test if the redone examples using this library has the same behavior of the original
examples from ortools by comparing the outputs of the functions.
"""
from unittest import TestCase
from importlib import import_module
from functools import partial, partialmethod
from ort_simpleroute._examples._capture_output import capture_lines


def _import_multiple_main(package_name, module_names):
    full_module_names = map(lambda x: ".".join([package_name, x]), module_names)
    modules = map(import_module, full_module_names)
    return list(map(lambda x: x.main, modules))


def _import_examples_main(examples_pkg, original_sub, redone_sub, example_names):
    """
    Import the main() function of sereral original and redone example modules.

    The main() functions are returned in two lists that contain the original main()s
    and the redone main()s respectively, and in the same order as the example_names
    were given.
    """
    package_names = tuple(
        map(lambda x: ".".join([examples_pkg, x]), [original_sub, redone_sub])
    )

    import_examples_from = partial(_import_multiple_main, module_names=example_names)
    original_mains, redone_mains = tuple(map(import_examples_from, package_names))

    return (original_mains, redone_mains)


EXAMPLES_PKG = "ort_simpleroute._examples"
ORIGINAL_SUB = "original"
REDONE_SUB = "redone"
EXAMPLE_NAMES = ["vrp_capacity", "vrp_pickup_delivery"]

ORIGINAL_MAINS, REDONE_MAINS = _import_examples_main(
    EXAMPLES_PKG, ORIGINAL_SUB, REDONE_SUB, EXAMPLE_NAMES
)


def compare_outputs(test_case: TestCase, callable_0, callable_1):
    """
    Verify that the output of two functions is the same.

    This is intended to be used as a method of a TestCase subclass.
    """
    c0_lines = capture_lines(callable_0)
    c1_lines = capture_lines(callable_1)
    test_case.assertEqual(c0_lines, c1_lines)


class CompareOutputsTestCase(TestCase):
    """Verify that original and redone examples have same output."""


for name, original_main, redone_main in zip(
    EXAMPLE_NAMES, ORIGINAL_MAINS, REDONE_MAINS
):
    method = partialmethod(
        compare_outputs, callable_0=original_main, callable_1=redone_main
    )
    setattr(CompareOutputsTestCase, "test_" + name, method)
