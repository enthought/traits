# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

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
from traits.ctrait import CTrait
from traits.traits import ForwardProperty, generic_trait
from traits.trait_types import Event, Float, Instance, Int


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

        # When
        update_traits_class_dict(class_name, bases, class_dict)

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

        # When
        update_traits_class_dict(class_name, bases, class_dict)

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

        # When
        update_traits_class_dict(class_name, bases, class_dict)

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

        # When
        update_traits_class_dict(class_name, bases, class_dict)

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

        # When
        update_traits_class_dict(class_name, bases, class_dict)

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

        # When
        update_traits_class_dict(class_name, bases, class_dict)

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

        # When
        update_traits_class_dict(class_name, bases, class_dict)

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


class TestHasTraits(unittest.TestCase):
    def test__class_traits(self):
        # Exercise the _class_traits() private introspection method.
        class Base(HasTraits):
            pin = Int

        a = Base()
        a_class_traits = a._class_traits()
        self.assertIsInstance(a_class_traits, dict)
        self.assertIn("pin", a_class_traits)
        self.assertIsInstance(a_class_traits["pin"], CTrait)

        b = Base()
        self.assertIs(b._class_traits(), a_class_traits)

    def test__instance_traits(self):
        # Exercise the _instance_traits() private introspection method.
        class Base(HasTraits):
            pin = Int

        a = Base()
        a_instance_traits = a._instance_traits()
        self.assertIsInstance(a_instance_traits, dict)

        # A second call should return the same dictionary.
        self.assertIs(a._instance_traits(), a_instance_traits)

        # A different instance should have its own instance traits dict.
        b = Base()
        self.assertIsNot(b._instance_traits(), a_instance_traits)

    def test__trait_notifications_enabled(self):
        class Base(HasTraits):
            foo = Int(0)

            foo_notify_count = Int(0)

            def _foo_changed(self):
                self.foo_notify_count += 1

        a = Base()

        # Default state is that notifications are enabled.
        self.assertTrue(a._trait_notifications_enabled())

        # Changing foo increments the count.
        old_count = a.foo_notify_count
        a.foo += 1
        self.assertEqual(a.foo_notify_count, old_count + 1)

        # After disabling notifications, count is not increased.
        a._trait_change_notify(False)
        self.assertFalse(a._trait_notifications_enabled())
        old_count = a.foo_notify_count
        a.foo += 1
        self.assertEqual(a.foo_notify_count, old_count)

        # After re-enabling notifications, count is increased.
        a._trait_change_notify(True)
        self.assertTrue(a._trait_notifications_enabled())
        old_count = a.foo_notify_count
        a.foo += 1
        self.assertEqual(a.foo_notify_count, old_count + 1)

    def test__trait_notifications_vetoed(self):
        class SomeEvent(HasTraits):
            event_id = Int()

        class Target(HasTraits):
            event = Event(Instance(SomeEvent))

            event_count = Int(0)

            def _event_fired(self):
                self.event_count += 1

        target = Target()
        event = SomeEvent(event_id=1234)

        # Default state is not vetoed.
        self.assertFalse(event._trait_notifications_vetoed())

        # Firing the event increments the count.
        old_count = target.event_count
        target.event = event
        self.assertEqual(target.event_count, old_count + 1)

        # Now veto the event. Firing the event won't affect the count.
        event._trait_veto_notify(True)
        self.assertTrue(event._trait_notifications_vetoed())
        old_count = target.event_count
        target.event = event
        self.assertEqual(target.event_count, old_count)

        # Unveto the event.
        event._trait_veto_notify(False)
        self.assertFalse(event._trait_notifications_vetoed())
        old_count = target.event_count
        target.event = event
        self.assertEqual(target.event_count, old_count + 1)
