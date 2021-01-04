# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import copy
import pickle
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
    observe,
    ObserverTraits,
    SingletonHasTraits,
    SingletonHasStrictTraits,
    SingletonHasPrivateTraits,
)
from traits.ctrait import CTrait
from traits.observation.api import trait
from traits.observation.exception_handling import (
    pop_exception_handler,
    push_exception_handler,
)
from traits.traits import ForwardProperty, generic_trait
from traits.trait_types import Event, Float, Instance, Int, List, Map, Str


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

    def test_observe_trait(self):
        # Given
        @observe(trait("value"), post_init=True, dispatch="ui")
        @observe("name")
        def handler(event):
            pass

        class_name = "MyClass"
        bases = (object,)
        class_dict = {"attr": "something", "my_listener": handler}

        # When
        update_traits_class_dict(class_name, bases, class_dict)

        # Then
        self.assertEqual(
            class_dict[ObserverTraits],
            {
                "my_listener": [
                    {
                        "expression": [trait("name")],
                        "post_init": False,
                        "dispatch": "same",
                        "handler_getter": getattr,
                    },
                    {
                        "expression": [trait("value")],
                        "post_init": True,
                        "dispatch": "ui",
                        "handler_getter": getattr,
                    },
                ],
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

    def test__object_notifiers_vetoed(self):

        class SomeEvent(HasTraits):
            event_id = Int()

        class Target(HasTraits):
            event = Event(Instance(SomeEvent))

            event_count = Int(0)

        target = Target()
        event = SomeEvent(event_id=9)

        def object_handler(object, name, old, new):
            if name == "event":
                object.event_count += 1

        target.on_trait_change(object_handler, name="anytrait")

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

    def test_traits_inited(self):
        foo = HasTraits()

        self.assertTrue(foo.traits_inited())

    def test__trait_set_inited(self):
        foo = HasTraits.__new__(HasTraits)

        self.assertFalse(foo.traits_inited())

        foo._trait_set_inited()

        self.assertTrue(foo.traits_inited())

    def test_generic_getattr_exception(self):
        # Regression test for enthought/traits#946.

        class PropertyLike:
            """
            Data descriptor giving a property-like object that produces
            successive reciprocals on __get__. This means that it raises
            on first access, but not on subsequent accesses.
            """
            def __init__(self):
                self.n = 0

            def __get__(self, obj, type=None):
                old_n = self.n
                self.n += 1
                return 1 / old_n

            # Need a __set__ method to make this a data descriptor.
            def __set__(self, obj, value):
                raise AttributeError("Read-only descriptor")

        class A(HasTraits):
            fruit = PropertyLike()

            banana_ = Int(1729)

        a = A()

        # The exception raised on the first attribute access should be
        # propagated.
        with self.assertRaises(ZeroDivisionError):
            a.fruit

        # Exercise the code path where the PyObject_GenericGetAttr call raises
        # AttributeError. In this case, we catch the error but the prefix trait
        # machinery raises a new AttributeError.
        with self.assertRaises(AttributeError):
            a.veg

        # Exercise the case where the prefix traits machinery goes on to
        # produce a valid result.
        self.assertEqual(a.banananana, 1729)

    def test_deepcopy_memoization(self):
        class A(HasTraits):
            x = Int()
            y = Str()

        a = A()
        objs = [a, a]
        objs_copy = copy.deepcopy(objs)
        self.assertIsNot(objs_copy[0], objs[0])
        self.assertIs(objs_copy[0], objs_copy[1])


class TestObjectNotifiers(unittest.TestCase):
    """ Test calling object notifiers. """

    def test_notifiers_empty(self):

        class Foo(HasTraits):
            x = Int()

        foo = Foo(x=1)
        self.assertEqual(foo._notifiers(True), [])

    def test_notifiers_on_object(self):

        class Foo(HasTraits):
            x = Int()

        foo = Foo(x=1)
        self.assertEqual(foo._notifiers(True), [])

        # when
        def handler():
            pass

        foo.on_trait_change(handler, name="anytrait")

        # then
        notifiers = foo._notifiers(True)
        self.assertEqual(len(notifiers), 1)
        onotifier, = notifiers
        self.assertEqual(onotifier.handler, handler)


class TestCallNotifiers(unittest.TestCase):

    def test_trait_and_object_notifiers_called(self):

        side_effects = []

        class Foo(HasTraits):
            x = Int()
            y = Int()

            def _x_changed(self):
                side_effects.append("x")

        def object_handler():
            side_effects.append("object")

        foo = Foo()
        foo.on_trait_change(object_handler, name="anytrait")

        # when
        side_effects.clear()
        foo.x = 3

        # then
        self.assertEqual(side_effects, ["x", "object"])

        # when
        side_effects.clear()
        foo.y = 4

        # then
        self.assertEqual(side_effects, ["object"])

    def test_trait_notifier_modify_object_notifier(self):
        # Test when a trait notifier has a side effect of adding
        # an object notifier

        side_effects = []

        def object_handler1():
            side_effects.append("object1")

        def object_handler2():
            side_effects.append("object2")

        class Foo(HasTraits):
            x = Int()
            y = Int()

            def _x_changed(self):
                side_effects.append("x")

                # add the second object notifier
                self.on_trait_change(object_handler2, name="anytrait")

        # Add an object handler so that the list is created for mutation.
        foo = Foo()
        foo.on_trait_change(object_handler1, name="anytrait")

        # when
        side_effects.clear()
        foo.x = 1

        # then
        # the second object notifier is not called.
        self.assertEqual(side_effects, ["x", "object1"])

        # But the object notifier is added and will be used the next time
        # when
        side_effects.clear()
        foo.y = 2

        # then
        # the second object notifier is called.
        self.assertEqual(side_effects, ["object1", "object2"])


class TestDeprecatedHasTraits(unittest.TestCase):
    def test_deprecated(self):
        class TestSingletonHasTraits(SingletonHasTraits):
            pass

        class TestSingletonHasStrictTraits(SingletonHasStrictTraits):
            pass

        class TestSingletonHasPrivateTraits(SingletonHasPrivateTraits):
            pass

        with self.assertWarns(DeprecationWarning):
            TestSingletonHasTraits()

        with self.assertWarns(DeprecationWarning):
            TestSingletonHasStrictTraits()

        with self.assertWarns(DeprecationWarning):
            TestSingletonHasPrivateTraits()


class MappedWithDefault(HasTraits):

    married = Map({"yes": 1, "yeah": 1, "no": 0, "nah": 0})

    default_calls = Int(0)

    def _married_default(self):
        self.default_calls += 1
        return "yes"


class TestHasTraitsPickling(unittest.TestCase):

    def test_pickle_mapped_default_method(self):
        person = MappedWithDefault()

        # Sanity check
        self.assertEqual(person.default_calls, 0)

        reconstituted = pickle.loads(pickle.dumps(person))

        self.assertEqual(reconstituted.married_, 1)
        self.assertEqual(reconstituted.married, "yes")
        self.assertEqual(reconstituted.default_calls, 1)


class Person(HasTraits):
    age = Int()


class PersonWithObserve(Person):
    events = List()

    @observe(trait("age"))
    def handler(self, event):
        self.events.append(event)


class TestHasTraitsObserveHook(unittest.TestCase):
    """ Test observe decorator and the observe method.
    """

    def setUp(self):
        push_exception_handler(reraise_exceptions=True)
        self.addCleanup(pop_exception_handler)

    def test_overloaded_signature_expression(self):
        # Test the overloaded signature for expression
        expressions = [
            trait("age"),
            "age",
            [trait("age")],
            ["age"],
        ]
        for expression in expressions:

            class NewPerson(Person):
                events = List()

                @observe(expression)
                def handler(self, event):
                    self.events.append(event)

            person = NewPerson()
            person.age += 1
            self.assertEqual(len(person.events), 1)

    def test_observe_method_remove(self):
        events = []
        person = Person()
        person.observe(events.append, "age")

        # sanity check
        person.age += 1
        self.assertEqual(len(events), 1)

        # when
        person.observe(events.append, "age", remove=True)

        # then
        person.age += 1
        self.assertEqual(len(events), 1)  # unchanged

    def test_observe_dispatch_ui(self):
        # Test to ensure "ui" is one of the allowed value
        # Not testing the actual effect as it requires GUI event loop
        # as well as assumption on the local thread identity while running
        # the test.
        person = Person()

        person.observe(repr, trait("age"), dispatch="ui")

    def test_inherit_observer_from_superclass(self):
        # Test observers can be inherited
        class BaseClass(HasTraits):
            events = List()

            @observe("value")
            def handler(self, event):
                self.events.append(event)

        class SubClass(BaseClass):
            value = Int()

        instance = SubClass()
        instance.value += 1
        self.assertEqual(len(instance.events), 1)

    def test_observer_overridden(self):
        # The handler is overriden, no change event should be registered.
        class BaseClass(HasTraits):
            events = List()

            @observe("value")
            def handler(self, event):
                self.events.append(event)

        class SubclassOverriden(BaseClass):
            value = Int()
            handler = None

        instance = SubclassOverriden()
        instance.value += 1
        self.assertEqual(len(instance.events), 0)

    def test_observe_post_init(self):

        class PersonWithPostInt(Person):
            events = List()

            @observe("age", post_init=True)
            def handler(self, event):
                self.events.append(event)

        person = PersonWithPostInt(age=10)
        self.assertEqual(len(person.events), 0)

        person.age += 1
        self.assertEqual(len(person.events), 1)

    def test_observe_pickability(self):
        # Test an HasTraits with observe can be pickled.
        person = PersonWithObserve()
        for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
            serialized = pickle.dumps(person, protocol=protocol)
            deserialized = pickle.loads(serialized)

            deserialized.age += 1
            self.assertEqual(len(deserialized.events), 1)

    def test_observe_deepcopy(self):
        # Test an HasTraits with observe can be deepcopied.
        person = PersonWithObserve()
        copied = copy.deepcopy(person)
        copied.age += 1
        self.assertEqual(len(copied.events), 1)
        self.assertEqual(len(person.events), 0)
