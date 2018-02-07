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

from ..api import HasTraits, Int, Range, Str, TraitError


class SimpleFloatRange(HasTraits):
    r = Range(0.0, 100.0)

    r_open_on_right = Range(0.0, 100.0, exclude_low=False, exclude_high=True)
    r_open_on_left = Range(0.0, 100.0, exclude_low=True, exclude_high=False)
    r_open = Range(0.0, 100.0, exclude_low=True, exclude_high=True)
    r_closed = Range(0.0, 100.0, exclude_low=False, exclude_high=False)

    r_nonnegative = Range(0.0, None)
    r_nonpositive = Range(None, 0.0)


class SimpleIntRange(HasTraits):
    r = Range(0, 100)

    r_open_on_right = Range(0, 100, exclude_low=False, exclude_high=True)
    r_open_on_left = Range(0, 100, exclude_low=True, exclude_high=False)
    r_open = Range(0, 100, exclude_low=True, exclude_high=True)
    r_closed = Range(0, 100, exclude_low=False, exclude_high=False)

    r_nonnegative = Range(0, None)
    r_nonpositive = Range(None, 0)


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
        obj = SimpleFloatRange()

        good_values = [
            1.47,
            MyFloat(2.35),
            23, 0, 100,
            23.5, 0.0, 100.0,
        ]

        if numpy_available:
            numpy_good_values = [
                numpy.float64(1.1),
                numpy.float32(1.78),
                numpy.float16(3.7),
                numpy.int8(23),
                numpy.uint8(24),
                numpy.int32(26),
                numpy.uint64(27),
            ]
            good_values.extend(numpy_good_values)

        for good_value in good_values:
            obj.r = good_value
            self.assertIs(type(obj.r), float)
            self.assertEqual(obj.r, float(good_value))

        bad_values = [
            "a string",
            1 + 2j,
            -50.0,  # out of range
            150.0,  # also out of range
            -50,
            150,
            MyIntLike(17),
        ]

        for bad_value in bad_values:
            with self.assertRaises(TraitError):
                obj.r = bad_value

    def test_type_validation_int_range(self):
        obj = SimpleIntRange()

        good_values = [23, 0, 100, MyIntLike(17)]

        if numpy_available:
            good_values.extend([
                numpy.int8(23),
                numpy.uint8(24),
                numpy.int32(26),
                numpy.uint64(27),
            ])

        for good_value in good_values:
            obj.r = good_value
            self.assertIs(type(obj.r), int)
            self.assertEqual(obj.r, operator.index(good_value))

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
            numpy_bad_values = [
                numpy.float64(1.1),
                numpy.float32(1.78),
                numpy.float16(3.7),
            ]
            bad_values.extend(numpy_bad_values)

        for bad_value in bad_values:
            with self.assertRaises(TraitError):
                obj.r = bad_value

    def test_bounds_exclusion_int_range(self):
        obj = SimpleIntRange()

        obj.r_open_on_right = 0
        self.assertEqual(obj.r_open_on_right, 0)
        with self.assertRaises(TraitError):
            obj.r_open_on_right = 100

        with self.assertRaises(TraitError):
            obj.r_open_on_left = 0
        obj.r_open_on_left = 100
        self.assertEqual(obj.r_open_on_left, 100)

        with self.assertRaises(TraitError):
            obj.r_open = 0
        with self.assertRaises(TraitError):
            obj.r_open = 100

        obj.r_closed = 0
        self.assertEqual(obj.r_closed, 0)
        obj.r_closed = 100
        self.assertEqual(obj.r_closed, 100)

        obj.r_nonnegative = 10**100
        self.assertEqual(obj.r_nonnegative, 10**100)
        with self.assertRaises(TraitError):
            obj.r_nonnegative = -10**100

        with self.assertRaises(TraitError):
            obj.r_nonpositive = 10**100
        obj.r_nonpositive = -10**100
        self.assertEqual(obj.r_nonpositive, -10**100)

        # Default case: both bounds included.
        obj.r = 0
        self.assertEqual(obj.r, 0)
        obj.r = 100
        self.assertEqual(obj.r, 100)

    def test_bounds_exclusion_float_range(self):
        obj = SimpleFloatRange()

        obj.r_open_on_right = 0.0
        self.assertEqual(obj.r_open_on_right, 0.0)
        with self.assertRaises(TraitError):
            obj.r_open_on_right = 100.0

        with self.assertRaises(TraitError):
            obj.r_open_on_left = 0.0
        obj.r_open_on_left = 100.0
        self.assertEqual(obj.r_open_on_left, 100.0)

        with self.assertRaises(TraitError):
            obj.r_open = 0.0
        with self.assertRaises(TraitError):
            obj.r_open = 100.0

        obj.r_closed = 0.0
        self.assertEqual(obj.r_closed, 0.0)
        obj.r_closed = 100.0
        self.assertEqual(obj.r_closed, 100.0)

        obj.r_nonnegative = 1e100
        self.assertEqual(obj.r_nonnegative, 1e100)
        with self.assertRaises(TraitError):
            obj.r_nonnegative = -1e100

        with self.assertRaises(TraitError):
            obj.r_nonpositive = 1e100
        obj.r_nonpositive = -1e100
        self.assertEqual(obj.r_nonpositive, -1e100)

        # Default case: both bounds included.
        obj.r = 0.0
        self.assertEqual(obj.r, 0.0)
        obj.r = 100.0
        self.assertEqual(obj.r, 100.0)
