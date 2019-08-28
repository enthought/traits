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


def import_handler(name):
    """
    Handle import errors if module is unavailable.

    Parameters
    ----------
    name : Str
        The name of the module being imported, lower case.

    Returns
    -------
    Tuple(Bool, None/module)
        Tuple containing a bool (whether or not a module is available) and the
        module object itself.

    """
    try:
        module = importlib.import_module(name)
        return True, module

    except ImportError:
        return False, None
