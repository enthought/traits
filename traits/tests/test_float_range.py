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
