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
Tests for the Range trait with value type int.
"""

import unittest

from traits.api import (
    BaseRange,
    Either,
    HasTraits,
    Instance,
    Range,
    TraitError,
)
from traits.testing.optional_dependencies import numpy, requires_numpy


def ModelFactory(name, RangeFactory):
    """
    Helper function to create various similar model classes.

    Parameters
    ----------
    name : str
        Name to give the created class.
    RangeFactory : callable(*range_args, **range_kwargs) -> TraitType
        Callable with the same signature as Range; this will be used
        to create the model traits.

    Returns
    -------
    HasTraits subclass
        Subclass containing various Range-like traits, for testing.

    """

    class ModelWithRanges(HasTraits):
        """
        Model containing various Range-like traits.
        """

        # Simple integer range trait.
        percentage = RangeFactory(0, 100)

        # Traits that exercise the various possiblities for inclusion
        # or exclusion of the endpoints.
        open_closed = RangeFactory(0, 100, exclude_low=True)

        closed_open = RangeFactory(0, 100, exclude_high=True)

        open = RangeFactory(0, 100, exclude_low=True, exclude_high=True)

        closed = RangeFactory(0, 100)

        # Traits for one-sided intervals
        steam_temperature = RangeFactory(low=100)

        ice_temperature = RangeFactory(high=0)

    ModelWithRanges.__name__ = name

    return ModelWithRanges


class Impossible(object):
    """
    Type that never gets instantiated.
    """

    def __init__(self):
        raise TypeError("Cannot instantiate this class")


# A trait type that has a fast validator but doesn't accept any values.
impossible = Instance(Impossible, allow_none=False)


def RangeCompound(*args, **kwargs):
    """
    Compound trait including a Range.
    """
    return Either(impossible, Range(*args, **kwargs))


def BaseRangeCompound(*args, **kwargs):
    """
    Compound trait including a BaseRange.
    """
    return Either(impossible, BaseRange(*args, **kwargs))


ModelWithRange = ModelFactory("ModelWithRange", RangeFactory=Range)

ModelWithBaseRange = ModelFactory("ModelWithBaseRange", RangeFactory=BaseRange)

ModelWithRangeCompound = ModelFactory(
    "ModelWithRangeCompound", RangeFactory=RangeCompound
)

ModelWithBaseRangeCompound = ModelFactory(
    "ModelWithBaseRangeCompound", RangeFactory=BaseRangeCompound,
)


class InheritsFromInt(int):
    """
    Object that's integer-like by virtue of inheriting from int.
    """

    pass


class IntLike(object):
    """
    Object that's integer-like by virtue of providing an __index__ method.
    """

    def __init__(self, value):
        self._value = value

    def __index__(self):
        return self._value


class BadIntLike(object):
    """
    Object whose __index__ method raises something other than TypeError.
    """

    def __index__(self):
        raise ZeroDivisionError("bogus error")


class CommonRangeTests(object):
    def test_accepts_int(self):
        self.model.percentage = 35
        self.assertIs(type(self.model.percentage), int)
        self.assertEqual(self.model.percentage, 35)
        with self.assertRaises(TraitError):
            self.model.percentage = -1
        with self.assertRaises(TraitError):
            self.model.percentage = 101

    def test_accepts_bool(self):
        self.model.percentage = False
        self.assertIs(type(self.model.percentage), int)
        self.assertEqual(self.model.percentage, 0)

        self.model.percentage = True
        self.assertIs(type(self.model.percentage), int)
        self.assertEqual(self.model.percentage, 1)

    def test_rejects_bad_types(self):
        # A selection of things that don't count as integer-like.
        non_integers = [
            "not a number",
            "\N{GREEK CAPITAL LETTER SIGMA}",
            b"not a number",
            "3.5",
            "3",
            3 + 4j,
            0j,
            [1.2],
            (1.2,),
            0.0,
            -27.8,
            35.0,
            None,
        ]

        for non_integer in non_integers:
            self.model.percentage = 73
            with self.assertRaises(TraitError):
                self.model.percentage = non_integer
            self.assertEqual(self.model.percentage, 73)

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
        ]
        for numpy_value in numpy_values:
            self.model.percentage = numpy_value
            self.assertIs(type(self.model.percentage), int)
            self.assertEqual(self.model.percentage, 25)

    @requires_numpy
    def test_rejects_numpy_types(self):
        numpy_values = [
            numpy.float16(25),
            numpy.float32(25),
            numpy.float64(25),
        ]
        for numpy_value in numpy_values:
            self.model.percentage = 88
            with self.assertRaises(TraitError):
                self.model.percentage = numpy_value
            self.assertEqual(self.model.percentage, 88)

    def test_accepts_int_subclass(self):
        self.model.percentage = InheritsFromInt(44)
        self.assertIs(type(self.model.percentage), int)
        self.assertEqual(self.model.percentage, 44)
        with self.assertRaises(TraitError):
            self.model.percentage = InheritsFromInt(-1)
        with self.assertRaises(TraitError):
            self.model.percentage = InheritsFromInt(101)

    def test_accepts_int_like(self):
        self.model.percentage = IntLike(35)
        self.assertIs(type(self.model.percentage), int)
        self.assertEqual(self.model.percentage, 35)
        with self.assertRaises(TraitError):
            self.model.percentage = IntLike(-1)
        with self.assertRaises(TraitError):
            self.model.percentage = IntLike(101)

    def test_bad_int_like(self):
        # Check that the exception is propagated as expected.
        with self.assertRaises(ZeroDivisionError):
            self.model.percentage = BadIntLike()

    def test_endpoints(self):
        # point within the interior of the range
        self.model.open = self.model.closed = 50
        self.model.open_closed = self.model.closed_open = 50
        self.assertEqual(self.model.open, 50)
        self.assertEqual(self.model.closed, 50)
        self.assertEqual(self.model.open_closed, 50)
        self.assertEqual(self.model.closed_open, 50)

        # low endpoint
        self.model.closed = self.model.closed_open = 0
        self.assertEqual(self.model.closed, 0)
        self.assertEqual(self.model.closed_open, 0)
        with self.assertRaises(TraitError):
            self.model.open = 0
        with self.assertRaises(TraitError):
            self.model.open_closed = 0

        # high endpoint
        self.model.closed = self.model.open_closed = 100
        self.assertEqual(self.model.closed, 100)
        self.assertEqual(self.model.open_closed, 100)
        with self.assertRaises(TraitError):
            self.model.open = 100
        with self.assertRaises(TraitError):
            self.model.closed_open = 100

    def test_half_infinite(self):
        ice_temperatures = [-273, -100, -1]
        water_temperatures = [1, 50, 99]
        steam_temperatures = [101, 1000, 10 ** 100, 10 ** 1000]

        for temperature in steam_temperatures:
            self.model.steam_temperature = temperature
            self.assertEqual(self.model.steam_temperature, temperature)

        for temperature in ice_temperatures + water_temperatures:
            self.model.steam_temperature = 1729
            with self.assertRaises(TraitError):
                self.model.steam_temperature = temperature
            self.assertEqual(self.model.steam_temperature, 1729)

        for temperature in ice_temperatures:
            self.model.ice_temperature = temperature
            self.assertEqual(self.model.ice_temperature, temperature)

        for temperature in water_temperatures + steam_temperatures:
            self.model.ice_temperature = -1729
            with self.assertRaises(TraitError):
                self.model.ice_temperature = temperature
            self.assertEqual(self.model.ice_temperature, -1729)


class TestIntRange(CommonRangeTests, unittest.TestCase):
    def setUp(self):
        self.model = ModelWithRange()


class TestIntBaseRange(CommonRangeTests, unittest.TestCase):
    def setUp(self):
        self.model = ModelWithBaseRange()


class TestIntRangeCompound(CommonRangeTests, unittest.TestCase):
    def setUp(self):
        self.model = ModelWithRangeCompound()


class TestIntBaseRangeCompound(CommonRangeTests, unittest.TestCase):
    def setUp(self):
        self.model = ModelWithBaseRangeCompound()
