# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

#  Imports

import unittest
import warnings

from traits.api import (
    Any,
    Bytes,
    CBytes,
    CFloat,
    CInt,
    ComparisonMode,
    Color,
    Delegate,
    Float,
    Font,
    HasTraits,
    Instance,
    Int,
    List,
    Range,
    RGBColor,
    Str,
    This,
    Trait,
    TraitError,
    TraitList,
    TraitPrefixList,
    TraitPrefixMap,
    Tuple,
    pop_exception_handler,
    push_exception_handler,
)
from traits.testing.optional_dependencies import requires_traitsui

#  Base unit test classes:


class BaseTest(object):
    def assign(self, value):
        self.obj.value = value

    def coerce(self, value):
        return value

    def test_assignment(self):
        obj = self.obj

        # Validate default value
        value = self._default_value
        self.assertEqual(obj.value, value)

        # Validate all legal values
        for i, value in enumerate(self._good_values):
            obj.value = value
            self.assertEqual(obj.value, self.coerce(value))

            # If there's a defined
            if i < len(self._mapped_values):
                self.assertEqual(obj.value_, self._mapped_values[i])

        # Validate correct behavior for illegal values
        for value in self._bad_values:
            self.assertRaises(TraitError, self.assign, value)


class test_base2(unittest.TestCase):
    def indexed_assign(self, list, index, value):
        list[index] = value

    def indexed_range_assign(self, list, index1, index2, value):
        list[index1:index2] = value

    def extended_slice_assign(self, list, index1, index2, step, value):
        list[index1:index2:step] = value

    # This avoids using a method name that contains 'test' so that this is not
    # called by the tester directly.
    def check_values(
        self,
        name,
        default_value,
        good_values,
        bad_values,
        actual_values=None,
        mapped_values=None,
    ):
        obj = self.obj

        # Make sure the default value is correct:
        value = default_value
        self.assertEqual(getattr(obj, name), value)

        # Iterate over all legal values being tested:
        if actual_values is None:
            actual_values = good_values
        i = 0
        for value in good_values:
            setattr(obj, name, value)
            self.assertEqual(getattr(obj, name), actual_values[i])
            if mapped_values is not None:
                self.assertEqual(
                    getattr(obj, name + "_"), mapped_values[i]
                )
            i += 1

        # Iterate over all illegal values being tested:
        for value in bad_values:
            self.assertRaises(TraitError, setattr, obj, name, value)


class AnyTrait(HasTraits):
    value = Any


class AnyTraitTest(BaseTest, unittest.TestCase):

    def setUp(self):
        self.obj = AnyTrait()

    _default_value = None
    _good_values = [10.0, b"ten", "ten", [10], {"ten": 10}, (10,), None, 1j]
    _mapped_values = []
    _bad_values = []


class CoercibleIntTrait(HasTraits):
    value = CInt(99)


class IntTrait(HasTraits):
    value = Int(99)


class CoercibleIntTest(AnyTraitTest):

    def setUp(self):
        self.obj = CoercibleIntTrait()

    _default_value = 99
    _good_values = [
        10,
        -10,
        10.1,
        -10.1,
        "10",
        "-10",
        b"10",
        b"-10",
    ]
    _bad_values = [
        "10L",
        "-10L",
        "10.1",
        "-10.1",
        b"10L",
        b"-10L",
        b"10.1",
        b"-10.1",
        "ten",
        b"ten",
        [10],
        {"ten": 10},
        (10,),
        None,
        1j,
    ]

    def coerce(self, value):
        try:
            return int(value)
        except:
            return int(float(value))


class IntTest(AnyTraitTest):

    def setUp(self):
        self.obj = IntTrait()

    _default_value = 99
    _good_values = [10, -10]
    _bad_values = [
        "ten",
        b"ten",
        [10],
        {"ten": 10},
        (10,),
        None,
        1j,
        10.1,
        -10.1,
        "10L",
        "-10L",
        "10.1",
        "-10.1",
        b"10L",
        b"-10L",
        b"10.1",
        b"-10.1",
        "10",
        "-10",
        b"10",
        b"-10",
    ]

    try:
        import numpy as np
    except ImportError:
        pass
    else:
        _good_values.extend(
            [
                np.int64(10),
                np.int64(-10),
                np.int32(10),
                np.int32(-10),
                np.int_(10),
                np.int_(-10),
            ]
        )

    def coerce(self, value):
        try:
            return int(value)
        except:
            return int(float(value))


