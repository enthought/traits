# ------------------------------------------------------------------------------
#
#  Copyright (c) 2014, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
# ------------------------------------------------------------------------------
"""
Tests for the ArrayOrNone TraitType.

"""

from __future__ import absolute_import

import unittest

from traits.api import ArrayOrNone, HasTraits, NO_COMPARE, TraitError
from traits.testing.unittest_tools import UnittestTools
from traits.testing.optional_dependencies import numpy, requires_numpy


if numpy is not None:
    # Use of `ArrayOrNone` requires NumPy to be installed.

    class Foo(HasTraits):
        maybe_array = ArrayOrNone

        maybe_float_array = ArrayOrNone(dtype=float)

        maybe_two_d_array = ArrayOrNone(shape=(None, None))

        maybe_array_with_default = ArrayOrNone(value=[1, 2, 3])

        maybe_array_no_compare = ArrayOrNone(comparison_mode=NO_COMPARE)


@requires_numpy
class TestArrayOrNone(unittest.TestCase, UnittestTools):
    """
    Tests for the ArrayOrNone TraitType.

    """

    def test_default(self):
        foo = Foo()
        self.assertIsNone(foo.maybe_array)

    def test_explicit_default(self):
        foo = Foo()
        self.assertIsInstance(foo.maybe_array_with_default, numpy.ndarray)

    def test_default_validation(self):
        # CArray and Array validate the default at class creation time;
        # we do the same for ArrayOrNone.
        with self.assertRaises(TraitError):

            class Bar(HasTraits):
                bad_array = ArrayOrNone(shape=(None, None), value=[1, 2, 3])

    def test_setting_array_from_array(self):
        foo = Foo()
        test_array = numpy.arange(5)
        foo.maybe_array = test_array
        output_array = foo.maybe_array
        self.assertIsInstance(output_array, numpy.ndarray)
        self.assertEqual(output_array.dtype, test_array.dtype)
        self.assertEqual(output_array.shape, test_array.shape)
        self.assertTrue((output_array == test_array).all())

    def test_setting_array_from_list(self):
        foo = Foo()
        test_list = [5, 6, 7, 8, 9]
        foo.maybe_array = test_list
        output_array = foo.maybe_array
        self.assertIsInstance(output_array, numpy.ndarray)
        self.assertEqual(output_array.dtype, numpy.dtype(int))
        self.assertEqual(output_array.shape, (5,))
        self.assertTrue((output_array == test_list).all())

    def test_setting_array_from_none(self):
        foo = Foo()
        test_array = numpy.arange(5)

        self.assertIsNone(foo.maybe_array)
        foo.maybe_array = test_array
        self.assertIsInstance(foo.maybe_array, numpy.ndarray)
        foo.maybe_array = None
        self.assertIsNone(foo.maybe_array)

    def test_dtype(self):
        foo = Foo()
        foo.maybe_float_array = [1, 2, 3]

        array_value = foo.maybe_float_array
        self.assertIsInstance(array_value, numpy.ndarray)
        self.assertEqual(array_value.dtype, numpy.dtype(float))

    def test_shape(self):
        foo = Foo()
        with self.assertRaises(TraitError):
            foo.maybe_two_d_array = [1, 2, 3]

    def test_change_notifications(self):
        foo = Foo()
        test_array = numpy.arange(-7, -2)
        different_test_array = numpy.arange(10)

        # Assigning None to something that's already None shouldn't fire.
        with self.assertTraitDoesNotChange(foo, "maybe_array"):
            foo.maybe_array = None

        # Changing from None to an array: expect an event.
        with self.assertTraitChanges(foo, "maybe_array"):
            foo.maybe_array = test_array

        # No event from assigning the same array again.
        with self.assertTraitDoesNotChange(foo, "maybe_array"):
            foo.maybe_array = test_array

        # But assigning a new array fires an event.
        with self.assertTraitChanges(foo, "maybe_array"):
            foo.maybe_array = different_test_array

        # No event even if the array is modified in place.
        different_test_array += 2
        with self.assertTraitDoesNotChange(foo, "maybe_array"):
            foo.maybe_array = different_test_array

        # Set back to None; we should get an event.
        with self.assertTraitChanges(foo, "maybe_array"):
            foo.maybe_array = None

    def test_comparison_mode_override(self):
        foo = Foo()
        test_array = numpy.arange(-7, 2)

        with self.assertTraitChanges(foo, "maybe_array_no_compare"):
            foo.maybe_array_no_compare = None

        with self.assertTraitChanges(foo, "maybe_array_no_compare"):
            foo.maybe_array_no_compare = test_array

        with self.assertTraitChanges(foo, "maybe_array_no_compare"):
            foo.maybe_array_no_compare = test_array

    def test_default_value_copied(self):
        # Check that we don't share defaults.
        test_default = numpy.arange(100.0, 110.0)

        class FooBar(HasTraits):
            foo = ArrayOrNone(value=test_default)

            bar = ArrayOrNone(value=test_default)

        foo_bar = FooBar()

        self.assertTrue((foo_bar.foo == test_default).all())
        self.assertTrue((foo_bar.bar == test_default).all())

        test_default += 2.0
        self.assertFalse((foo_bar.foo == test_default).all())
        self.assertFalse((foo_bar.bar == test_default).all())

        foo = foo_bar.foo
        foo += 1729.0
        self.assertFalse((foo_bar.foo == foo_bar.bar).all())
