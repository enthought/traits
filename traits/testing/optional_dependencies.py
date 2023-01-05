# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import importlib
import unittest


def optional_import(name):
    """
    Optionally import a module, returning None if that module is unavailable.

    Parameters
    ----------
    name : Str
        The name of the module being imported.

    Returns
    -------
    None or module
        None if the module is not available, and the module otherwise.

    """
    try:
        module = importlib.import_module(name)
    except ImportError:
        return None
    else:
        return module


# Commonly-used unittest skip decorators.
cython = optional_import("cython")
requires_cython = unittest.skipIf(cython is None, "Cython not available")

mypy = optional_import("mypy")
requires_mypy = unittest.skipIf(mypy is None, "Mypy not available")

numpy = optional_import("numpy")
requires_numpy = unittest.skipIf(numpy is None, "NumPy not available")

numpy_typing = optional_import("numpy.typing")
requires_numpy_typing = unittest.skipIf(
    numpy_typing is None, "numpy.typing not available")

pkg_resources = optional_import("pkg_resources")
requires_pkg_resources = unittest.skipIf(
    pkg_resources is None, "pkg_resources not available"
)

pyface = optional_import("pyface")
requires_pyface = unittest.skipIf(pyface is None, "Pyface not available")

sphinx = optional_import("sphinx")
requires_sphinx = unittest.skipIf(sphinx is None, "Sphinx not available")

traitsui = optional_import("traitsui")
requires_traitsui = unittest.skipIf(traitsui is None, "TraitsUI not available")
# Import traitsui.api so that client code can use traitsui.api directly without
# an extra import.
if traitsui is not None:
    import traitsui.api