class CoercibleFloatTrait(HasTraits):
    value = CFloat(99.0)


class FloatTrait(HasTraits):
    value = Float(99.0)


class CoercibleFloatTest(AnyTraitTest):
    def setUp(self):
        self.obj = CoercibleFloatTrait()

    _default_value = 99.0
    _good_values = [
        10,
        -10,
        10.1,
        -10.1,
        "10",
        "-10",
        "10.1",
        "-10.1",
        b"10",
        b"-10",
        b"10.1",
        b"-10.1",
    ]
    _bad_values = [
        "10L",
        "-10L",
        b"10L",
        b"-10L",
        "ten",
        b"ten",
        [10],
        {"ten": 10},
        (10,),
        None,
        1j,
    ]

    def coerce(self, value):
        return float(value)


class FloatTest(AnyTraitTest):
    def setUp(self):
        self.obj = FloatTrait()

    _default_value = 99.0
    _good_values = [10, -10, 10.1, -10.1]
    _bad_values = [
        "ten",
        b"ten",
        [10],
        {"ten": 10},
        (10,),
        None,
        1j,
        "10",
        "-10",
        "10L",
        "-10L",
        "10.1",
        "-10.1",
        b"10",
        b"-10",
        b"10L",
        b"-10L",
        b"10.1",
        b"-10.1",
    ]

    def coerce(self, value):
        return float(value)


#  Trait that can only have 'complex'(i.e. imaginary) values:


class ImaginaryValueTrait(HasTraits):
    value = Trait(99.0 - 99.0j)


class ImaginaryValueTest(AnyTraitTest):
    def setUp(self):
        self.obj = ImaginaryValueTrait()

    _default_value = 99.0 - 99.0j
    _good_values = [
        10,
        -10,
        10.1,
        -10.1,
        "10",
        "-10",
        "10.1",
        "-10.1",
        10j,
        10 + 10j,
        10 - 10j,
        10.1j,
        10.1 + 10.1j,
        10.1 - 10.1j,
        "10j",
        "10+10j",
        "10-10j",
    ]
    _bad_values = [b"10L", "-10L", "ten", [10], {"ten": 10}, (10,), None]

    def coerce(self, value):
        return complex(value)


class StringTrait(HasTraits):
    value = Trait("string")


class StringTest(AnyTraitTest):

    def setUp(self):
        self.obj = StringTrait()

    _default_value = "string"
    _good_values = [
        10,
        -10,
        10.1,
        -10.1,
        "10",
        "-10",
        "10L",
        "-10L",
        "10.1",
        "-10.1",
        "string",
        1j,
        [10],
        ["ten"],
        {"ten": 10},
        (10,),
        None,
    ]
    _bad_values = []

    def coerce(self, value):
        return str(value)


class BytesTrait(HasTraits):
    value = Bytes(b"bytes")


class BytesTest(StringTest):

    def setUp(self):
        self.obj = BytesTrait()

    _default_value = b"bytes"
    _good_values = [b"", b"10", b"-10"]
    _bad_values = [
        10,
        -10,
        10.1,
        [b""],
        [b"bytes"],
        [0],
        {b"ten": b"10"},
        (b"",),
        None,
        True,
        "",
        "string",
    ]

    def coerce(self, value):
        return bytes(value)


class CoercibleBytesTrait(HasTraits):
    value = CBytes(b"bytes")


class CoercibleBytesTest(StringTest):

    def setUp(self):
        self.obj = CoercibleBytesTrait()

    _default_value = b"bytes"
    _good_values = [
        b"",
        b"10",
        b"-10",
        10,
        [10],
        (10,),
        set([10]),
        {10: "foo"},
        True,
    ]
    _bad_values = [
        "",
        "string",
        -10,
        10.1,
        [b""],
        [b"bytes"],
        [-10],
        (-10,),
        {-10: "foo"},
        set([-10]),
        [256],
        (256,),
        {256: "foo"},
        set([256]),
        {b"ten": b"10"},
        (b"",),
        None,
    ]

    def coerce(self, value):
        return bytes(value)


