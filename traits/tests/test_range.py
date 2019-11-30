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
Tests for the Range trait.
"""

# XXX Add tests for pass by position for legacy Ranges; the init
# keywords should be in the same order as before.

# XXX Add tests for other possible value_types: Int(), Int, int,
# Float(), Float, float should all work.

# XXX Add tests for cloning / pickling?


import datetime
import operator
import unittest
import warnings

from traits.api import (
    Any,
    BaseRange,
    CTrait,
    Date,
    Either,
    Float,
    HasTraits,
    Instance,
    Int,
    Range,
    Str,
    TraitError,
)
from traits.testing.optional_dependencies import numpy, requires_numpy


class InheritsFromInt(int):
    """
    Object that's integer-like by virtue of inheriting from int.
    """

    pass


class IntLike(object):
    """
    Object that's integer-like by virtue of providing an __index__ method.

    Also usable in comparisons with integers.
    """

    def __init__(self, value):
        self._value = value

    def __index__(self):
        return self._value

    def __le__(self, other):
        return operator.index(self) <= other

    def __lt__(self, other):
        return operator.index(self) < other

    def __ge__(self, other):
        return operator.index(self) >= other

    def __gt__(self, other):
        return operator.index(self) > other

    def __eq__(self, other):
        return operator.index(self) == other

    def __ne__(self, other):
        return operator.index(self) != other


class BadIntLike(object):
    """
    Object whose __index__ method raises something other than TypeError.
    """

    def __index__(self):
        raise ZeroDivisionError("bogus error")


def IntModelFactory(name, RangeFactory):
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

        unbounded = RangeFactory(value_trait=Int())

        unbounded_with_default = RangeFactory(value=50)

        # Traits for one-sided intervals
        steam_temperature = RangeFactory(low=100)

        ice_temperature = RangeFactory(high=0)

        # Trait with non-integer low and high values (but values that are
        # comparable with integers).
        room_temperature = RangeFactory(low=IntLike(10), high=IntLike(30),)

    ModelWithRanges.__name__ = name

    return ModelWithRanges


class DynamicRangesModel(HasTraits):

    # Dynamic low and high
    dynamic_int = Range(
        low_name="low_bound", high_name="high_bound", value_trait=Int()
    )

    dynamic_float = Range(
        low_name="low_bound", high_name="high_bound", value_trait=Float()
    )

    dynamic_with_static_default = Range(
        low_name="low_bound",
        high_name="high_bound",
        value=73,
        value_trait=Int(),
    )

    dynamic_with_static_default_legacy = Range(
        low="low_bound", high="high_bound", value=73.0,
    )

    # Dynamic high value
    dynamic_high = Range(low=0, high="high_bound")

    # Dynamic low value
    dynamic_low = Range(low="low_bound", high=100)

    # Dynamic low, no high; legacy mode (no value_trait)
    dynamic_low_no_high = Range(low="low_bound")

    # Dynamic high, no low; legacy mode (no value_trait)
    dynamic_high_no_low = Range(high="high_bound")

    # Dynamic high and low; legacy mode (no value_trait)
    dynamic_low_and_high = Range(low="low_bound", high="high_bound")

    # Dynamic high, referring to a trait that doesn't exist.
    dynamic_high_nonexistent = Range(low=0, high="nonexistent")

    # Dynamic default
    dynamic_default = Range(low=0, high=100, value="default")

    # Dynamic everything, legacy mode
    full_dynamic_legacy = Range(
        low="low_bound", high="high_bound", value="default",
    )

    # Dynamic everything (value type Int)
    full_dynamic_int = Range(
        low_name="low_bound",
        high_name="high_bound",
        value="default",
        value_trait=Int(),
    )

    # Dynamic everything (value type Float)
    full_dynamic_float = Range(
        low_name="low_bound",
        high_name="high_bound",
        value="default",
        value_trait=Float(),
    )

    # Trait providing the upper bound of a dynamic range.
    high_bound = Any(100)

    # Trait providing the lower bound of a dynamic range.
    low_bound = Any(0)

    # Trait providing the default value for a dynamic range.
    default = Any(50)


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


ModelWithRange = IntModelFactory("ModelWithRange", RangeFactory=Range)

ModelWithBaseRange = IntModelFactory(
    "ModelWithBaseRange", RangeFactory=BaseRange
)

ModelWithRangeCompound = IntModelFactory(
    "ModelWithRangeCompound", RangeFactory=RangeCompound
)

ModelWithBaseRangeCompound = IntModelFactory(
    "ModelWithBaseRangeCompound", RangeFactory=BaseRangeCompound,
)


class CommonIntRangeTests(object):
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
            [1],
            (1,),
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

    def test_bad_default(self):
        class Model(HasTraits):
            foo = Range(1, 2, 1.5, value_trait=Int())

        model = Model()
        with self.assertRaises(TraitError):
            model.foo

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

    def test_integer_like_limits(self):
        self.model.room_temperature = 15
        self.assertIsExactInt(self.model.room_temperature, 15)
        self.model.room_temperature = IntLike(25)
        self.assertIsExactInt(self.model.room_temperature, 25)

        self.model.room_temperature = 27
        with self.assertRaises(TraitError):
            # Bad type.
            self.model.room_temperature = 13.0
        self.assertIsExactInt(self.model.room_temperature, 27)

        # Out-of-range values
        self.model.room_temperature = 27

        with self.assertRaises(TraitError):
            self.model.room_temperature = 5
        self.assertIsExactInt(self.model.room_temperature, 27)

        with self.assertRaises(TraitError):
            self.model.room_temperature = 33
        self.assertIsExactInt(self.model.room_temperature, 27)

    def test_bad_limits(self):
        non_integers = [
            3 + 4j,
            0j,
            [1],
            (1,),
            [1.2],
            (1.2,),
        ]

        for non_integer in non_integers:
            with self.assertRaises(TraitError):
                Range(low=0, high=non_integer)
            with self.assertRaises(TraitError):
                Range(low=non_integer, high=100)

    def test_unbounded_range_with_default(self):
        # For compound traits, default is None.
        if self.compound:
            self.assertIsNone(self.model.unbounded_with_default)
            return

        # Type will be inferred as Float.
        self.assertIsIdentical(self.model.unbounded_with_default, 50.0)

    def test_unbounded_range_no_default(self):
        # For compound traits, default is None.
        if self.compound:
            self.assertIsNone(self.model.unbounded)
            return

        self.assertIsExactInt(self.model.unbounded, 0)

    def assertIsIdentical(self, actual, expected):
        self.assertIs(type(actual), type(expected))
        self.assertEqual(actual, expected)

    def assertIsExactInt(self, actual, expected):
        self.assertIs(type(actual), int)
        self.assertEqual(actual, expected)


class TestIntRange(CommonIntRangeTests, unittest.TestCase):
    def setUp(self):
        self.range_factory = Range
        self.model = ModelWithRange()
        self.compound = False


class TestIntBaseRange(CommonIntRangeTests, unittest.TestCase):
    def setUp(self):
        self.range_factory = BaseRange
        self.model = ModelWithBaseRange()
        self.compound = False


class TestIntRangeCompound(CommonIntRangeTests, unittest.TestCase):
    def setUp(self):
        self.range_factory = RangeCompound
        self.model = ModelWithRangeCompound()
        self.compound = True


class TestIntBaseRangeCompound(CommonIntRangeTests, unittest.TestCase):
    def setUp(self):
        self.range_factory = BaseRangeCompound
        self.model = ModelWithBaseRangeCompound()
        self.compound = True


def as_integer(value):
    """
    Integer conversion matching the behaviour of the Int trait.
    """
    return Int().validate(None, "dummy", value)


class TestRangeTypeInference(unittest.TestCase):
    def test_static_case(self):
        float_range_traits = [
            Range(low=0.0, high=10.0, value=5.0),
            Range(low=0.0, high=10.0, value=5),
            Range(low=0.0, high=10.0, value=None),
            Range(low=0.0, high=10, value=5.0),
            Range(low=0.0, high=10, value=5),
            Range(low=0.0, high=10, value=None),
            Range(low=0.0, high=None, value=5.0),
            Range(low=0.0, high=None, value=5),
            Range(low=0.0, high=None, value=None),
            Range(low=0, high=10.0, value=5.0),
            Range(low=0, high=10.0, value=5),
            Range(low=0, high=10.0, value=None),
            Range(low=None, high=10.0, value=5.0),
            Range(low=None, high=10.0, value=5),
            Range(low=None, high=10.0, value=None),
        ]

        int_range_traits = [
            Range(low=0, high=10, value=5),
            Range(low=0, high=10, value=None),
            Range(low=0, high=None, value=5),
            Range(low=0, high=None, value=None),
            Range(low=None, high=10, value=5),
            Range(low=None, high=10, value=None),
            Range(low=0, high=10, value=5.0),
            Range(low=0, high=None, value=5.0),
            Range(low=None, high=10, value=5.0),
        ]

        for range_trait in float_range_traits:

            class Model(HasTraits):
                foo = range_trait

            model = Model()
            model.foo = 7
            self.assertIs(type(model.foo), float)
            self.assertEqual(model.foo, 7.0)

        for range_trait in int_range_traits:

            class Model(HasTraits):
                foo = range_trait

            model = Model()
            model.foo = 7
            self.assertIs(type(model.foo), int)
            self.assertEqual(model.foo, 7.0)

    def test_deprecated_dynamic_default(self):
        with warnings.catch_warnings(record=True) as warn_msgs:
            warnings.simplefilter("always", DeprecationWarning)
            range_traits = [
                Range(low=3, high=5, value="value"),
                Range(low="low", high=5, value="value"),
                Range(low=3, high="high", value="value"),
            ]

        # Expect one warning for each of our range traits.
        self.assertEqual(len(warn_msgs), len(range_traits))

        for warn_msg in warn_msgs:
            message = str(warn_msg.message)
            self.assertIn("Use of a dynamic default", message)
            self.assertIn("test_integer_range", warn_msg.filename)

    def test_deprecated_type_inference(self):
        # Case where no type can be inferred, and we drop
        # back to Float.
        with warnings.catch_warnings(record=True) as warn_msgs:
            warnings.simplefilter("always", DeprecationWarning)
            range_traits = [
                Range(low=None, high=None, value=None),
                Range(low="low", high=None, value=None),
                Range(low="low", high="high", value=None),
                Range(low=None, high="high", value=None),
                Range(low=None, high=None, value=5.0),
                Range(low=None, high=None, value=5),
            ]

        for range_trait in range_traits:

            class Model(HasTraits):
                low = Any(0)

                high = Any(100)

                foo = range_trait

            model = Model()
            model.foo = 7
            self.assertIs(type(model.foo), float)
            self.assertEqual(model.foo, 7.0)

        # Expect one warning for each of our range traits.
        self.assertEqual(len(warn_msgs), len(range_traits))

        for warn_msg in warn_msgs:
            message = str(warn_msg.message)
            self.assertIn("Unable to infer a value type", message)
            self.assertIn("test_integer_range", warn_msg.filename)

    def test_conflicting_defaults(self):
        # An explicitly-specified default wins over the value_type default.
        class Model(HasTraits):
            foo = Range(value=5, value_trait=Int(3))

            bar = Range(3, 5, 4, value_trait=Float(3.5))

            baz = Range(3, 5, value_trait=Float(3.5))

        model = Model()
        self.assertEqual(model.foo, 5)
        self.assertEqual(model.bar, 4)
        self.assertEqual(model.baz, 3.5)


class TestDynamicRange(unittest.TestCase):
    def setUp(self):
        self.model = DynamicRangesModel()

    def test_dynamic_high(self):
        self.check_trait_set(dynamic_high=50)
        self.check_trait_set(dynamic_high=IntLike(50))
        self.check_trait_set(dynamic_high=InheritsFromInt(50))
        self.check_trait_set(dynamic_high=100)

        self.check_trait_error(dynamic_high=120)
        self.check_trait_error(dynamic_high=-20)

        self.model.high_bound = 200
        self.check_trait_set(dynamic_high=120)

        # Setting a new high that puts the value out of bounds
        # resets the value.
        self.model.high_bound = 60
        self.assertEqual(self.model.dynamic_high, 60)

    def test_dynamic_high_default(self):
        self.assertEqual(self.model.dynamic_high, 0)

    def test_dynamic_high_none(self):
        self.model.high_bound = None
        self.check_trait_set(dynamic_high=50)
        self.check_trait_set(dynamic_high=500)
        self.check_trait_set(dynamic_high=10 ** 1000)

        self.check_trait_error(dynamic_high=-20)

    def test_dynamic_high_float(self):
        # Retrieving the value involves comparing with the low
        # and high, which can raise if those have the wrong type.
        self.model.high_bound = 100.0
        self.assertIs(type(self.model.dynamic_high), int)
        self.assertEqual(self.model.dynamic_high, 0)

    def test_dynamic_high_int_like(self):
        self.model.high_bound = IntLike(60)
        self.check_trait_set(dynamic_high=60)
        self.check_trait_error(dynamic_high=61)

    def test_dynamic_high_nonexistent(self):
        with self.assertRaises(AttributeError):
            self.model.dynamic_high_nonexistent

    def test_dynamic_low_int(self):
        self.model.low_bound = 20
        self.assertEqual(self.model.dynamic_low, 20)

    def test_dynamic_low_int_like(self):
        self.model.low_bound = IntLike(20)
        self.assertEqual(self.model.dynamic_low, 20)
        self.check_trait_set(dynamic_low=25)
        self.check_trait_error(dynamic_low=19)

    def test_dynamic_low_float(self):
        self.model.low_bound = 21.0
        # In legacy mode we have clip_on_get turned on by default,
        # and the default value is not validated. So even though
        # the value type is int, we retrieve a float here.
        self.assertIdentical(self.model.dynamic_low, 21.0)

    def test_dynamic_default(self):
        self.model.default = 27
        self.assertIs(type(self.model.dynamic_default), int)
        self.assertEqual(self.model.dynamic_default, 27)

    def test_bad_dynamic_default(self):
        self.model.default = 27.0
        with self.assertRaises(TraitError):
            self.model.dynamic_default

    def test_dynamic_no_default(self):
        self.model.low_bound = None
        self.model.high_bound = None
        self.assertIs(type(self.model.dynamic_int), int)
        self.assertEqual(self.model.dynamic_int, 0)

        self.assertIs(type(self.model.dynamic_float), float)
        self.assertEqual(self.model.dynamic_float, 0.0)

    def test_dynamic_with_static_default(self):
        self.assertIdentical(self.model.dynamic_with_static_default, 73)
        self.model.high_bound = 50
        # No clip-on-get if not in legacy mode.
        self.assertIdentical(self.model.dynamic_with_static_default, 73)

    def test_dynamic_with_static_default_legacy(self):
        self.assertIdentical(
            self.model.dynamic_with_static_default_legacy, 73.0
        )
        self.model.high_bound = 50
        self.assertIdentical(self.model.dynamic_with_static_default_legacy, 50)
        # dynamic low and high values aren't validated.
        self.model.high_bound = 45.0
        self.assertIdentical(
            self.model.dynamic_with_static_default_legacy, 45.0
        )

    def test_dynamic_default_all_none(self):
        self.model.low_bound = None
        self.model.high_bound = None
        self.model.default = None

        # default *is* validated for CALLABLE_DEFAULT_VALUE
        with self.assertRaises(TraitError):
            self.model.full_dynamic_int
        with self.assertRaises(TraitError):
            self.assertIsNone(self.model.full_dynamic_float)

    def test_dynamic_low_no_high_default(self):
        # In legacy mode, if no default given, should use low.
        self.model.low_bound = -10
        self.assertIdentical(self.model.dynamic_low_no_high, -10)

    def test_dynamic_high_no_low_default(self):
        # In legacy mode, if no default and no low given, should use high.
        self.model.high_bound = 10
        self.assertIdentical(self.model.dynamic_high_no_low, 10)

    def test_dynamic_low_and_high_default(self):
        self.model.low_bound = -10
        self.model.high_bound = 10
        self.assertIdentical(self.model.dynamic_low_and_high, -10)

    def test_default_from_inner_trait(self):
        # Check that for a dynamic range with no default specified, we get the
        # value trait's default.

        class Model(HasTraits):
            dynamic = Range(
                low_name="low_bound",
                high_name="high_bound",
                value_trait=Int(35),
            )

            low_bound = Any(0)

            high_bound = Any(100)

        model = Model()
        self.assertIdentical(model.dynamic, 35)

    def test_full_dynamic_default(self):
        self.model.low_bound = None
        self.model.high_bound = None
        self.model.default = 23

        with self.assertRaises(TraitError):
            self.model.full_dynamic_int

    def test_full_dynamic_default_legacy(self):
        self.model.low_bound = None
        self.model.high_bound = None
        self.model.default = 23

        # In legacy mode, the default is not subject to validation,
        # so we retrieve an int rather than a float.
        self.assertIdentical(self.model.full_dynamic_legacy, 23)

    def test_static_and_dynamic_conflict(self):
        with self.assertRaises(TraitError):
            Range(low=0, low_name="low", value_trait=Float())
        with self.assertRaises(TraitError):
            Range(low=0, low_name="low")
        with self.assertRaises(TraitError):
            Range(high=0, high_name="high", value_trait=Float())
        with self.assertRaises(TraitError):
            Range(high=0, high_name="high")

    def test_inner_traits(self):
        range_trait = Range(-1, 1, value_trait=Float())
        inner_traits = range_trait.inner_traits()

        self.assertIsInstance(inner_traits, tuple)
        self.assertEqual(len(inner_traits), 1)
        inner_trait = inner_traits[0]
        self.assertIsInstance(inner_trait, CTrait)
        self.assertIsInstance(inner_trait.trait_type, Float)

    def check_trait_set(self, **kwargs):
        # Check the result of setting an integer range trait.
        for name, value in kwargs.items():
            setattr(self.model, name, value)
            retrieved_value = getattr(self.model, name)
            expected_value = as_integer(value)
            self.assertIs(type(retrieved_value), type(expected_value))
            self.assertEqual(retrieved_value, expected_value)

    def check_trait_error(self, **kwargs):
        for name, value in kwargs.items():
            original_value = getattr(self.model, name)
            with self.assertRaises(TraitError):
                setattr(self.model, name, value)
            # Check that the value is unchanged.
            self.assertEqual(getattr(self.model, name), original_value)

    def assertIdentical(self, actual, expected):
        self.assertIs(type(actual), type(expected))
        self.assertEqual(actual, expected)


class ClipOnGetModel(HasTraits):
    low = Int(0)

    high = Int(100)

    not_clipped_dynamic = Range(
        low_name="low", high_name="high", value=200, value_trait=Int(),
    )

    # Legacy mode: clipping occurs for all three traits below.
    clipped_legacy = Range("low", "high", -100)

    clipped_legacy_high = Range(0, "high", 200)

    clipped_legacy_low = Range("low", 100, 200)

    # Non-legacy mode, value_trait specified. No clipping.
    clipped_new = Range(
        low_name="low", high_name="high", value=200, value_trait=Int()
    )


class TestRangeClipOnGet(unittest.TestCase):
    def setUp(self):
        self.model = ClipOnGetModel()

    def test_not_clipped_dynamic(self):
        with self.assertRaises(TraitError):
            self.model.not_clipped_dynamic
        with self.assertRaises(TraitError):
            self.model.not_clipped_dynamic = 150
        self.model.not_clipped_dynamic = 90
        self.assertIdentical(self.model.not_clipped_dynamic, 90)

        self.model.high = 50
        self.assertIdentical(self.model.not_clipped_dynamic, 90)

    def test_legacy_mode_clipping(self):
        self.assertIdentical(self.model.clipped_legacy, 0)
        self.model.low = -200
        self.assertIdentical(self.model.clipped_legacy, -100)
        self.model.high = -150
        self.assertIdentical(self.model.clipped_legacy, -150)
        self.model.high = 100
        self.model.low = 0
        self.assertIdentical(self.model.clipped_legacy, 0)

        self.assertIdentical(self.model.clipped_legacy_high, 100)
        self.model.high = 300
        self.assertIdentical(self.model.clipped_legacy_high, 200)
        self.model.high = 100
        self.assertIdentical(self.model.clipped_legacy_high, 100)

        self.assertIdentical(self.model.clipped_legacy_low, 100)
        self.model.clipped_legacy_low = 50
        self.assertIdentical(self.model.clipped_legacy_low, 50)
        with self.assertRaises(TraitError):
            self.model.clipped_legacy_low = -50
        self.model.low = -100
        self.model.clipped_legacy_low = -50
        self.assertIdentical(self.model.clipped_legacy_low, -50)
        self.model.low = 0
        self.assertIdentical(self.model.clipped_legacy_low, 0)

    def test_new_mode_clipping(self):
        with self.assertRaises(TraitError):
            self.model.clipped_new
        with self.assertRaises(TraitError):
            self.model.clipped_new = -100
        self.model.low = -200
        self.model.clipped_new = -100
        self.assertIdentical(self.model.clipped_new, -100)
        self.model.low = 0
        self.assertIdentical(self.model.clipped_new, -100)

    def assertIdentical(self, actual, expected):
        self.assertIs(type(actual), type(expected))
        self.assertEqual(actual, expected)


class HasNonNumericRanges(HasTraits):
    foo = Range("i", "o", "kanga", exclude_high=True, value_trait=Str())

    bar = Range(
        datetime.date(1931, 1, 1),
        datetime.date(1940, 12, 31),
        datetime.date(1932, 5, 5),
        value_trait=Date(),
    )


class TestNonNumericRanges(unittest.TestCase):
    def test_str_range(self):
        model = HasNonNumericRanges()
        self.assertEqual(model.foo, "kanga")

        valid_values = ["i", "ii", "jkl", "nzz"]
        invalid_values = ["hzzz", "o", "oa", "zzz"]

        for value in valid_values:
            model.foo = value
            self.assertEqual(model.foo, value)

        for value in invalid_values:
            old_value = model.foo
            with self.assertRaises(TraitError):
                model.foo = value
            self.assertEqual(model.foo, old_value)

    def test_date_range(self):
        model = HasNonNumericRanges()
        self.assertEqual(model.bar, datetime.date(1932, 5, 5))

        valid_values = [
            datetime.date(1931, 1, 1),
            datetime.date(1936, 9, 17),
            datetime.date(1940, 12, 31),
        ]

        invalid_values = [
            datetime.date(1930, 12, 31),
            datetime.date(1941, 1, 1),
        ]

        for value in valid_values:
            model.bar = value
            self.assertEqual(model.bar, value)

        for value in invalid_values:
            old_value = model.bar
            with self.assertRaises(TraitError):
                model.bar = value
            self.assertEqual(model.bar, old_value)


class TestFullInfo(unittest.TestCase):
    def test_full_info(self):
        # Test pairs (range_trait, expected_info_text)
        infos = [
            (
                Range(low=-6, high=7, value_trait=Int()),
                "-6 <= an integer <= 7",
            ),
            (
                Range(low=-6, high=7, exclude_low=True, value_trait=Int()),
                "-6 < an integer <= 7",
            ),
            (
                Range(low=-6, high=7, exclude_high=True, value_trait=Int()),
                "-6 <= an integer < 7",
            ),
            (
                Range(
                    low=-6,
                    high=7,
                    exclude_low=True,
                    exclude_high=True,
                    value_trait=Int(),
                ),
                "-6 < an integer < 7",
            ),
            (Range(low=-6, high=None, value_trait=Int()), "an integer >= -6"),
            (
                Range(low=-6, high=None, exclude_low=True, value_trait=Int()),
                "an integer > -6",
            ),
            (Range(low=None, high=7, value_trait=Int()), "an integer <= 7"),
            (
                Range(low=None, high=7, exclude_high=True, value_trait=Int()),
                "an integer < 7",
            ),
            (Range(low=None, high=None, value_trait=Int()), "an integer"),
            (
                Range(low=-3.5, high=4.2, value_trait=Float()),
                "-3.5 <= a float <= 4.2",
            ),
            (Range(low=None, high=None, value_trait=Float()), "a float"),
        ]

        for range_trait, expected_info in infos:
            actual_info = range_trait.full_info(None, "dummy", None)
            self.assertEqual(actual_info, expected_info)


class DefaultDeferralModel(HasTraits):
    low = Float(-10.0)
    high = Float(10.0)

    range1 = Range(low=-2.3, high=4.5)
    range2 = Range(low=-2.3, high="high")
    range2a = Range(low=-2.3, high_name="high")
    range3 = Range(low=-2.3)

    range4 = Range(low="low", high=4.5)
    range5 = Range(low="low", high="high")
    range5b = Range(low="low", high_name="high")
    range6 = Range(low="low")

    range4a = Range(low_name="low", high=4.5)
    range5a = Range(low_name="low", high="high")
    range5c = Range(low_name="low", high_name="high")
    range6a = Range(low_name="low")

    range7 = Range(high=4.5)
    range8 = Range(high="high")
    range8a = Range(high_name="high")
    range9 = Range()


class TestLegacyRangeDefaultDeferral(unittest.TestCase):
    def test_default_deferral(self):

        model = DefaultDeferralModel()

        # Defer to low if given.
        self.assertIdentical(model.range1, -2.3)
        self.assertIdentical(model.range2, -2.3)
        self.assertIdentical(model.range2a, -2.3)
        self.assertIdentical(model.range3, -2.3)

        # ... even if low is a string
        self.assertIdentical(model.range4, -10.0)
        self.assertIdentical(model.range5, -10.0)
        self.assertIdentical(model.range5b, -10.0)
        self.assertIdentical(model.range6, -10.0)

        self.assertIdentical(model.range4a, -10.0)
        self.assertIdentical(model.range5a, -10.0)
        self.assertIdentical(model.range5c, -10.0)
        self.assertIdentical(model.range6a, -10.0)

        # if no low, defer to high
        self.assertIdentical(model.range7, 4.5)
        self.assertIdentical(model.range8, 10.0)
        self.assertIdentical(model.range8a, 10.0)

        # and if neither low nor high given, use the (inferred) value_trait
        # default of 0.0
        self.assertIdentical(model.range9, 0.0)

    def assertIdentical(self, actual, expected):
        self.assertIs(type(actual), type(expected))
        self.assertEqual(actual, expected)


class Impossible(object):
    """
    Type that never gets instantiated.
    """

    def __init__(self):
        raise TypeError("Cannot instantiate this class")


def FloatModelFactory(name, RangeFactory):
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

        # Simple floating-point range trait.
        percentage = RangeFactory(0.0, 100.0)

        # Traits that exercise the various possiblities for inclusion
        # or exclusion of the endpoints.
        open_closed = RangeFactory(0.0, 100.0, exclude_low=True)

        closed_open = RangeFactory(0.0, 100.0, exclude_high=True)

        open = RangeFactory(0.0, 100.0, exclude_low=True, exclude_high=True)

        closed = RangeFactory(0.0, 100.0)

        unbounded = RangeFactory()

        unbounded_with_default = RangeFactory(value=50.0)

        # Traits for one-sided intervals
        steam_temperature = RangeFactory(low=100.0)

        ice_temperature = Range(high=0.0)

    ModelWithRanges.__name__ = name

    return ModelWithRanges


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


ModelWithRange = FloatModelFactory("ModelWithRange", RangeFactory=Range)

ModelWithBaseRange = FloatModelFactory(
    "ModelWithBaseRange", RangeFactory=BaseRange
)

ModelWithRangeCompound = FloatModelFactory(
    "ModelWithRangeCompound", RangeFactory=RangeCompound,
)

ModelWithBaseRangeCompound = FloatModelFactory(
    "ModelWithBaseRangeCompound", RangeFactory=BaseRangeCompound,
)


class InheritsFromFloat(float):
    """
    Object that's float-like by virtue of inheriting from float.
    """

    pass


class FloatLike(object):
    """
    Object that's float-like by virtue of providing a __float__ method.

    Also participates in comparisons with floats.
    """

    def __init__(self, value):
        self._value = value

    def __float__(self):
        return self._value

    def __le__(self, other):
        return float(self) <= other

    def __lt__(self, other):
        return float(self) < other

    def __ge__(self, other):
        return float(self) >= other

    def __gt__(self, other):
        return float(self) > other

    def __eq__(self, other):
        return float(self) == other

    def __ne__(self, other):
        return float(self) != other


class BadFloatLike(object):
    """
    Object whose __float__ method raises something other than TypeError.
    """

    def __float__(self):
        raise ZeroDivisionError("bogus error")


class CommonFloatRangeTests(object):
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
            "not a number",
            "\N{GREEK CAPITAL LETTER SIGMA}",
            b"not a number",
            "3.5",
            "3",
            3 + 4j,
            0j,
            [1],
            (1,),
            [1.2],
            (1.2,),
            None,
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

    def test_bad_default(self):
        class Model(HasTraits):
            foo = Range(1.0, 2.0, 1.5j, value_trait=Float())

        model = Model()
        with self.assertRaises(TraitError):
            model.foo

    def test_endpoints(self):
        # point within the interior of the range
        self.model.open = self.model.closed = 50.0
        self.model.open_closed = self.model.closed_open = 50.0
        self.assertEqual(self.model.open, 50.0)
        self.assertEqual(self.model.closed, 50.0)
        self.assertEqual(self.model.open_closed, 50.0)
        self.assertEqual(self.model.closed_open, 50.0)

        # low endpoint
        self.model.closed = self.model.closed_open = 0.0
        self.assertEqual(self.model.closed, 0.0)
        self.assertEqual(self.model.closed_open, 0.0)
        with self.assertRaises(TraitError):
            self.model.open = 0.0
        with self.assertRaises(TraitError):
            self.model.open_closed = 0.0

        # high endpoint
        self.model.closed = self.model.open_closed = 100.0
        self.assertEqual(self.model.closed, 100.0)
        self.assertEqual(self.model.open_closed, 100.0)
        with self.assertRaises(TraitError):
            self.model.open = 100.0
        with self.assertRaises(TraitError):
            self.model.closed_open = 100.0

    def test_half_infinite(self):
        ice_temperatures = [-273.15, -273.0, -100.0, -1.0, -0.1, -0.001]
        water_temperatures = [0.001, 0.1, 1.0, 50.0, 99.0, 99.9, 99.999]
        steam_temperatures = [100.001, 100.1, 101.0, 1000.0, 1e100]

        for temperature in steam_temperatures:
            self.model.steam_temperature = temperature
            self.assertEqual(self.model.steam_temperature, temperature)

        for temperature in ice_temperatures + water_temperatures:
            self.model.steam_temperature = 1729.0
            with self.assertRaises(TraitError):
                self.model.steam_temperature = temperature
            self.assertEqual(self.model.steam_temperature, 1729.0)

        for temperature in ice_temperatures:
            self.model.ice_temperature = temperature
            self.assertEqual(self.model.ice_temperature, temperature)

        for temperature in water_temperatures + steam_temperatures:
            self.model.ice_temperature = -1729.0
            with self.assertRaises(TraitError):
                self.model.ice_temperature = temperature
            self.assertEqual(self.model.ice_temperature, -1729.0)

    def test_float_like_limits(self):
        class Model(HasTraits):
            temperature = self.range_factory(
                low=FloatLike(10.0), high=FloatLike(30.0),
            )

        model = Model()
        model.temperature = 15.5
        self.assertIsExactFloat(model.temperature, 15.5)
        model.temperature = FloatLike(25.7)
        self.assertIsExactFloat(model.temperature, 25.7)
        model.temperature = 13
        self.assertIsExactFloat(model.temperature, 13.0)

        # Out-of-range values.
        model.temperature = 27.0

        with self.assertRaises(TraitError):
            model.temperature = 5.0
        self.assertIsExactFloat(model.temperature, 27.0)

        with self.assertRaises(TraitError):
            model.temperature = 35.0
        self.assertIsExactFloat(model.temperature, 27.0)

    def test_unbounded_range_with_default(self):
        # For compound traits, default is None.
        if self.compound:
            self.assertIsNone(self.model.unbounded_with_default)
            return

        self.assertIsExactFloat(self.model.unbounded_with_default, 50.0)

    def test_unbounded_range_no_default(self):
        # For compound traits, default is None.
        if self.compound:
            self.assertIsNone(self.model.unbounded)
            return

        self.assertIsExactFloat(self.model.unbounded, 0.0)

    def assertIsExactFloat(self, actual, expected):
        self.assertIs(type(actual), float)
        self.assertEqual(actual, expected)


class TestFloatRange(CommonFloatRangeTests, unittest.TestCase):
    def setUp(self):
        self.range_factory = Range
        self.model = ModelWithRange()
        self.compound = False


class TestFloatBaseRange(CommonFloatRangeTests, unittest.TestCase):
    def setUp(self):
        self.range_factory = BaseRange
        self.model = ModelWithBaseRange()
        self.compound = False


class TestFloatRangeCompound(CommonFloatRangeTests, unittest.TestCase):
    def setUp(self):
        self.range_factory = RangeCompound
        self.model = ModelWithRangeCompound()
        self.compound = True


class TestFloatBaseRangeCompound(CommonFloatRangeTests, unittest.TestCase):
    def setUp(self):
        self.range_factory = BaseRangeCompound
        self.model = ModelWithBaseRangeCompound()
        self.compound = True


# XXX Move me to a different file?


class TestRange(unittest.TestCase):
    def test_low_or_high_invalid(self):
        with self.assertRaises(TraitError):
            Range(low=None, high=1j)
        with self.assertRaises(TraitError):
            Range(low=[2.3], high=4.5)

    def test_static_integer_like(self):
        int_like = Range(low=None, high=3)
        self.assertAccepts(int_like, 2, 2)
        self.assertRejects(int_like, 2.0)

        int_like = Range(low=0, high=None)
        self.assertAccepts(int_like, 2, 2)
        self.assertRejects(int_like, 2.0)

        int_like = Range(low=0, high=3)
        self.assertAccepts(int_like, 2, 2)
        self.assertRejects(int_like, 2.0)

    def test_static_float_like(self):
        float_like = Range(low=None, high=3.0)
        self.assertAccepts(float_like, 2, 2.0)
        self.assertAccepts(float_like, 2.0, 2.0)

        float_like = Range(low=0.0, high=None)
        self.assertAccepts(float_like, 2, 2.0)
        self.assertAccepts(float_like, 2.0, 2.0)

        float_like = Range(low=0.0, high=3.0)
        self.assertAccepts(float_like, 2, 2.0)
        self.assertAccepts(float_like, 2.0, 2.0)

        # Mixed types for low and high
        float_like = Range(low=0.0, high=3)
        self.assertAccepts(float_like, 2, 2.0)
        self.assertAccepts(float_like, 2.0, 2.0)

        float_like = Range(low=0, high=3.0)
        self.assertAccepts(float_like, 2, 2.0)
        self.assertAccepts(float_like, 2.0, 2.0)

    def assertAccepts(self, trait, value, expected):
        obj = HasTraits()
        new_value = trait.validate(obj, "name", value)
        self.assertIs(type(new_value), type(expected))
        self.assertEqual(new_value, expected)

    def assertRejects(self, trait, value):
        obj = HasTraits()
        with self.assertRaises(TraitError):
            trait.validate(obj, "name", value)
