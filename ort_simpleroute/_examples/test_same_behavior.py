import sys
from io import StringIO
from unittest import TestCase
from importlib import import_module
from functools import partial, partialmethod


def _import_multiple_main(package_name, module_names):
    full_module_names = map(lambda x: ".".join([package_name, x]), module_names)
    modules = map(import_module, full_module_names)
    return list(map(lambda x: x.main, modules))


def import_examples_main(examples_pkg, original_sub, redone_sub, example_names):
    package_names = tuple(
        map(lambda x: ".".join([examples_pkg, x]), [original_sub, redone_sub])
    )

    import_examples_from = partial(_import_multiple_main, module_names=example_names)
    original_mains, redone_mains = tuple(map(import_examples_from, package_names))

    return (original_mains, redone_mains)


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio
        sys.stdout = self._stdout


def capture_lines(function):
    with Capturing() as output:
        function()
    return output


examples_pkg = "ort_simpleroute._examples"
original_sub = "original"
redone_sub = "redone"
example_names = ["vrp_capacity", "vrp_pickup_delivery"]

original_mains, redone_mains = import_examples_main(
    examples_pkg, original_sub, redone_sub, example_names
)


def compare_outputs(test_case, callable_0, callable_1):
    c0_lines = capture_lines(callable_0)
    c1_lines = capture_lines(callable_1)
    test_case.assertEqual(c0_lines, c1_lines)


class CompareOutputsTestCase(TestCase):
    pass


for name, original_main, redone_main in zip(
    example_names, original_mains, redone_mains
):
    method = partialmethod(
        compare_outputs, callable_0=original_main, callable_1=redone_main
    )
    setattr(CompareOutputsTestCase, "test_" + name, method)
