# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import enum
import unittest

from traits.api import Any, Enum, HasTraits, List, Property, TraitError


class FooEnum(enum.Enum):
    foo = 0
    bar = 1
    baz = 2


class OtherEnum(enum.Enum):
    one = 1
    two = 2
    three = 3


class ExampleModel(HasTraits):
    valid_models = Property(List)
    root = Enum(values="valid_models")

    def _get_valid_models(self):
        return ["model1", "model2", "model3"]


class EnumListExample(HasTraits):

    values = Any(['foo', 'bar', 'baz'])

    value = Enum(['foo', 'bar', 'baz'])

    value_default = Enum('bar', ['foo', 'bar', 'baz'])

    value_name = Enum(values='values')

    value_name_default = Enum('bar', values='values')


class EnumTupleExample(HasTraits):

    values = Any(('foo', 'bar', 'baz'))

    value = Enum(('foo', 'bar', 'baz'))

    value_default = Enum('bar', ('foo', 'bar', 'baz'))

    value_name = Enum(values='values')

    value_name_default = Enum('bar', values='values')


class EnumEnumExample(HasTraits):

    values = Any(FooEnum)

    value = Enum(FooEnum)

    value_default = Enum(FooEnum.bar, FooEnum)

    value_name = Enum(values='values')

    value_name_default = Enum(FooEnum.bar, values='values')


class EnumTestCase(unittest.TestCase):
    def test_valid_enum(self):
        example_model = ExampleModel(root="model1")
        example_model.root = "model2"

    def test_invalid_enum(self):
        example_model = ExampleModel(root="model1")

        def assign_invalid():
            example_model.root = "not_valid_model"

        self.assertRaises(TraitError, assign_invalid)

    def test_enum_list(self):
        example = EnumListExample()
        self.assertEqual(example.value, 'foo')
        self.assertEqual(example.value_default, 'bar')
        self.assertEqual(example.value_name, 'foo')
        self.assertEqual(example.value_name_default, 'bar')

        example.value = 'bar'
        self.assertEqual(example.value, 'bar')

        with self.assertRaises(TraitError):
            example.value = "something"

        with self.assertRaises(TraitError):
            example.value = 0

        example.values = ['one', 'two', 'three']
        example.value_name = 'two'
        self.assertEqual(example.value_name, 'two')

        with self.assertRaises(TraitError):
            example.value_name = 'bar'

    def test_enum_tuple(self):
        example = EnumTupleExample()
        self.assertEqual(example.value, 'foo')
        self.assertEqual(example.value_default, 'bar')
        self.assertEqual(example.value_name, 'foo')
        self.assertEqual(example.value_name_default, 'bar')

        example.value = 'bar'
        self.assertEqual(example.value, 'bar')

        with self.assertRaises(TraitError):
            example.value = "something"

        with self.assertRaises(TraitError):
            example.value = 0

        example.values = ('one', 'two', 'three')
        example.value_name = 'two'
        self.assertEqual(example.value_name, 'two')

        with self.assertRaises(TraitError):
            example.value_name = 'bar'

    def test_enum_enum(self):
        example = EnumEnumExample()
        self.assertEqual(example.value, FooEnum.foo)
        self.assertEqual(example.value_default, FooEnum.bar)
        self.assertEqual(example.value_name, FooEnum.foo)
        self.assertEqual(example.value_name_default, FooEnum.bar)

        example.value = FooEnum.bar
        self.assertEqual(example.value, FooEnum.bar)

        with self.assertRaises(TraitError):
            example.value = "foo"

        with self.assertRaises(TraitError):
            example.value = 0

        example.values = OtherEnum
        example.value_name = OtherEnum.two
        self.assertEqual(example.value_name, OtherEnum.two)

        with self.assertRaises(TraitError):
            example.value_name = FooEnum.bar