class EnumTrait(HasTraits):
    value = Trait([1, "one", 2, "two", 3, "three", 4.4, "four.four"])


class EnumTest(AnyTraitTest):

    def setUp(self):
        self.obj = EnumTrait()

    _default_value = 1
    _good_values = [1, "one", 2, "two", 3, "three", 4.4, "four.four"]
    _bad_values = [0, "zero", 4, None]


# Suppress DeprecationWarning from (implicit) TraitMap instantiation
with warnings.catch_warnings():
    warnings.filterwarnings(action="ignore", category=DeprecationWarning)

    class MappedTrait(HasTraits):
        value = Trait("one", {"one": 1, "two": 2, "three": 3})


class MappedTest(AnyTraitTest):
    def setUp(self):
        self.obj = MappedTrait()

    _default_value = "one"
    _good_values = ["one", "two", "three"]
    _mapped_values = [1, 2, 3]
    _bad_values = ["four", 1, 2, 3, [1], (1,), {1: 1}, None]


# Suppress DeprecationWarning from TraitPrefixList instantiation.
with warnings.catch_warnings():
    warnings.filterwarnings(action="ignore", category=DeprecationWarning)

    class PrefixListTrait(HasTraits):
        value = Trait("one", TraitPrefixList("one", "two", "three"))


class PrefixListTest(AnyTraitTest):
    def setUp(self):
        self.obj = PrefixListTrait()

    _default_value = "one"
    _good_values = [
        "o",
        "on",
        "one",
        "tw",
        "two",
        "th",
        "thr",
        "thre",
        "three",
    ]
    _bad_values = ["t", "one ", " two", 1, None]

    def coerce(self, value):
        return {"o": "one", "on": "one", "tw": "two", "th": "three"}[value[:2]]


# Suppress DeprecationWarning from TraitPrefixMap instantiation.
with warnings.catch_warnings():
    warnings.filterwarnings(action="ignore", category=DeprecationWarning)

    class PrefixMapTrait(HasTraits):
        value = Trait("one", TraitPrefixMap({"one": 1, "two": 2, "three": 3}))


class PrefixMapTest(AnyTraitTest):
    def setUp(self):
        self.obj = PrefixMapTrait()

    _default_value = "one"
    _good_values = [
        "o",
        "on",
        "one",
        "tw",
        "two",
        "th",
        "thr",
        "thre",
        "three",
    ]
    _mapped_values = [1, 1, 1, 2, 2, 3, 3, 3]
    _bad_values = ["t", "one ", " two", 1, None]

    def coerce(self, value):
        return {"o": "one", "on": "one", "tw": "two", "th": "three"}[value[:2]]


# Old style class version:


class OTraitTest1:
    pass


class OTraitTest2(OTraitTest1):
    pass


class OTraitTest3(OTraitTest2):
    pass


class OBadTraitTest:
    pass


otrait_test1 = OTraitTest1()


class OldInstanceTrait(HasTraits):
    value = Trait(otrait_test1)


class OldInstanceTest(AnyTraitTest):
    def setUp(self):
        self.obj = OldInstanceTrait()

    _default_value = otrait_test1
    _good_values = [
        otrait_test1,
        OTraitTest1(),
        OTraitTest2(),
        OTraitTest3(),
        None,
    ]
    _bad_values = [
        0,
        0.0,
        0j,
        OTraitTest1,
        OTraitTest2,
        OBadTraitTest(),
        b"bytes",
        "string",
        [otrait_test1],
        (otrait_test1,),
        {"data": otrait_test1},
    ]


# New style class version:
class NTraitTest1(object):
    pass


class NTraitTest2(NTraitTest1):
    pass


class NTraitTest3(NTraitTest2):
    pass


class NBadTraitTest:
    pass


ntrait_test1 = NTraitTest1()


class NewInstanceTrait(HasTraits):
    value = Trait(ntrait_test1)


