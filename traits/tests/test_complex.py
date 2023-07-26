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
Tests for the Complex trait type.
"""

import unittest

from traits.api import BaseComplex, Complex, Either, HasTraits, TraitError
from traits.testing.optional_dependencies import numpy, requires_numpy


class IntegerLike:
    def __init__(self, value):
        self._value = value

    def __index__(self):
        return self._value


# Python versions < 3.8 don't support conversion of something with __index__
# to complex.
try:
    complex(IntegerLike(3))
except TypeError:
    complex_accepts_index = False
else:
    complex_accepts_index = True


class FloatLike:
    def __init__(self, value):
        self._value = value

    def __float__(self):
        return self._value


class ComplexLike:
    def __init__(self, value):
        self._value = value

    def __complex__(self):
        return self._value


class HasComplexTraits(HasTraits):
    value = Complex()

    # Assignment to the `Either` trait exercises a different C code path (see
    # validate_trait_complex in ctraits.c). This use of "Either" should not
    # be replaced with "Union", since "Union" does not exercise that same
    # code path.
    value_or_none = Either(None, Complex())


class HasBaseComplexTraits(HasTraits):
    value = BaseComplex()

    value_or_none = Either(None, BaseComplex())


class CommonComplexTests(object):
    """ Common tests for Complex and BaseComplex. """

    def test_default_value(self):
        a = self.test_class()
        self.assertIs(type(a.value), complex)
        self.assertEqual(a.value, complex(0.0, 0.0))

    def test_rejects_str(self):
        a = self.test_class()
        with self.assertRaises(TraitError):
            a.value = "3j"

    def test_accepts_int(self):
        a = self.test_class()
        a.value = 7
        self.assertIs(type(a.value), complex)
        self.assertEqual(a.value, complex(7.0, 0.0))

    def test_accepts_float(self):
        a = self.test_class()
        a.value = 7.0
        self.assertIs(type(a.value), complex)
        self.assertEqual(a.value, complex(7.0, 0.0))

    def test_accepts_complex(self):
        a = self.test_class()
        a.value = 7j
        self.assertIs(type(a.value), complex)
        self.assertEqual(a.value, complex(0.0, 7.0))

    def test_accepts_complex_subclass(self):
        class ComplexSubclass(complex):
            pass

        a = self.test_class()
        a.value = ComplexSubclass(5.0, 12.0)
        self.assertIs(type(a.value), complex)
        self.assertEqual(a.value, complex(5.0, 12.0))

    @unittest.skipUnless(
        complex_accepts_index,
        "complex does not support __index__ for this Python version",
    )
    def test_accepts_integer_like(self):
        a = self.test_class()
        a.value = IntegerLike(3)
        self.assertIs(type(a.value), complex)
        self.assertEqual(a.value, complex(3.0, 0.0))

    def test_accepts_float_like(self):
        a = self.test_class()
        a.value = FloatLike(3.2)
        self.assertIs(type(a.value), complex)
        self.assertEqual(a.value, complex(3.2, 0.0))

    def test_accepts_complex_like(self):
        a = self.test_class()
        a.value = ComplexLike(3.0 + 4j)
        self.assertIs(type(a.value), complex)
        self.assertEqual(a.value, complex(3.0, 4.0))

    @requires_numpy
    def test_accepts_numpy_values(self):
        test_values = [
            numpy.int32(23),
            numpy.float32(3.7),
            numpy.float64(2.3),
            numpy.complex64(1.2 - 3.8j),
            numpy.complex128(3.1 + 4.7j),
        ]
        for value in test_values:
            with self.subTest(value=value):
                a = self.test_class()
                a.value = value
                self.assertIs(type(a.value), complex)
                self.assertEqual(a.value, complex(value))

    def test_validate_trait_complex_code_path(self):
        a = self.test_class()
        a.value_or_none = 3.0 + 4j
        self.assertIs(type(a.value_or_none), complex)
        self.assertEqual(a.value_or_none, complex(3.0, 4.0))

    def test_exceptions_propagated(self):
        class CustomException(Exception):
            pass

        class BadComplexLike:
            def __complex__(self):
                raise CustomException("something went wrong")

        a = self.test_class()
        with self.assertRaises(CustomException):
            a.value = BadComplexLike()


class TestComplex(unittest.TestCase, CommonComplexTests):
    def setUp(self):
        self.test_class = HasComplexTraits


class TestBaseComplex(unittest.TestCase, CommonComplexTests):
    def setUp(self):
        self.test_class = HasBaseComplexTraits
