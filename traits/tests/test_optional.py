# (C) Copyright 2005-2024 Enthought, Inc., Austin, TX
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
    DefaultValue,
    Float,
    HasTraits,
    Instance,
    Int,
    List,
    Str,
    TraitError,
    TraitType,
    Optional,
    Union,
    Constant,
)
from traits.trait_types import _NoneTrait


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


class TestOptional(unittest.TestCase):

    def test_optional_basic(self):
        class TestClass(HasTraits):
            attribute = Optional(Int)

        TestClass(attribute=None)
        TestClass(attribute=3)

        self.assertIsNone(TestClass(attribute=None).attribute)
        self.assertEqual(TestClass(attribute=3).attribute, 3)

        with self.assertRaises(TraitError):
            TestClass(attribute="3")

    def test_optional_list(self):
        class TestClass(HasTraits):
            attribute = Optional(List(Int))

        TestClass(attribute=None)
        TestClass(attribute=[1, 2, 3])

        with self.assertRaises(TraitError):
            TestClass(attribute=3)

    def test_optional_instance(self):
        class TestClass(HasTraits):
            attribute = Optional(Instance(Int))

        TestClass(attribute=None)
        TestClass(attribute=Int(3))

        with self.assertRaises(TraitError):
            TestClass(attribute=3)
        with self.assertRaises(TraitError):
            TestClass(attribute=Int)

    def test_optional_instance_custom_class(self):
        class TestClass(HasTraits):
            attribute = Optional(Instance(CustomClass))

        TestClass(attribute=None)
        TestClass(attribute=CustomClass(value=5))

        with self.assertRaises(TraitError):
            TestClass(attribute=5)

        with self.assertRaises(TraitError):
            TestClass(attribute=CustomClass)

        self.assertEqual(
            TestClass(attribute=CustomClass(value=5)).attribute.value, 5
        )

        self.assertIsNone(TestClass().attribute)
        self.assertIsNone(TestClass(attribute=None).attribute)

    def test_optional_user_defined_type(self):
        class TestClass(HasTraits):
            attribute = Optional(CustomStrType)

        a = TestClass(attribute="my value")
        self.assertEqual(a.attribute, "my value")

        b = TestClass()
        self.assertIsNone(b.attribute)

        c = TestClass(attribute=3)
        self.assertEqual(c.attribute, 3)

    def test_optional_instance_with_implicit_default_value(self):
        """
        Implicit default is always ``None``
        """

        class TestClass(HasTraits):
            attribute = Optional(Int)

        self.assertIsNone(TestClass().attribute)
        self.assertEqual(TestClass(attribute=3).attribute, 3)
        self.assertIsNone(TestClass(attribute=None).attribute)

    def test_optional_instance_with_metadata_default_value(self):
        """
        Setting the ``default_value`` at trait-level sets the default value
        """

        class TestClass(HasTraits):
            attribute = Optional(Int, default_value=5)

        self.assertEqual(TestClass().attribute, 5)
        self.assertEqual(TestClass(attribute=3).attribute, 3)
        self.assertIsNone(TestClass(attribute=None).attribute)

    def test_optional_instance_with_type_default_value(self):
        """
        Setting the ``default_value`` of the inner trait does not set the
        default value of the ``Optional``
        """
        # Note: may want to warn in this case
        # Discussion ref: enthought/traits#1298

        class TestClass(HasTraits):
            attribute = Optional(Int(5))

        self.assertIsNone(TestClass().attribute)
        self.assertEqual(TestClass(attribute=3).attribute, 3)
        self.assertIsNone(TestClass(attribute=None).attribute)

    def test_optional_invalid_trait(self):
        with self.assertRaises(ValueError) as e:

            class _TestClass(HasTraits):
                attribute = Optional(123)

        self.assertEqual(
            str(e.exception),
            "Optional trait declaration expects a trait type or an instance "
            "of trait type or None, but got 123 instead",
        )

    def test_optional_of_none(self):
        with self.assertRaises(TraitError) as e:

            class _TestClass(HasTraits):
                attribute = Optional(None)

        self.assertEqual(str(e.exception), "Optional type must not be None.")

    def test_optional_unspecified_arguments(self):
        with self.assertRaises(TypeError) as e:

            class TestClass(HasTraits):
                none = Optional()

        self.assertIn(
            "missing 1 required positional argument", str(e.exception)
        )

    def test_optional_multiple_type_arguments(self):
        with self.assertRaises(TypeError):

            class TestClass(HasTraits):
                attribute = Optional(Int, Float)

    def test_optional_default_raise_error(self):
        """
        Behaviour inherited from ``Union``
        """
        with self.assertRaises(ValueError) as e:

            class TestClass(HasTraits):
                attribute = Optional(Int(), default=5)

        self.assertEqual(
            str(e.exception),
            "Optional default value should be set via 'default_value', not "
            "'default'.",
        )

    def test_optional_inner_traits(self):
        class TestClass(HasTraits):
            attribute = Optional(Int(3))

        obj = TestClass()
        t1, t2 = obj.trait("attribute").inner_traits

        self.assertEqual(type(t1.trait_type), _NoneTrait)
        self.assertEqual(t1.default_value(), (DefaultValue.constant, None))
        self.assertEqual(type(t2.trait_type), Int)
        self.assertEqual(t2.default_value(), (DefaultValue.constant, 3))

    def test_optional_notification(self):
        class TestClass(HasTraits):
            attribute = Optional(Int)
            shadow_attribute = None

            def _attribute_changed(self, new):
                self.shadow_attribute = new

        obj = TestClass(attribute=3)

        obj.attribute = 5
        self.assertEqual(obj.shadow_attribute, 5)

        obj.attribute = None
        self.assertIsNone(obj.shadow_attribute)

    def test_optional_nested(self):
        """
        You can nest ``Optional``... if you want to
        """

        class TestClass(HasTraits):
            attribute = Optional(Optional(Int))

        self.assertIsNone(TestClass(attribute=None).attribute)
        self.assertIsNone(TestClass().attribute)

        obj = TestClass(attribute=3)

        obj.attribute = 5
        self.assertEqual(obj.attribute, 5)

        obj.attribute = None
        self.assertIsNone(obj.attribute)

    def test_optional_union_of_optional(self):
        """
        ``Union(T1, Optional(T2))`` acts like ``Union(T1, None, T2)``
        """
        class TestClass(HasTraits):
            attribute = Union(Int, Optional(Float))

        self.assertEqual(TestClass(attribute=3).attribute, 3)
        self.assertEqual(TestClass(attribute=3.0).attribute, 3.0)
        self.assertIsNone(TestClass(attribute=None).attribute)
        self.assertEqual(TestClass().attribute, 0)

        a = TestClass(attribute=3)
        a.attribute = 5
        self.assertEqual(a.attribute, 5)
        a.attribute = 5.0
        self.assertEqual(a.attribute, 5.0)
        a.attribute = None
        self.assertIsNone(a.attribute)

    def test_optional_extend_trait(self):
        class OptionalOrStr(Optional):
            def validate(self, obj, name, value):
                if isinstance(value, str):
                    return value
                return super().validate(obj, name, value)

        class TestClass(HasTraits):
            attribute = OptionalOrStr(Int)

        self.assertEqual(TestClass(attribute=123).attribute, 123)
        self.assertEqual(TestClass(attribute="abc").attribute, "abc")
        self.assertIsNone(TestClass(attribute=None).attribute)
        self.assertIsNone(TestClass().attribute)

        with self.assertRaises(TraitError):
            TestClass(attribute=1.23)

    @unittest.expectedFailure
    def test_optional_default_value_validation(self):
        """
        XFAIL: Default value is not validated against allowed types

        See discussion on enthought/traits#1784
        """
        with self.assertRaises(Exception):
            # Expectation: something in here ought to fail
            class TestClass(HasTraits):
                attribute = Optional(Str, default_value=3.5)

            TestClass()

    @unittest.expectedFailure  # See enthought/traits#1784
    def test_optional_constant_initialization(self):
        class TestClass(HasTraits):
            attribute = Optional(Constant(123))

        self.assertEqual(TestClass(attribute=123).attribute, 123)
        self.assertIsNone(TestClass(attribute=None).attribute)

        # Fails here - internal trait validation fails
        with self.assertRaises(TraitError):
            TestClass(attribute=124)

    @unittest.expectedFailure  # See enthought/traits#1784
    def test_optional_constant_setting(self):
        class TestClass(HasTraits):
            attribute = Optional(Constant(123))

        obj = TestClass(attribute=123)
        obj.attribute = None
        obj.attribute = 123

        # Fails here - internal trait validation fails
        with self.assertRaises(TraitError):
            obj.attribute = 124
