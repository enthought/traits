#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt

from __future__ import absolute_import

import operator

try:
    import numpy
except ImportError:
    numpy_available = False
else:
    numpy_available = True

from traits.testing.unittest_tools import unittest

from ..api import BaseRange, Either, HasTraits, Int, Range, Str, TraitError


# We need a lot of similar-looking test classes; use a factory to create them.

def range_test_class(range_factory, low, high):
    """
    Create a HasTraits subclass containing Range traits based
    on the given range_factory.
    """
    class RangeTestClass(HasTraits):
        r = range_factory(low, high)

        r_open_on_right = range_factory(
            low, high, exclude_low=False, exclude_high=True)
        r_open_on_left = range_factory(
            low, high, exclude_low=True, exclude_high=False)
        r_open = range_factory(
            low, high, exclude_low=True, exclude_high=True)
        r_closed = range_factory(
            low, high, exclude_low=False, exclude_high=False)
        r_bounded_below = range_factory(low, None, exclude_low=False)
        r_bounded_above = range_factory(None, high, exclude_high=False)

    return RangeTestClass


SimpleFloatRange = range_test_class(Range, 0.0, 100.0)
SimpleIntRange = range_test_class(Range, 0, 100)
SimpleFloatBaseRange = range_test_class(BaseRange, 0.0, 100.0)
SimpleIntBaseRange = range_test_class(BaseRange, 0, 100)

# The Either(None, Range) traits exercise a different code-path in ctraits.c:
# see validate_trait_complex.
CompoundFloatRange = range_test_class(
    lambda *args, **kwargs: Either(None, Range(*args, **kwargs)),
    0.0, 100.0,
)
CompoundIntRange = range_test_class(
    lambda *args, **kwargs: Either(None, Range(*args, **kwargs)),
    0, 100,
)


class WithFloatRange(HasTraits):
    r = Range(0.0, 100.0)
    r_copied_on_change = Str

    _changed_handler_calls = Int

    def _r_changed(self, old, new):
        self._changed_handler_calls += 1
        self.r_copied_on_change = str(self.r)

        if (self.r % 10) > 0:
            self.r += 10 - (self.r % 10)


class WithLargeIntRange(HasTraits):
    r = Range(0, 1000)
    r_copied_on_change = Str

    _changed_handler_calls = Int

    def _r_changed(self, old, new):
        self._changed_handler_calls += 1
        self.r_copied_on_change = str(self.r)

        if self.r > 100:
            self.r = 0


class WithDynamicRange(HasTraits):
    low = Int(0)
    high = Int(10)
    value = Int(3)

    r = Range(value='value', low='low', high='high', exclude_high=True)

    def _r_changed(self, old, new):
        self._changed_handler_calls += 1


class MyFloat(object):
    def __init__(self, value):
        self._value = value

    def __float__(self):
        return self._value


class MyIntLike(object):
    def __init__(self, value):
        self._value = value

    def __index__(self):
        return self._value


