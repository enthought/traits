# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.api import (
    Bytes, DefaultValue, Float, HasTraits, Instance, Int, List, Str,
    TraitError, TraitType, Type, Union)


class CustomClass(HasTraits):
    value = Int


class CustomStrType(TraitType):

    #: The default value type to use.
    default_value_type = DefaultValue.constant

    #: The default value.
    default_value = "a string value"

    def validate(self, obj, name, value):
        if not isinstance(value, Str):
            return value
        self.error(obj, name, value)


class TestUnion(unittest.TestCase):

    def test_union_incompatible_trait(self):
        with self.assertRaises(ValueError) as exception_context:
            Union(Str(), "none")

        self.assertEqual(
            str(exception_context.exception),
            "Union trait declaration expects a trait type or an instance of "
            "trait type or None, but got 'none' instead"
        )

    def test_list_trait_types(self):
        class TestClass(HasTraits):
            int_or_str_type = Union(Type, Int, Str)

        TestClass(int_or_str_type=3)
        TestClass(int_or_str_type="3.5")

        with self.assertRaises(TraitError):
            TestClass(int_or_str_type=3.5)

        with self.assertRaises(TraitError):
            TestClass(int_or_str_type=Int(3))

    def test_malformed_declaration(self):
        with self.assertRaises(ValueError):
            class TestClass(HasTraits):
                a = Union(int, Float)

            TestClass(a=2.4)

        with self.assertRaises(ValueError):
            class TestClass(HasTraits):
                a = Union([1, 2], Float)

            TestClass(a=2.4)

    def test_list_trait_instances(self):
        class TestClass(HasTraits):
            float_or_str_obj = Union(Instance(Float), Instance(Str))

        TestClass(float_or_str_obj=Float(3.5))
        TestClass(float_or_str_obj=Str("3.5"))

        with self.assertRaises(TraitError):
            TestClass(float_or_str_obj=Float)

        with self.assertRaises(TraitError):
            TestClass(float_or_str_obj=3.5)

    def test_union_with_none(self):
        class TestClass(HasTraits):
            int_or_none = Union(None, Int)

        TestClass(int_or_none=None)

    def test_union_unspecified_arguments(self):
        class TestClass(HasTraits):
            none = Union()
        TestClass(none=None)

    def test_default_value(self):
        class TestClass(HasTraits):
            atr = Union(Int(3), Float(4.1), Str("Something"))

        self.assertEqual(TestClass().atr, 3)

        class TestClass(HasTraits):
            atr = Union(
                Int(3), Float(4.1), Str("Something"),
                default_value="XYZ",
            )

        self.assertEqual(TestClass().atr, "XYZ")

        class TestClass(HasTraits):
            atr = Union()

        self.assertEqual(TestClass().atr, None)

        class TestClass(HasTraits):
            atr = Union(None)

        self.assertEqual(TestClass().atr, None)

    def test_default_raise_error(self):
        # If 'default' is defined, it could be caused by migration from
        # ``Either``. Raise an error to aid migrations from ``Either``
        # to ``Union``

        with self.assertRaises(ValueError) as exception_context:
            Union(Int(), Float(), default=1.0)

        self.assertEqual(
            str(exception_context.exception),
            "Union default value should be set via 'default_value', not "
            "'default'."
        )

    def test_inner_traits(self):
        class TestClass(HasTraits):
            atr = Union(Float, Int, Str)

        obj = TestClass()
        t1, t2, t3 = obj.trait('atr').inner_traits

        self.assertEqual(type(t1.trait_type), Float)
        self.assertEqual(type(t2.trait_type), Int)
        self.assertEqual(type(t3.trait_type), Str)

    def test_union_user_defined_class(self):
        class TestClass(HasTraits):
            obj = Union(Instance(CustomClass), Int)

        TestClass(obj=CustomClass(value=5))
        TestClass(obj=5)

        with self.assertRaises(TraitError):
            TestClass(obj=CustomClass)

    def test_union_user_defined_type(self):
        class TestClass(HasTraits):
            type_value = Union(CustomStrType, Int)

        TestClass(type_value="new string")

    def test_notification(self):
        class TestClass(HasTraits):
            union_attr = Union(Int)
            shadow_union_trait = None

            def _union_attr_changed(self, new):
                self.shadow_union_trait = new

        obj = TestClass(union_attr=-1)

        obj.union_attr = 1
        self.assertEqual(obj.shadow_union_trait, 1)

    def test_extending_union_trait(self):
        class UnionAllowStr(Union):
            def validate(self, obj, name, value):
                if isinstance(value, str):
                    return value
                return super().validate(obj, name, value)

        class TestClass(HasTraits):
            s = UnionAllowStr(Int, Float)

        TestClass(s="sdf")

    def test_list_inside_union_default(self):
        class HasUnionWithList(HasTraits):
            foo = Union(List(Int), Str)

        has_union = HasUnionWithList()
        value = has_union.foo
        self.assertIsInstance(value, list)
        with self.assertRaises(TraitError):
            value.append("not an integer")

    def test_constant_default(self):
        # Exercise the branch where the default is constant.
        class HasUnionWithList(HasTraits):
            foo = Union(Int(23), Float)

            nested = Union(Union(Str(), Bytes()), Union(Int(), Float(), None))

        has_union = HasUnionWithList()
        value = has_union.foo
        self.assertEqual(value, 23)

        self.assertEqual(
            has_union.trait("foo").default_value(),
            (DefaultValue.constant, 23),
        )
        self.assertEqual(
            has_union.trait("nested").default_value(),
            (DefaultValue.constant, ""),
        )
