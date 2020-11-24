"""Function to import examples programatically."""
from importlib import import_module
from functools import partial


def _import_multiple_main(package_name, module_names):
    full_module_names = map(lambda x: ".".join([package_name, x]), module_names)
    modules = map(import_module, full_module_names)
    return list(map(lambda x: x.main, modules))


def import_examples_main(examples_pkg, original_sub, redone_sub, example_names):
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