class NewInstanceTest(AnyTraitTest):
    def setUp(self):
        self.obj = NewInstanceTrait()

    _default_value = ntrait_test1
    _good_values = [
        ntrait_test1,
        NTraitTest1(),
        NTraitTest2(),
        NTraitTest3(),
        None,
    ]
    _bad_values = [
        0,
        0.0,
        0j,
        NTraitTest1,
        NTraitTest2,
        NBadTraitTest(),
        b"bytes",
        "string",
        [ntrait_test1],
        (ntrait_test1,),
        {"data": ntrait_test1},
    ]


class FactoryClass(HasTraits):
    pass


class ConsumerClass(HasTraits):
    x = Instance(FactoryClass, ())


class ConsumerSubclass(ConsumerClass):
    x = FactoryClass()


embedded_instance_trait = Trait(
    "", Str, Instance("traits.has_traits.HasTraits")
)


class Dummy(HasTraits):
    x = embedded_instance_trait
    xl = List(embedded_instance_trait)


class RegressionTest(unittest.TestCase):
    """ Check that fixed bugs stay fixed.
    """

    def test_factory_subclass_no_segfault(self):
        """ Test that we can provide an instance as a default in the definition
        of a subclass.
        """
        # There used to be a bug where this would segfault.
        obj = ConsumerSubclass()
        obj.x

    def test_trait_compound_instance(self):
        """ Test that a deferred Instance() embedded in a TraitCompound handler
        and then a list will not replace the validate method for the outermost
        trait.
        """
        # Pass through an instance in order to make the instance trait resolve
        # the class.
        d = Dummy()
        d.xl = [HasTraits()]
        d.x = "OK"


#  Trait(using a function) that must be an odd integer:


def odd_integer(object, name, value):
    try:
        float(value)
        if (value % 2) == 1:
            return int(value)
    except:
        pass
    raise TraitError


class OddIntegerTrait(HasTraits):
    value = Trait(99, odd_integer)


class OddIntegerTest(AnyTraitTest):
    def setUp(self):
        self.obj = OddIntegerTrait()

    _default_value = 99
    _good_values = [
        1,
        3,
        5,
        7,
        9,
        999999999,
        1.0,
        3.0,
        5.0,
        7.0,
        9.0,
        999999999.0,
        -1,
        -3,
        -5,
        -7,
        -9,
        -999999999,
        -1.0,
        -3.0,
        -5.0,
        -7.0,
        -9.0,
        -999999999.0,
    ]
    _bad_values = [0, 2, -2, 1j, None, "1", [1], (1,), {1: 1}]


class NotifierTraits(HasTraits):
    value1 = Int
    value2 = Int
    value1_count = Int
    value2_count = Int

    def _anytrait_changed(self, trait_name, old, new):
        if trait_name == "value1":
            self.value1_count += 1
        elif trait_name == "value2":
            self.value2_count += 1

    def _value1_changed(self, old, new):
        self.value1_count += 1

    def _value2_changed(self, old, new):
        self.value2_count += 1


class NotifierTests(unittest.TestCase):
    def setUp(self):
        obj = self.obj = NotifierTraits()
        obj.value1 = 0
        obj.value2 = 0
        obj.value1_count = 0
        obj.value2_count = 0

    def tearDown(self):
        obj = self.obj
        obj.on_trait_change(self.on_value1_changed, "value1", remove=True)
        obj.on_trait_change(self.on_value2_changed, "value2", remove=True)
        obj.on_trait_change(self.on_anytrait_changed, remove=True)

    def on_anytrait_changed(self, object, trait_name, old, new):
        if trait_name == "value1":
            self.obj.value1_count += 1
        elif trait_name == "value2":
            self.obj.value2_count += 1

    def on_value1_changed(self):
        self.obj.value1_count += 1

    def on_value2_changed(self):
        self.obj.value2_count += 1

    def test_simple(self):
        obj = self.obj

        obj.value1 = 1
        self.assertEqual(obj.value1_count, 2)
        self.assertEqual(obj.value2_count, 0)

        obj.value2 = 1
        self.assertEqual(obj.value1_count, 2)
        self.assertEqual(obj.value2_count, 2)

    def test_complex(self):
        obj = self.obj

        obj.on_trait_change(self.on_value1_changed, "value1")
        obj.value1 = 1
        self.assertEqual(obj.value1_count, 3)
        self.assertEqual(obj.value2_count, 0)

        obj.on_trait_change(self.on_value2_changed, "value2")
        obj.value2 = 1
        self.assertEqual(obj.value1_count, 3)
        self.assertEqual(obj.value2_count, 3)

        obj.on_trait_change(self.on_anytrait_changed)

        obj.value1 = 2
        self.assertEqual(obj.value1_count, 7)
        self.assertEqual(obj.value2_count, 3)

        obj.value1 = 2
        self.assertEqual(obj.value1_count, 7)
        self.assertEqual(obj.value2_count, 3)

        obj.value2 = 2
        self.assertEqual(obj.value1_count, 7)
        self.assertEqual(obj.value2_count, 7)

        obj.on_trait_change(self.on_value1_changed, "value1", remove=True)
        obj.value1 = 3
        self.assertEqual(obj.value1_count, 10)
        self.assertEqual(obj.value2_count, 7)

        obj.on_trait_change(self.on_value2_changed, "value2", remove=True)
        obj.value2 = 3
        self.assertEqual(obj.value1_count, 10)
        self.assertEqual(obj.value2_count, 10)

        obj.on_trait_change(self.on_anytrait_changed, remove=True)

        obj.value1 = 4
        self.assertEqual(obj.value1_count, 12)
        self.assertEqual(obj.value2_count, 10)

        obj.value2 = 4
        self.assertEqual(obj.value1_count, 12)
        self.assertEqual(obj.value2_count, 12)


