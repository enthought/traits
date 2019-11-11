# -----------------------------------------------------------------------------
#
#  Copyright (c) 2019, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
# -----------------------------------------------------------------------------

import importlib
import unittest


def import_handler(name):
    """
    Handle import errors if module is unavailable.

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
cython = import_handler("cython")
requires_cython = unittest.skipIf(cython is None, "Cython not available")

numpy = import_handler("numpy")
requires_numpy = unittest.skipIf(numpy is None, "NumPy not available")

sphinx = import_handler("sphinx")
requires_sphinx = unittest.skipIf(sphinx is None, "Sphinx not available")

traitsui = import_handler("traitsui")
requires_traitsui = unittest.skipIf(traitsui is None, "TraitsUI not available")