class RangeTestCase(unittest.TestCase):

    def test_non_ui_events(self):

        obj = WithFloatRange()
        obj._changed_handler_calls = 0

        obj.r = 10
        self.assertEqual(1, obj._changed_handler_calls)

        obj._changed_handler_calls = 0
        obj.r = 34.56
        self.assertEqual(obj._changed_handler_calls, 2)
        self.assertEqual(obj.r, 40)

    def test_non_ui_int_events(self):

        # Even though the range is configured for 0..1000, the handler resets
        # the value to 0 when it exceeds 100.
        obj = WithLargeIntRange()
        obj._changed_handler_calls = 0

        obj.r = 10
        self.assertEqual(obj._changed_handler_calls, 1)
        self.assertEqual(obj.r, 10)

        obj.r = 100
        self.assertEqual(obj._changed_handler_calls, 2)
        self.assertEqual(obj.r, 100)

        obj.r = 101
        self.assertEqual(obj._changed_handler_calls, 4)
        self.assertEqual(obj.r, 0)

    def test_dynamic_events(self):

        obj = WithDynamicRange()
        obj._changed_handler_calls = 0

        obj.r = 5
        self.assertEqual(obj._changed_handler_calls, 1)
        self.assertEqual(obj.r, 5)

        with self.assertRaises(TraitError):
            obj.r = obj.high
        self.assertEqual(obj.r, 5)

    def test_type_validation_float_range(self):
        good_values = [
            1.47,
            MyFloat(2.35),
            23, 0, 100,
            23.5, 0.0, 100.0,
            True,
        ]
        if numpy_available:
            good_values.extend([
                numpy.float16(1.1), numpy.float32(1.78), numpy.float64(3.7),
                numpy.int8(23), numpy.uint8(24),
                numpy.int16(25), numpy.uint16(26),
                numpy.int32(27), numpy.uint32(28),
                numpy.int64(29), numpy.uint64(30),
                numpy.bool_(True),
            ])

        bad_values = [
            "a string",
            1 + 2j, 0j,
            -50.0,  # out of range
            150.0,  # also out of range
            -50,
            150,
            MyIntLike(17),
        ]

        test_objects = [
            SimpleFloatRange(),
            CompoundFloatRange(),
            SimpleFloatBaseRange(),
        ]
        for obj in test_objects:
            for good_value in good_values:
                obj.r = good_value
                self.assertIs(type(obj.r), float)
                self.assertEqual(obj.r, float(good_value))
            for bad_value in bad_values:
                with self.assertRaises(TraitError):
                    obj.r = bad_value

    def test_type_validation_int_range(self):
        good_values = [23, 0, 100, MyIntLike(17), True]
        if numpy_available:
            good_values.extend([
                numpy.int8(23), numpy.uint8(24),
                numpy.int16(25), numpy.uint16(26),
                numpy.int32(27), numpy.uint32(28),
                numpy.int64(29), numpy.uint64(30),
                numpy.bool_(True),
            ])

        bad_values = [
            "a string",
            1 + 2j,
            -50.0,
            150.0,
            1.47,
            MyFloat(2.35),
            -50,  # out of range
            150,  # also out of range
            MyIntLike(127),
        ]
        if numpy_available:
            bad_values.extend([
                numpy.float16(1.1), numpy.float32(1.78), numpy.float64(3.7),
                numpy.complex_(1+0j),
            ])

        test_objects = [
            SimpleIntRange(),
            CompoundIntRange(),
            SimpleIntBaseRange(),
        ]
        for obj in test_objects:
            for good_value in good_values:
                obj.r = good_value
                self.assertIs(type(obj.r), int)
                self.assertEqual(obj.r, operator.index(good_value))
            for bad_value in bad_values:
                with self.assertRaises(TraitError):
                    obj.r = bad_value

    def test_bounds_exclusion_float_range(self):
        test_objects = [
            SimpleFloatRange(),
            CompoundFloatRange(),
            SimpleFloatBaseRange(),
        ]
        for obj in test_objects:
            self._check_bounds(obj, 0.0, 100.0)

    def test_bounds_exclusion_int_range(self):
        test_objects = [
            SimpleIntRange(),
            CompoundIntRange(),
            SimpleIntBaseRange(),
        ]
        for obj in test_objects:
            self._check_bounds(obj, 0, 100)

    def _check_bounds(self, obj, low, high):
        """
        Helper function to check bound validation.
        """
        obj.r_open_on_right = low
        self.assertEqual(obj.r_open_on_right, low)
        with self.assertRaises(TraitError):
            obj.r_open_on_right = high

        with self.assertRaises(TraitError):
            obj.r_open_on_left = low
        obj.r_open_on_left = high
        self.assertEqual(obj.r_open_on_left, high)

        with self.assertRaises(TraitError):
            obj.r_open = low
        with self.assertRaises(TraitError):
            obj.r_open = high

        obj.r_closed = low
        self.assertEqual(obj.r_closed, low)
        obj.r_closed = high
        self.assertEqual(obj.r_closed, high)

        obj.r_bounded_below = low
        self.assertEqual(obj.r_bounded_below, low)
        obj.r_bounded_below = low + 1000
        self.assertEqual(obj.r_bounded_below, low + 1000)
        with self.assertRaises(TraitError):
            obj.r_bounded_below = low - 1000

        obj.r_bounded_above = high
        self.assertEqual(obj.r_bounded_above, high)
        with self.assertRaises(TraitError):
            obj.r_bounded_above = high + 1000
        obj.r_bounded_above = high - 1000
        self.assertEqual(obj.r_bounded_above, high - 1000)

        # Default case: both bounds included.
        obj.r = low
        self.assertEqual(obj.r, low)
        obj.r = high
        self.assertEqual(obj.r, high)
