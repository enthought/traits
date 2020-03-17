# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

try:
    from collections.abc import Collection
except ImportError:
    # Python3.5 and below does not have Collection
    from collections import Container as Collection
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


class CustomCollection(Collection):

    def __init__(self, *data):
        self.data = tuple(data)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __contains__(self, x):
        return x in self.data


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


class EnumCollectionExample(HasTraits):
    rgb = Enum("red", CustomCollection("red", "green", "blue"))

    rgb_char = Enum("r", "g", "b")

    numbers = Enum(CustomCollection("one", "two", "three"))

    letters = Enum("abcdefg")

    int_set_enum = Enum(1, {1, 2})

    correct_int_set_enum = Enum([1, {1, 2}])

    yes_no = Enum("yes", "no")


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

    def test_enum_collection(self):
        collection_enum = EnumCollectionExample()
        self.assertEqual("red", collection_enum.rgb)
        self.assertEqual("r", collection_enum.rgb_char)
        self.assertEqual("one", collection_enum.numbers)
        self.assertEqual("abcdefg", collection_enum.letters)

        collection_enum.rgb = "blue"
        self.assertEqual("blue", collection_enum.rgb)

        collection_enum.rgb_char = 'g'
        self.assertEqual("g", collection_enum.rgb_char)

        with self.assertRaises(TraitError):
            collection_enum.rgb = "two"

        with self.assertRaises(TraitError):
            collection_enum.letters = 'b'

        collection_enum.yes_no = "no"
        with self.assertRaises(TraitError):
            collection_enum.yes_no = "n"

        self.assertEqual(1, collection_enum.int_set_enum)
        # Fixing issue #835 introduces the following behaviour, which would
        # have otherwise not thrown a TraitError
        with self.assertRaises(TraitError):
            collection_enum.int_set_enum = {1, 2}

        # But the behaviour can be fixed, as seen below
        self.assertEqual(1, collection_enum.correct_int_set_enum)
        collection_enum.correct_int_set_enum = {1, 2}

        with self.assertRaises(TraitError):
            collection_enum.correct_int_set_enum = 2
