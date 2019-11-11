# -----------------------------------------------------------------------------
#
#  Copyright (c) 2015, Enthought, Inc.
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
"""
Tests for the Float trait type.

"""
import unittest

import six

from traits.api import BaseFloat, Either, Float, HasTraits, TraitError, Unicode
from traits.testing.optional_dependencies import (
    numpy, requires_numpy, requires_python2)

if six.PY2:
    LONG_TYPE = long
else:
    LONG_TYPE = int


class MyFloat(object):
    def __init__(self, value):
        self._value = value

    def __float__(self):
        return self._value


class BadFloat(object):
    def __float__(self):
        raise ZeroDivisionError


class FloatModel(HasTraits):
    value = Float

    # Assignment to the `Either` trait exercises a different C code path (see
    # validate_trait_complex in ctraits.c).
    value_or_none = Either(None, Float)

    float_or_text = Either(Float, Unicode)


class BaseFloatModel(HasTraits):
    value = BaseFloat

    value_or_none = Either(None, BaseFloat)

    float_or_text = Either(Float, Unicode)


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

    def test_accepts_int(self):
        a = self.test_class()

        a.value = 2
        self.assertIs(type(a.value), float)
        self.assertEqual(a.value, 2.0)

        a.value_or_none = 2
        self.assertIs(type(a.value_or_none), float)
        self.assertEqual(a.value_or_none, 2.0)

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
        a.float_or_text = u"not a float"
        self.assertEqual(a.float_or_text, u"not a float")

    @requires_python2
    def test_accepts_small_long(self):
        a = self.test_class()
        a.value = LONG_TYPE(2)
        self.assertIs(type(a.value), float)
        self.assertEqual(a.value, 2.0)

        a.value_or_none = LONG_TYPE(2)
        self.assertIs(type(a.value_or_none), float)
        self.assertEqual(a.value_or_none, 2.0)

    @requires_python2
    def test_accepts_large_long(self):
        a = self.test_class()

        # Value large enough to be a long on Python 2.
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
