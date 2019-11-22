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


class ModelWithRanges(HasTraits):
    """
    Model containing various Range traits for testing purposes.
    """

    # Simple floating-point range trait.
    percentage = Range(0.0, 100.0)

    # Range as part of a complex trait. This (currently)
    # exercises a different code path in ctraits.c from percentage.
    percentage_or_none = Either(None, Range(0.0, 100.0))


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


class TestFloatRange(unittest.TestCase):
    def test_accepts_float(self):
        model = ModelWithRanges()
        model.percentage = 35.0
        self.assertIs(type(model.percentage), float)
        self.assertEqual(model.percentage, 35.0)
        with self.assertRaises(TraitError):
            model.percentage = -0.5
        with self.assertRaises(TraitError):
            model.percentage = 100.5

    def test_accepts_float_subclass(self):
        model = ModelWithRanges()
        model.percentage = InheritsFromFloat(44.0)
        self.assertIs(type(model.percentage), float)
        self.assertEqual(model.percentage, 44.0)
        with self.assertRaises(TraitError):
            model.percentage = InheritsFromFloat(-0.5)
        with self.assertRaises(TraitError):
            model.percentage = InheritsFromFloat(100.5)

    def test_accepts_float_like(self):
        model = ModelWithRanges()
        model.percentage = FloatLike(35.0)
        self.assertIs(type(model.percentage), float)
        self.assertEqual(model.percentage, 35.0)
        with self.assertRaises(TraitError):
            model.percentage = FloatLike(-0.5)
        with self.assertRaises(TraitError):
            model.percentage = FloatLike(100.5)

    def test_range_in_compound_trait_accepts_float(self):
        model = ModelWithRanges()
        model.percentage_or_none = 35.0
        self.assertIs(type(model.percentage_or_none), float)
        self.assertEqual(model.percentage_or_none, 35.0)
        with self.assertRaises(TraitError):
            model.percentage_or_none = -0.5
        with self.assertRaises(TraitError):
            model.percentage_or_none = 100.5

    def test_range_in_compound_trait_accepts_float_subclass(self):
        model = ModelWithRanges()
        model.percentage_or_none = InheritsFromFloat(67.0)
        self.assertIs(type(model.percentage_or_none), float)
        self.assertEqual(model.percentage_or_none, 67.0)
        with self.assertRaises(TraitError):
            model.percentage_or_none = InheritsFromFloat(-0.5)
        with self.assertRaises(TraitError):
            model.percentage_or_none = InheritsFromFloat(100.5)

    def test_range_in_compound_trait_accepts_float_like(self):
        model = ModelWithRanges()
        model.percentage_or_none = FloatLike(67.0)
        self.assertIs(type(model.percentage_or_none), float)
        self.assertEqual(model.percentage_or_none, 67.0)
        with self.assertRaises(TraitError):
            model.percentage_or_none = FloatLike(-0.5)
        with self.assertRaises(TraitError):
            model.percentage_or_none = FloatLike(100.5)

    def test_bad_float_like(self):
        model = ModelWithRanges()
        with self.assertRaises(ZeroDivisionError):
            model.percentage = BadFloatLike()
        with self.assertRaises(ZeroDivisionError):
            model.percentage_or_none = BadFloatLike()
