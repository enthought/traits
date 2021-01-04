# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Tests for the Int trait type.

"""

import decimal
import sys
import unittest

from traits.api import Either, HasTraits, Int, CInt, TraitError
from traits.testing.optional_dependencies import numpy, requires_numpy


class A(HasTraits):
    integral = Int

    convertible = CInt

    convertible_or_none = Either(None, CInt)


class IntegerLike(object):
    def __index__(self):
        return 42


class Truncatable(object):
    def __int__(self):
        return 42


class TestInt(unittest.TestCase):
    def test_default(self):
        a = A()
        self.assertEqual(a.integral, 0)
        self.assertIs(type(a.integral), int)

    def test_accepts_int(self):
        a = A()
        a.integral = 23
        self.assertEqual(a.integral, 23)
        self.assertIs(type(a.integral), int)

    def test_accepts_large_integer(self):
        size_limit = sys.maxsize
        a = A()
        a.integral = size_limit
        self.assertEqual(a.integral, size_limit)
        self.assertIs(type(a.integral), int)

        a.integral = size_limit + 1
        self.assertEqual(a.integral, size_limit + 1)
        self.assertIs(type(a.integral), int)

        a.integral = 2**2048 + 1
        self.assertEqual(a.integral, 2**2048 + 1)
        self.assertIs(type(a.integral), int)

    def test_accepts_bool(self):
        a = A()
        a.integral = True
        self.assertEqual(a.integral, 1)
        self.assertIs(type(a.integral), int)

    def test_respects_dunder_index(self):
        a = A()
        a.integral = IntegerLike()
        self.assertEqual(a.integral, 42)
        self.assertIs(type(a.integral), int)

    def test_rejects_dunder_int(self):
        a = A()
        with self.assertRaises(TraitError):
            a.integral = Truncatable()

    def test_rejects_floating_point_types(self):
        a = A()
        with self.assertRaises(TraitError):
            a.integral = 23.0
        with self.assertRaises(TraitError):
            a.integral = decimal.Decimal(23)

    def test_rejects_string(self):
        a = A()
        with self.assertRaises(TraitError):
            a.integral = "23"

    @requires_numpy
    def test_numpy_types(self):
        a = A()
        a.integral = numpy.int32(23)
        self.assertEqual(a.integral, 23)
        self.assertIs(type(a.integral), int)

        a.integral = numpy.uint64(2 ** 63 + 2)
        self.assertEqual(a.integral, 2 ** 63 + 2)
        self.assertIs(type(a.integral), int)

        with self.assertRaises(TraitError):
            a.integral = numpy.float32(4.0)
        with self.assertRaises(TraitError):
            a.integral = numpy.float64(4.0)

    def test_cint_conversion_of_subclasses(self):
        # Regression test for enthought/traits#646
        a = A()

        a.convertible = True
        self.assertIs(type(a.convertible), int)
        self.assertEqual(a.convertible, 1)

        a.convertible_or_none = True
        self.assertIs(type(a.convertible_or_none), int)
        self.assertEqual(a.convertible_or_none, 1)
