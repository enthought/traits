# -----------------------------------------------------------------------------
#
#  Copyright (c) 2019, Enthought, Inc.
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
Tests for the Range trait with value type float.
"""

import unittest

from traits.api import Either, HasTraits, Range, TraitError
from traits.testing.optional_dependencies import numpy, requires_numpy


class ModelWithRange(HasTraits):
    """
    Model containing simple Range trait.
    """

    # Simple floating-point range trait.
    percentage = Range(0.0, 100.0)


class ModelWithRangeCompound(HasTraits):
    """
    Model containing compound Range trait.
    """

    # Range as part of a compound trait. This (currently)
    # exercises a different code path in ctraits.c from percentage.
    percentage = Either(None, Range(0.0, 100.0))


class InheritsFromFloat(float):
    """
    Object that's float-like by virtue of inheriting from float.
    """

    pass


class FloatLike(object):
    """
    Object that's float-like by virtue of providing a __float__ method.
    """

    def __init__(self, value):
        self._value = value

    def __float__(self):
        return self._value


class BadFloatLike(object):
    """
    Object whose __float__ method raises something other than TypeError.
    """

    def __float__(self):
        raise ZeroDivisionError("bogus error")


class CommonRangeTests(object):
    def test_accepts_float(self):
        self.model.percentage = 35.0
        self.assertIs(type(self.model.percentage), float)
        self.assertEqual(self.model.percentage, 35.0)
        with self.assertRaises(TraitError):
            self.model.percentage = -0.5
        with self.assertRaises(TraitError):
            self.model.percentage = 100.5

    def test_accepts_int(self):
        self.model.percentage = 35
        self.assertIs(type(self.model.percentage), float)
        self.assertEqual(self.model.percentage, 35.0)
        with self.assertRaises(TraitError):
            self.model.percentage = -1
        with self.assertRaises(TraitError):
            self.model.percentage = 101

    def test_accepts_bool(self):
        self.model.percentage = False
        self.assertIs(type(self.model.percentage), float)
        self.assertEqual(self.model.percentage, 0.0)

        self.model.percentage = True
        self.assertIs(type(self.model.percentage), float)
        self.assertEqual(self.model.percentage, 1.0)

    def test_rejects_bad_types(self):
        # A selection of things that don't count as float-like.
        non_floats = [
            u"not a number",
            u"\N{GREEK CAPITAL LETTER SIGMA}",
            b"not a number",
            "3.5",
            "3",
            3 + 4j,
            0j,
            [1.2],
            (1.2,),
        ]

        for non_float in non_floats:
            with self.assertRaises(TraitError):
                self.model.percentage = non_float

    @requires_numpy
    def test_accepts_numpy_types(self):
        numpy_values = [
            numpy.uint8(25),
            numpy.uint16(25),
            numpy.uint32(25),
            numpy.uint64(25),
            numpy.int8(25),
            numpy.int16(25),
            numpy.int32(25),
            numpy.int64(25),
            numpy.float16(25),
            numpy.float32(25),
            numpy.float64(25),
        ]
        for numpy_value in numpy_values:
            self.model.percentage = numpy_value
            self.assertIs(type(self.model.percentage), float)
            self.assertEqual(self.model.percentage, 25.0)

    def test_accepts_float_subclass(self):
        self.model.percentage = InheritsFromFloat(44.0)
        self.assertIs(type(self.model.percentage), float)
        self.assertEqual(self.model.percentage, 44.0)
        with self.assertRaises(TraitError):
            self.model.percentage = InheritsFromFloat(-0.5)
        with self.assertRaises(TraitError):
            self.model.percentage = InheritsFromFloat(100.5)

    def test_accepts_float_like(self):
        self.model.percentage = FloatLike(35.0)
        self.assertIs(type(self.model.percentage), float)
        self.assertEqual(self.model.percentage, 35.0)
        with self.assertRaises(TraitError):
            self.model.percentage = FloatLike(-0.5)
        with self.assertRaises(TraitError):
            self.model.percentage = FloatLike(100.5)

    def test_bad_float_like(self):
        with self.assertRaises(ZeroDivisionError):
            self.model.percentage = BadFloatLike()


class TestFloatRange(CommonRangeTests, unittest.TestCase):
    def setUp(self):
        self.model = ModelWithRange()


class TestFloatRangeCompound(CommonRangeTests, unittest.TestCase):
    def setUp(self):
        self.model = ModelWithRangeCompound()
