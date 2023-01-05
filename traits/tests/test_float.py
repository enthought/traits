# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Tests for the Float trait type.

"""
import unittest

from traits.api import BaseFloat, Either, Float, HasTraits, Str, TraitError
from traits.testing.optional_dependencies import numpy, requires_numpy


class IntegerLike:
    def __init__(self, value):
        self._value = value

    def __index__(self):
        return self._value


# Python versions < 3.8 don't support conversion of something with __index__
# to float.
try:
    float(IntegerLike(3))
except TypeError:
    float_accepts_index = False
else:
    float_accepts_index = True


class MyFloat(object):
    def __init__(self, value):
        self._value = value

    def __float__(self):
        return self._value


class InheritsFromFloat(float):
    pass


class BadFloat(object):
    def __float__(self):
        raise ZeroDivisionError


class FloatModel(HasTraits):
    value = Float

    # Assignment to the `Either` trait exercises a different C code path (see
    # validate_trait_complex in ctraits.c).
    value_or_none = Either(None, Float)

    float_or_text = Either(Float, Str)


class BaseFloatModel(HasTraits):
    value = BaseFloat

    value_or_none = Either(None, BaseFloat)

    float_or_text = Either(Float, Str)


class CommonFloatTests(object):
    """ Common tests for Float and BaseFloat """

    def test_default(self):
        a = self.test_class()
        self.assertEqual(a.value, 0.0)

    def test_accepts_float(self):
        a = self.test_class()

        a.value = 5.6
        self.assertIs(type(a.value), float)
        self.assertEqual(a.value, 5.6)

        a.value_or_none = 5.6
        self.assertIs(type(a.value_or_none), float)
        self.assertEqual(a.value_or_none, 5.6)

    def test_accepts_float_subclass(self):
        a = self.test_class()

        a.value = InheritsFromFloat(37.0)
        self.assertIs(type(a.value), float)
        self.assertEqual(a.value, 37.0)

        a.value_or_none = InheritsFromFloat(37.0)
        self.assertIs(type(a.value), float)
        self.assertEqual(a.value, 37.0)

    def test_accepts_int(self):
        a = self.test_class()

        a.value = 2
        self.assertIs(type(a.value), float)
        self.assertEqual(a.value, 2.0)

        a.value_or_none = 2
        self.assertIs(type(a.value_or_none), float)
        self.assertEqual(a.value_or_none, 2.0)

    @unittest.skipUnless(
        float_accepts_index,
        "float does not support __index__ for this Python version",
    )
    def test_accepts_integer_like(self):
        a = self.test_class()
        a.value = IntegerLike(3)
        self.assertIs(type(a.value), float)
        self.assertEqual(a.value, 3.0)

    def test_accepts_float_like(self):
        a = self.test_class()

        a.value = MyFloat(1729.0)
        self.assertIs(type(a.value), float)
        self.assertEqual(a.value, 1729.0)

        a.value = MyFloat(594.0)
        self.assertIs(type(a.value), float)
        self.assertEqual(a.value, 594.0)

    def test_rejects_string(self):
        a = self.test_class()
        with self.assertRaises(TraitError):
            a.value = "2.3"
        with self.assertRaises(TraitError):
            a.value_or_none = "2.3"

    def test_bad_float_exceptions_propagated(self):
        a = self.test_class()
        with self.assertRaises(ZeroDivisionError):
            a.value = BadFloat()

    def test_compound_trait_float_conversion_fail(self):
        # Check that a failure to convert to float doesn't terminate
        # an assignment to a compound trait.
        a = self.test_class()
        a.float_or_text = "not a float"
        self.assertEqual(a.float_or_text, "not a float")

    def test_accepts_small_integer(self):
        a = self.test_class()
        a.value = 2
        self.assertIs(type(a.value), float)
        self.assertEqual(a.value, 2.0)

        a.value_or_none = 2
        self.assertIs(type(a.value_or_none), float)
        self.assertEqual(a.value_or_none, 2.0)

    def test_accepts_large_integer(self):
        a = self.test_class()

        a.value = 2 ** 64
        self.assertIs(type(a.value), float)
        self.assertEqual(a.value, 2 ** 64)

        a.value_or_none = 2 ** 64
        self.assertIs(type(a.value_or_none), float)
        self.assertEqual(a.value_or_none, 2 ** 64)

    @requires_numpy
    def test_accepts_numpy_floats(self):
        test_values = [
            numpy.float64(2.3),
            numpy.float32(3.7),
            numpy.float16(1.28),
        ]
        a = self.test_class()
        for test_value in test_values:
            a.value = test_value
            self.assertIs(type(a.value), float)
            self.assertEqual(a.value, test_value)

            a.value_or_none = test_value
            self.assertIs(type(a.value_or_none), float)
            self.assertEqual(a.value_or_none, test_value)


class TestFloat(unittest.TestCase, CommonFloatTests):
    def setUp(self):
        self.test_class = FloatModel

    def test_exceptions_propagate_in_compound_trait(self):
        # This test doesn't currently pass for BaseFloat, which is why it's not
        # in the common tests. That's probably a bug.
        a = self.test_class()
        with self.assertRaises(ZeroDivisionError):
            a.value_or_none = BadFloat()


class TestBaseFloat(unittest.TestCase, CommonFloatTests):
    def setUp(self):
        self.test_class = BaseFloatModel
