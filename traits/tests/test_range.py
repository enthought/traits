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

def hastraits_range_class(range_factory, low, high):
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


SimpleFloatRange = hastraits_range_class(Range, 0.0, 100.0)
SimpleIntRange = hastraits_range_class(Range, 0, 100)
SimpleFloatBaseRange = hastraits_range_class(BaseRange, 0.0, 100.0)
SimpleIntBaseRange = hastraits_range_class(BaseRange, 0, 100)

# The Either(None, Range) traits exercise a different code-path in ctraits.c:
# see validate_trait_complex.
CompoundFloatRange = hastraits_range_class(
    lambda *args, **kwargs: Either(None, Range(*args, **kwargs)),
    0.0, 100.0,
)
CompoundIntRange = hastraits_range_class(
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

    r_high_dynamic = Range(value='value', low=0, high='high')

    r_low_dynamic = Range(value='value', low='low', high=10.0)


class FloatLike(object):
    """
    Object coercable to a float via __float__.
    """
    def __init__(self, value):
        self._value = value

    def __float__(self):
        return float(self._value)


class IntLike(object):
    """
    Object coercable to an int via __index__.
    """
    def __init__(self, value):
        self._value = value

    def __index__(self):
        return int(operator.index(self._value))


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
            FloatLike(2.35),
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
            IntLike(17),
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
        good_values = [23, 0, 100, IntLike(17), True]
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
            FloatLike(2.35),
            -50,  # out of range
            150,  # also out of range
            IntLike(127),
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

    def test_value_type_inference(self):
        self.assertIsIntRange(Range(2, 3))
        self.assertIsFloatRange(Range(2, 3.0))
        self.assertIsFloatRange(Range(2.0, 3))
        self.assertIsFloatRange(Range(2.0, 3.0))
        self.assertIsIntRange(Range(None, 3))
        self.assertIsIntRange(Range(2, None))
        self.assertIsFloatRange(Range(None, 3.0))
        self.assertIsFloatRange(Range(2.0, None))

        # The type of the default value doesn't get taken into account
        self.assertIsIntRange(Range(2, 4, 3.0))

        # It's illegal to fail to give either bound, or to use non-inty
        # and non-floaty bounds.
        with self.assertRaises(TraitError):
            Range(None, None)

        with self.assertRaises(TraitError):
            Range(5.6, 1+2j)
        with self.assertRaises(TraitError):
            Range((1, 2), None)
        with self.assertRaises(TraitError):
            Range(IntLike(23), FloatLike(45.0))
        with self.assertRaises(TraitError):
            Range(FloatLike(23.0), IntLike(45))

    def test_static_validation_bounds_conversion(self):
        r = Range(IntLike(23), IntLike(45))
        self.assertIsIntRange(r)
        self.assertIs(type(r._low), int)
        self.assertEqual(r._low, 23)
        self.assertIs(type(r._high), int)
        self.assertEqual(r._high, 45)

        r = Range(None, IntLike(45))
        self.assertIsIntRange(r)
        self.assertIs(r._low, None)
        self.assertIs(type(r._high), int)
        self.assertEqual(r._high, 45)

        r = Range(IntLike(23), None)
        self.assertIsIntRange(r)
        self.assertIs(type(r._low), int)
        self.assertEqual(r._low, 23)
        self.assertIs(r._high, None)

        r = Range(FloatLike(23.0), FloatLike(45.0))
        self.assertIsFloatRange(r)
        self.assertIs(type(r._low), float)
        self.assertEqual(r._low, 23.0)
        self.assertIs(type(r._high), float)
        self.assertEqual(r._high, 45.0)

        r = Range(None, FloatLike(45.0))
        self.assertIsFloatRange(r)
        self.assertIs(r._low, None)
        self.assertIs(type(r._high), float)
        self.assertEqual(r._high, 45.0)

        r = Range(FloatLike(23.0), None)
        self.assertIsFloatRange(r)
        self.assertIs(type(r._low), float)
        self.assertEqual(r._low, 23.0)
        self.assertIs(r._high, None)

        r = Range(23, FloatLike(45.0))
        self.assertIsFloatRange(r)
        self.assertIs(type(r._low), float)
        self.assertEqual(r._low, 23.0)
        self.assertIs(type(r._high), float)
        self.assertEqual(r._high, 45.0)

        r = Range(FloatLike(23.0), 45)
        self.assertIsFloatRange(r)
        self.assertIs(type(r._low), float)
        self.assertEqual(r._low, 23.0)
        self.assertIs(type(r._high), float)
        self.assertEqual(r._high, 45.0)

    def test_semi_dynamic_range(self):
        obj = WithDynamicRange()
        obj.r_high_dynamic = 5
        self.assertEqual(obj.r_high_dynamic, 5)
        # Current range is [0, 10]
        with self.assertRaises(TraitError):
            obj.r_high_dynamic = -10
        with self.assertRaises(TraitError):
            obj.r_high_dynamic = 15

        # Change the upper limit.
        obj.high = 20
        obj.r_high_dynamic = 15
        self.assertEqual(obj.r_high_dynamic, 15)
        with self.assertRaises(TraitError):
            obj.r_high_dynamic = 25

        obj = WithDynamicRange()
        obj.r_low_dynamic = 5.0
        self.assertEqual(obj.r_low_dynamic, 5.0)
        # Current range is [0.0, 10.0]
        with self.assertRaises(TraitError):
            obj.r_low_dynamic = -5.0
        with self.assertRaises(TraitError):
            obj.r_low_dynamic = 15.0

        obj.low = -10
        obj.r_low_dynamic = -5.0
        self.assertEqual(obj.r_low_dynamic, -5.0)
        with self.assertRaises(TraitError):
            obj.r_low_dynamic = -15.0

    # assertions and helper methods

    def assertIsIntRange(self, range):
        """
        Assert that the given range is static and integer-based.
        """
        self.assertEqual(range._validate, "integer_validate")

    def assertIsFloatRange(self, range):
        """
        Assert that the given range is static and float-based.
        """
        self.assertEqual(range._validate, "float_validate")

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
