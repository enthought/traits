# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Non-standard functions for the 'nose' testing framework

This module is deprecated, and will be removed in a future release.

.. deprecated:: 6.1.0

"""

import warnings

try:
    from nose import DeprecatedTest, SkipTest
    from nose.tools import make_decorator

    def skip(f):
        """ Decorator to indicate a test should be skipped.

        .. deprecated:: 6.1.0

        """
        warnings.warn(
            "The traits.testing.nose_tools module and its contents "
            "are deprecated",
            DeprecationWarning,
            stacklevel=2,
        )

        def g(*args, **kw):
            raise SkipTest()

        return make_decorator(f)(g)

    def deprecated(f):
        """ Decorator to indicate a test is deprecated.

        .. deprecated:: 6.1.0

        """
        warnings.warn(
            "The traits.testing.nose_tools module and its contents "
            "are deprecated",
            DeprecationWarning,
            stacklevel=2,
        )

        def g(*args, **kw):
            raise DeprecatedTest()

        return make_decorator(f)(g)


except ImportError:
    # Define stubs in case nose isn't installed.

    def skip(f):
        """ Stub replacement for marking a unit test to be skipped in the
        absence of 'nose'.

        .. deprecated:: 6.1.0
        """
        warnings.warn(
            "The traits.testing.nose_tools module and its contents "
            "are deprecated",
            DeprecationWarning,
            stacklevel=2,
        )

        warnings.warn("skipping unit tests requires the package 'nose'")
        return f

    def deprecated(f):
        """ Stub replacement for marking a unit test deprecated in the absence
        of 'nose'.

        .. deprecated:: 6.1.0
        """
        warnings.warn(
            "The traits.testing.nose_tools module and its contents "
            "are deprecated",
            DeprecationWarning,
            stacklevel=2,
        )

        warnings.warn(
            "skipping deprecated unit tests requires the package 'nose'"
        )
        return f


def performance(f):
    """ Decorator to add an attribute to the test to mark it as
    a performance-measuring test.

    .. deprecated:: 6.1.0

    """
    warnings.warn(
        "The traits.testing.nose_tools module and its contents "
        "are deprecated",
        DeprecationWarning,
        stacklevel=2,
    )

    f.performance = True
    return f
