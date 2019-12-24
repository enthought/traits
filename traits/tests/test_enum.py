import enum
import unittest

from traits.api import Enum, HasTraits, List, Property, TraitError


class FooEnum(enum.Enum):
    foo = 0
    bar = 1
    baz = 2


class ExampleModel(HasTraits):
    valid_models = Property(List)
    root = Enum(values="valid_models")

    def _get_valid_models(self):
        return ["model1", "model2", "model3"]


class EnumEnumExample(HasTraits):

    value = Enum(FooEnum)

    value_default = Enum(FooEnum.bar, FooEnum)


class EnumTestCase(unittest.TestCase):
    def test_valid_enum(self):
        example_model = ExampleModel(root="model1")
        example_model.root = "model2"

    def test_invalid_enum(self):
        example_model = ExampleModel(root="model1")

        def assign_invalid():
            example_model.root = "not_valid_model"

        self.assertRaises(TraitError, assign_invalid)

    def test_enum_enum(self):
        example = EnumEnumExample()
        self.assertEqual(example.value, FooEnum.foo)
        self.assertEqual(example.value_default, FooEnum.bar)

        example.value = FooEnum.bar
        self.assertEqual(example.value, FooEnum.bar)

        with self.assertRaises(TraitError):
            example.value = "foo"

        with self.assertRaises(TraitError):
            example.value = 0