class RaisesArgumentlessRuntimeError(HasTraits):
    x = Int(0)

    def _x_changed(self):
        raise RuntimeError


class TestRuntimeError(unittest.TestCase):
    def setUp(self):
        push_exception_handler(lambda *args: None, reraise_exceptions=True)

    def tearDown(self):
        pop_exception_handler()

    def test_runtime_error(self):
        f = RaisesArgumentlessRuntimeError()
        self.assertRaises(RuntimeError, setattr, f, "x", 5)


class DelegatedFloatTrait(HasTraits):
    value = Trait(99.0)


class DelegateTrait(HasTraits):
    value = Delegate("delegate")
    delegate = Trait(DelegatedFloatTrait())


class DelegateTrait2(DelegateTrait):
    delegate = Trait(DelegateTrait())


class DelegateTrait3(DelegateTrait):
    delegate = Trait(DelegateTrait2())


class DelegateTests(unittest.TestCase):
    def test_delegation(self):
        obj = DelegateTrait3()

        self.assertEqual(obj.value, 99.0)
        parent1 = obj.delegate
        parent2 = parent1.delegate
        parent3 = parent2.delegate
        parent3.value = 3.0
        self.assertEqual(obj.value, 3.0)
        parent2.value = 2.0
        self.assertEqual(obj.value, 2.0)
        self.assertEqual(parent3.value, 3.0)
        parent1.value = 1.0
        self.assertEqual(obj.value, 1.0)
        self.assertEqual(parent2.value, 2.0)
        self.assertEqual(parent3.value, 3.0)
        obj.value = 0.0
        self.assertEqual(obj.value, 0.0)
        self.assertEqual(parent1.value, 1.0)
        self.assertEqual(parent2.value, 2.0)
        self.assertEqual(parent3.value, 3.0)
        del obj.value
        self.assertEqual(obj.value, 1.0)
        del parent1.value
        self.assertEqual(obj.value, 2.0)
        self.assertEqual(parent1.value, 2.0)
        del parent2.value
        self.assertEqual(obj.value, 3.0)
        self.assertEqual(parent1.value, 3.0)
        self.assertEqual(parent2.value, 3.0)
        del parent3.value
        # Uncommenting the following line allows
        # the last assertions to pass. However, this
        # may not be intended behavior, so keeping
        # the line commented.
        # del parent2.value
        self.assertEqual(obj.value, 99.0)
        self.assertEqual(parent1.value, 99.0)
        self.assertEqual(parent2.value, 99.0)
        self.assertEqual(parent3.value, 99.0)


#  Complex(i.e. 'composite') Traits tests:

# Make a TraitCompound handler that does not have a fast_validate so we can
# check for a particular regression.
slow = Trait(1, Range(1, 3), Range(-3, -1))
try:
    del slow.handler.fast_validate
