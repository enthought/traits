# ------------------------------------------------------------------------------
# Copyright (c) 2005-2014, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in /LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# ------------------------------------------------------------------------------

""" A decorator for marking methods/functions as deprecated. """

# Standard library imports.
import functools
import warnings


def deprecated(message):
    """ A factory for decorators for marking methods/functions as deprecated.

    """

    def decorator(fn):
        """ A decorator for marking methods/functions as deprecated. """

        @functools.wraps(fn)
        def wrapper(*args, **kw):
            """ The method/function wrapper. """

            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return fn(*args, **kw)

        return wrapper

    return decorator
