# ------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in /LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# ------------------------------------------------------------------------------

from __future__ import absolute_import

import unittest

try:
    import numpy
except ImportError:
    numpy_available = False
else:
    numpy_available = True

from traits.api import Array, Bool, HasTraits


if numpy_available:
    # Use of `Array` requires NumPy to be installed.

    class Foo(HasTraits):
        a = Array()
        event_fired = Bool(False)

        def _a_changed(self):
            self.event_fired = True


class ArrayTestCase(unittest.TestCase):
    """ Test cases for delegated traits. """

    @unittest.skipUnless(numpy_available, "numpy not available")
    def test_zero_to_one_element(self):
        """ Test that an event fires when an Array trait changes from zero to
        one element.
        """

        f = Foo()
        f.a = numpy.zeros((2,), float)
        f.event_fired = False

        # Change the array.
        f.a = numpy.concatenate((f.a, numpy.array([100])))

        # Confirm that the static trait handler was invoked.
        self.assertEqual(f.event_fired, True)

        return
