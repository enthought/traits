# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.api import Array, Bool, HasTraits, TraitError
from traits.testing.optional_dependencies import numpy, requires_numpy


if numpy is not None:
    # Use of `Array` requires NumPy to be installed.

    class Foo(HasTraits):
        a = Array()
        event_fired = Bool(False)

        def _a_changed(self):
            self.event_fired = True


@requires_numpy
class ArrayTestCase(unittest.TestCase):
    """ Test cases for delegated traits. """

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

    def test_safe_casting(self):
        class Bar(HasTraits):
            unsafe_f32 = Array(dtype="float32")
            safe_f32 = Array(dtype="float32", casting="safe")

        f64 = numpy.array([1], dtype="float64")
        f32 = numpy.array([1], dtype="float32")

        b = Bar()

        b.unsafe_f32 = f32
        b.unsafe_f32 = f64
        b.safe_f32 = f32
        with self.assertRaises(TraitError):
            b.safe_f32 = f64
