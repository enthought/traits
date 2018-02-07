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
import sys

try:
    import numpy
except ImportError:
    numpy_available = False
else:
    numpy_available = True

from traits.testing.unittest_tools import unittest

from ..api import BaseFloat, Either, Float, HasTraits, TraitError


class MyFloat(object):
    def __init__(self, value):
        self._value = value

    def __float__(self):
        return self._value


class FloatModel(HasTraits):
    value = Float

    # Assignment to the `Either` trait exercises a different C code path (see
    # validate_trait_complex in ctraits.c).
    value_or_none = Either(None, Float)


class BaseFloatModel(HasTraits):
    value = BaseFloat

    value_or_none = Either(None, BaseFloat)


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

    def test_rejects_string(self):
        a = self.test_class()
        with self.assertRaises(TraitError):
            a.value = "2.3"
        with self.assertRaises(TraitError):
            a.value_or_none = "2.3"

    def test_accepts_float_like(self):
        a = self.test_class()

        a.value = MyFloat(1729.0)
        self.assertIs(type(a.value), float)
        self.assertEqual(a.value, 1729.0)

        a.value = MyFloat(594.0)
        self.assertIs(type(a.value), float)
        self.assertEqual(a.value, 594.0)

    @unittest.skipUnless(sys.version_info < (3,), "Not applicable to Python 3")
    def test_accepts_small_long(self):
        a = self.test_class()

        a.value = long(2)
        self.assertIs(type(a.value), float)
        self.assertEqual(a.value, 2.0)

        a.value_or_none = long(2)
        self.assertIs(type(a.value_or_none), float)
        self.assertEqual(a.value_or_none, 2.0)

    @unittest.skipUnless(sys.version_info < (3,), "Not applicable to Python 3")
    def test_accepts_large_long(self):
        a = self.test_class()

        # Value large enough to be a long on Python 2.
        a.value = 2**64
        self.assertIs(type(a.value), float)
        self.assertEqual(a.value, 2**64)

        a.value_or_none = 2**64
        self.assertIs(type(a.value_or_none), float)
        self.assertEqual(a.value_or_none, 2**64)

    @unittest.skipUnless(numpy_available, "Test requires NumPy")
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


class TestBaseFloat(unittest.TestCase, CommonFloatTests):
    def setUp(self):
        self.test_class = BaseFloatModel
