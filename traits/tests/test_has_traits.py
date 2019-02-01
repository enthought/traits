import unittest

from traits.has_traits import (
    update_traits_class_dict,
    on_trait_change,
    BaseTraits,
    ClassTraits,
    PrefixTraits,
    ListenerTraits,
    InstanceTraits,
    HasTraits,
)
from traits.traits import ForwardProperty, generic_trait
from traits.trait_types import Float, Int


def _dummy_getter(self):
    pass


def _dummy_setter(self, value):
    pass


def _dummy_validator(self, value):
    pass


class TestCreateTraitsMetaDict(unittest.TestCase):
    def test_class_attributes(self):
        # Given
        class_name = "MyClass"
        bases = (object,)
        class_dict = {"attr": "something"}
        is_category = False

        # When
        update_traits_class_dict(class_name, bases, class_dict, is_category)

        # Then; Check that the original Python-level class attributes are still
        # present in the class dictionary.
        self.assertEqual(class_dict["attr"], "something")

        # Other traits dictionaries should be empty.
        for kind in (BaseTraits, ClassTraits, ListenerTraits, InstanceTraits):
            self.assertEqual(class_dict[kind], {})

    def test_forward_property(self):
        # Given
        class_name = "MyClass"
        bases = (object,)
        class_dict = {
            "attr": "something",
            "my_property": ForwardProperty({}),
            "_get_my_property": _dummy_getter,
            "_set_my_property": _dummy_setter,
            "_validate_my_property": _dummy_validator,
        }
        is_category = False

        # When
        update_traits_class_dict(class_name, bases, class_dict, is_category)

        # Then
        self.assertEqual(class_dict[ListenerTraits], {})
        self.assertEqual(class_dict[InstanceTraits], {})

        # Both ClassTraits and BaseTraits should contain a single trait (the
        # property we created)
        self.assertEqual(len(class_dict[BaseTraits]), 1)
        self.assertEqual(len(class_dict[ClassTraits]), 1)
        self.assertIs(
            class_dict[BaseTraits]["my_property"],
            class_dict[ClassTraits]["my_property"],
        )

        # The class_dict should still have the entry for `attr`, but not
        # `my_property`.
        self.assertEqual(class_dict["attr"], "something")
        self.assertNotIn("my_property", class_dict)

    def test_standard_trait(self):
        # Given
        class_name = "MyClass"
        bases = (object,)
        class_dict = {"attr": "something", "my_int": Int}
        is_category = False

        # When
        update_traits_class_dict(class_name, bases, class_dict, is_category)

        # Then
        self.assertEqual(class_dict[ListenerTraits], {})
        self.assertEqual(class_dict[InstanceTraits], {})

        # Both ClassTraits and BaseTraits should contain a single trait (the
        # Int trait)
        self.assertEqual(len(class_dict[BaseTraits]), 1)
        self.assertEqual(len(class_dict[ClassTraits]), 1)
        self.assertIs(
            class_dict[BaseTraits]["my_int"], class_dict[ClassTraits]["my_int"]
        )

        # The class_dict should still have the entry for `attr`, but not
        # `my_int`.
        self.assertEqual(class_dict["attr"], "something")
        self.assertNotIn("my_int", class_dict)

    def test_prefix_trait(self):
        # Given
        class_name = "MyClass"
        bases = (object,)
        class_dict = {"attr": "something", "my_int_": Int}  # prefix trait
        is_category = False

        # When
        update_traits_class_dict(class_name, bases, class_dict, is_category)

        # Then
        for kind in (BaseTraits, ClassTraits, ListenerTraits, InstanceTraits):
            self.assertEqual(class_dict[kind], {})

        self.assertIn("my_int", class_dict[PrefixTraits])

        # The class_dict should still have the entry for `attr`, but not
        # `my_int`.
        self.assertEqual(class_dict["attr"], "something")
        self.assertNotIn("my_int", class_dict)

    def test_listener_trait(self):
        # Given
        @on_trait_change("something")
        def listener(self):
            pass

        class_name = "MyClass"
        bases = (object,)
        class_dict = {"attr": "something", "my_listener": listener}
        is_category = False

        # When
        update_traits_class_dict(class_name, bases, class_dict, is_category)

        # Then
        self.assertEqual(class_dict[BaseTraits], {})
        self.assertEqual(class_dict[ClassTraits], {})
        self.assertEqual(class_dict[InstanceTraits], {})
        self.assertEqual(
            class_dict[ListenerTraits],
            {
                "my_listener": (
                    "method",
                    {
                        "pattern": "something",
                        "post_init": False,
                        "dispatch": "same",
                    },
                )
            },
        )

    def test_python_property(self):
        # Given
        class_name = "MyClass"
        bases = (object,)
        class_dict = {
            "attr": "something",
            "my_property": property(_dummy_getter),
        }
        is_category = False

        # When
        update_traits_class_dict(class_name, bases, class_dict, is_category)

        # Then
        self.assertEqual(class_dict[BaseTraits], {})
        self.assertEqual(class_dict[InstanceTraits], {})
        self.assertEqual(class_dict[ListenerTraits], {})
        self.assertIs(class_dict[ClassTraits]["my_property"], generic_trait)

    def test_complex_baseclass(self):
        # Given
        class Base(HasTraits):
            x = Int

        class_name = "MyClass"
        bases = (Base,)
        class_dict = {"attr": "something", "my_trait": Float()}
        is_category = False

        # When
        update_traits_class_dict(class_name, bases, class_dict, is_category)

        # Then
        self.assertEqual(class_dict[InstanceTraits], {})
        self.assertEqual(class_dict[ListenerTraits], {})
        self.assertIs(
            class_dict[BaseTraits]["x"], class_dict[ClassTraits]["x"]
        )
        self.assertIs(
            class_dict[BaseTraits]["my_trait"],
            class_dict[ClassTraits]["my_trait"],
        )