except AttributeError:
    pass


# Suppress DeprecationWarnings from TraitPrefixList and TraitPrefixMap
with warnings.catch_warnings():
    warnings.filterwarnings(action="ignore", category=DeprecationWarning)

    class complex_value(HasTraits):
        num1 = Trait(1, Range(1, 5), Range(-5, -1))
        num2 = Trait(
            1,
            Range(1, 5),
            TraitPrefixList("one", "two", "three", "four", "five"),
        )
        num3 = Trait(
            1,
            Range(1, 5),
            TraitPrefixMap(
                {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
            ),
        )
        num4 = Trait(1, Trait(1, Tuple, slow), 10)
        num5 = Trait(1, 10, Trait(1, Tuple, slow))


class test_complex_value(test_base2):
    def setUp(self):
        self.obj = complex_value()

    def test_num1(self):
        self.check_values(
            "num1",
            1,
            [1, 2, 3, 4, 5, -1, -2, -3, -4, -5],
            [
                0,
                6,
                -6,
                "0",
                "6",
                "-6",
                0.0,
                6.0,
                -6.0,
                [1],
                (1,),
                {1: 1},
                None,
            ],
            [1, 2, 3, 4, 5, -1, -2, -3, -4, -5],
        )

    def test_enum_exceptions(self):
        """ Check that enumerated values can be combined with nested
        TraitCompound handlers.
        """
        self.check_values(
            "num4", 1, [1, 2, 3, -3, -2, -1, 10, ()], [0, 4, 5, -5, -4, 11]
        )
        self.check_values(
            "num5", 1, [1, 2, 3, -3, -2, -1, 10, ()], [0, 4, 5, -5, -4, 11]
        )


class test_list_value(test_base2):
    def setUp(self):
        with self.assertWarns(DeprecationWarning):

            class list_value(HasTraits):
                # Trait definitions:
                list1 = Trait([2], TraitList(Trait([1, 2, 3, 4]), maxlen=4))
                list2 = Trait(
                    [2], TraitList(Trait([1, 2, 3, 4]), minlen=1, maxlen=4)
                )
                alist = List()

        self.obj = list_value()
        self.last_event = None

    def tearDown(self):
        del self.last_event

    def del_range(self, list, index1, index2):
        del list[index1:index2]

    def del_extended_slice(self, list, index1, index2, step):
        del list[index1:index2:step]

    def check_list(self, list):
        self.assertEqual(list, [2])
        self.assertEqual(len(list), 1)
        list.append(3)
        self.assertEqual(len(list), 2)
        list[1] = 2
        self.assertEqual(list[1], 2)
        self.assertEqual(len(list), 2)
        list[0] = 1
        self.assertEqual(list[0], 1)
        self.assertEqual(len(list), 2)
        self.assertRaises(TraitError, self.indexed_assign, list, 0, 5)
        self.assertRaises(TraitError, list.append, 5)
        self.assertRaises(TraitError, list.extend, [1, 2, 3])
        list.extend([3, 4])
        self.assertEqual(list, [1, 2, 3, 4])
        self.assertRaises(TraitError, list.append, 1)
        self.assertRaises(
            ValueError, self.extended_slice_assign, list, 0, 4, 2, [4, 5, 6]
        )
        del list[1]
        self.assertEqual(list, [1, 3, 4])
        del list[0]
        self.assertEqual(list, [3, 4])
        list[:0] = [1, 2]
        self.assertEqual(list, [1, 2, 3, 4])
        self.assertRaises(
            TraitError, self.indexed_range_assign, list, 0, 0, [1]
        )
        del list[0:3]
        self.assertEqual(list, [4])
        self.assertRaises(
            TraitError, self.indexed_range_assign, list, 0, 0, [4, 5]
        )

    def test_list1(self):
        self.check_list(self.obj.list1)

    def test_list2(self):
        self.check_list(self.obj.list2)
        self.assertRaises(TraitError, self.del_range, self.obj.list2, 0, 1)
        self.assertRaises(
            TraitError, self.del_extended_slice, self.obj.list2, 4, -5, -1
        )

    def assertLastTraitListEventEqual(self, index, removed, added):
        self.assertEqual(self.last_event.index, index)
        self.assertEqual(self.last_event.removed, removed)
        self.assertEqual(self.last_event.added, added)

    def test_trait_list_event(self):
        """ Record TraitListEvent behavior.
        """
        self.obj.alist = [1, 2, 3, 4]
        self.obj.on_trait_change(self._record_trait_list_event, "alist_items")
        del self.obj.alist[0]
        self.assertLastTraitListEventEqual(0, [1], [])
        self.obj.alist.append(5)
        self.assertLastTraitListEventEqual(3, [], [5])
        self.obj.alist[0:2] = [6, 7]
        self.assertLastTraitListEventEqual(0, [2, 3], [6, 7])
        self.obj.alist[:2] = [4, 5]
        self.assertLastTraitListEventEqual(0, [6, 7], [4, 5])
        self.obj.alist[0:2:1] = [8, 9]
        self.assertLastTraitListEventEqual(0, [4, 5], [8, 9])
        self.obj.alist[0:2:1] = [8, 9]
        # If list values stay the same, a new TraitListEvent will be generated.
        self.assertLastTraitListEventEqual(0, [8, 9], [8, 9])
        old_event = self.last_event
        self.obj.alist[4:] = []
        # If no structural change, NO new TraitListEvent will be generated.
        self.assertIs(self.last_event, old_event)
        self.obj.alist[0:4:2] = [10, 11]
        self.assertLastTraitListEventEqual(
            slice(0, 3, 2), [8, 4], [10, 11]
        )
        del self.obj.alist[1:4:2]
        self.assertLastTraitListEventEqual(slice(1, 4, 2), [9, 5], [])
        self.obj.alist = [1, 2, 3, 4]
        del self.obj.alist[2:4]
        self.assertLastTraitListEventEqual(2, [3, 4], [])
        self.obj.alist[:0] = [5, 6, 7, 8]
        self.assertLastTraitListEventEqual(0, [], [5, 6, 7, 8])
        del self.obj.alist[:2]
        self.assertLastTraitListEventEqual(0, [5, 6], [])
        del self.obj.alist[0:2]
        self.assertLastTraitListEventEqual(0, [7, 8], [])
        del self.obj.alist[:]
        self.assertLastTraitListEventEqual(0, [1, 2], [])

    def _record_trait_list_event(self, object, name, old, new):
        self.last_event = new


class ThisDummy(HasTraits):
    allows_none = This()
    disallows_none = This(allow_none=False)


class TestThis(unittest.TestCase):
    def test_this_none(self):
        d = ThisDummy()
        self.assertIsNone(d.allows_none)
        d.allows_none = None
        d.allows_none = ThisDummy()
        self.assertIsNotNone(d.allows_none)
        d.allows_none = None
        self.assertIsNone(d.allows_none)

        # Still starts out as None, unavoidably.
        self.assertIsNone(d.disallows_none)
        d.disallows_none = ThisDummy()
        self.assertIsNotNone(d.disallows_none)
        with self.assertRaises(TraitError):
            d.disallows_none = None
        self.assertIsNotNone(d.disallows_none)

    def test_this_other_class(self):
        d = ThisDummy()
        with self.assertRaises(TraitError):
            d.allows_none = object()
        self.assertIsNone(d.allows_none)


class ComparisonModeTests(unittest.TestCase):
    def test_comparison_mode_none(self):
        class HasComparisonMode(HasTraits):
            bar = Trait(comparison_mode=ComparisonMode.none)

        old_compare = HasComparisonMode()
        events = []
        old_compare.on_trait_change(lambda: events.append(None), "bar")

        some_list = [1, 2, 3]

        self.assertEqual(len(events), 0)
        old_compare.bar = some_list
        self.assertEqual(len(events), 1)
        old_compare.bar = some_list
        self.assertEqual(len(events), 2)
        old_compare.bar = [1, 2, 3]
        self.assertEqual(len(events), 3)
        old_compare.bar = [4, 5, 6]
        self.assertEqual(len(events), 4)

    def test_comparison_mode_identity(self):
        class HasComparisonMode(HasTraits):
            bar = Trait(comparison_mode=ComparisonMode.identity)

        old_compare = HasComparisonMode()
        events = []
        old_compare.on_trait_change(lambda: events.append(None), "bar")

        some_list = [1, 2, 3]

        self.assertEqual(len(events), 0)
        old_compare.bar = some_list
        self.assertEqual(len(events), 1)
        old_compare.bar = some_list
        self.assertEqual(len(events), 1)
        old_compare.bar = [1, 2, 3]
        self.assertEqual(len(events), 2)
        old_compare.bar = [4, 5, 6]
        self.assertEqual(len(events), 3)

    def test_comparison_mode_equality(self):
        class HasComparisonMode(HasTraits):
            bar = Trait(comparison_mode=ComparisonMode.equality)

        old_compare = HasComparisonMode()
        events = []
        old_compare.on_trait_change(lambda: events.append(None), "bar")

        some_list = [1, 2, 3]

        self.assertEqual(len(events), 0)
        old_compare.bar = some_list
        self.assertEqual(len(events), 1)
        old_compare.bar = some_list
        self.assertEqual(len(events), 1)
        old_compare.bar = [1, 2, 3]
        self.assertEqual(len(events), 1)
        old_compare.bar = [4, 5, 6]
        self.assertEqual(len(events), 2)

    def test_rich_compare_false(self):
        with warnings.catch_warnings(record=True) as warn_msgs:
            warnings.simplefilter("always", DeprecationWarning)

            class OldRichCompare(HasTraits):
                bar = Trait(rich_compare=False)

        # Check for a DeprecationWarning.
        self.assertEqual(len(warn_msgs), 1)
        warn_msg = warn_msgs[0]
        self.assertIs(warn_msg.category, DeprecationWarning)
        self.assertIn(
            "'rich_compare' metadata has been deprecated",
            str(warn_msg.message)
        )
        _, _, this_module = __name__.rpartition(".")
        self.assertIn(this_module, warn_msg.filename)

        # Behaviour matches comparison_mode=ComparisonMode.identity.
        old_compare = OldRichCompare()
        events = []
        old_compare.on_trait_change(lambda: events.append(None), "bar")

        some_list = [1, 2, 3]

        self.assertEqual(len(events), 0)
        old_compare.bar = some_list
        self.assertEqual(len(events), 1)
        old_compare.bar = some_list
        self.assertEqual(len(events), 1)
        old_compare.bar = [1, 2, 3]
        self.assertEqual(len(events), 2)
        old_compare.bar = [4, 5, 6]
        self.assertEqual(len(events), 3)

    def test_rich_compare_true(self):
        with warnings.catch_warnings(record=True) as warn_msgs:
            warnings.simplefilter("always", DeprecationWarning)

            class OldRichCompare(HasTraits):
                bar = Trait(rich_compare=True)

        # Check for a DeprecationWarning.
        self.assertEqual(len(warn_msgs), 1)
        warn_msg = warn_msgs[0]
        self.assertIs(warn_msg.category, DeprecationWarning)
        self.assertIn(
            "'rich_compare' metadata has been deprecated",
            str(warn_msg.message)
        )
        _, _, this_module = __name__.rpartition(".")
        self.assertIn(this_module, warn_msg.filename)

        # Behaviour matches comparison_mode=ComparisonMode.identity.
        old_compare = OldRichCompare()
        events = []
        old_compare.on_trait_change(lambda: events.append(None), "bar")

        some_list = [1, 2, 3]

        self.assertEqual(len(events), 0)
        old_compare.bar = some_list
        self.assertEqual(len(events), 1)
        old_compare.bar = some_list
        self.assertEqual(len(events), 1)
        old_compare.bar = [1, 2, 3]
        self.assertEqual(len(events), 1)
        old_compare.bar = [4, 5, 6]
        self.assertEqual(len(events), 2)


@requires_traitsui
class TestDeprecatedTraits(unittest.TestCase):

    def test_color_deprecated(self):
        with self.assertWarnsRegex(DeprecationWarning, "'Color' in 'traits'"):
            Color()

    def test_rgb_color_deprecated(self):
        with self.assertWarnsRegex(DeprecationWarning,
                                   "'RGBColor' in 'traits'"):
            RGBColor()

    def test_font_deprecated(self):
        with self.assertWarnsRegex(DeprecationWarning, "'Font' in 'traits'"):
            Font()
