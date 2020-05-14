# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Integration tests for HasTraits and observe.
"""

import copy
import pickle
import unittest
from unittest import mock

from traits.api import (
    HasTraits,
    Int,
    Instance,
    List,
    observe,
    Str,
)
from traits.observers.api import (
    pop_exception_handler,
    push_exception_handler,
    trait,
)


class SingleValue(HasTraits):

    value = Int()


# Test ``observe`` decorator registers the handlers as expected ---------------

class Foo(HasTraits):
    """ Dummy class with a single value and an instance with a single value
    """
    value = Int()

    single_value_instance = Instance(SingleValue)


class FooWithTextObserver(Foo):
    """ Dummy class for testing the use of string in ``observe``
    """

    value_handler_events = List()

    multi_observer_handler_events = List()

    value_or_single_value_instance_events = List()

    @observe("value")
    def value_handler(self, event):
        self.value_handler_events.append(event)

    @observe("single_value_instance")
    @observe("value")
    @observe("single_value_instance:value")
    def multi_observer_handler(self, event):
        self.multi_observer_handler_events.append(event)

    @observe(["value", "single_value_instance"])
    def value_or_single_value_instance_handler(self, event):
        self.value_or_single_value_instance_events.append(event)


class FooWithExpressionObserver(Foo):
    """ Dummy class for testing the use of Expression instead of str
    in ``observe``
    """

    value_handler_events = List()

    multi_observer_handler_events = List()

    value_or_single_value_instance_events = List()

    @observe(trait("value"))
    def value_handler(self, event):
        self.value_handler_events.append(event)

    @observe(trait("single_value_instance"))
    @observe(trait("value"))
    @observe(trait("single_value_instance", notify=False).trait("value"))
    def multi_observer_handler(self, event):
        self.multi_observer_handler_events.append(event)

    @observe(trait("value") | trait("single_value_instance"))
    def value_or_single_value_instance_handler(self, event):
        self.value_or_single_value_instance_events.append(event)


class TestHasTraitsObserveDecorator(unittest.TestCase):
    """ Integration tests with the user-facing observe decorator.
    """

    def setUp(self):
        push_exception_handler(reraise_exceptions=True)
        self.addCleanup(pop_exception_handler)

    def test_value_observed(self):

        foos = [
            FooWithTextObserver(),
            FooWithExpressionObserver(),
        ]

        for foo in foos:
            with self.subTest(foo=foo):
                foo.value += 1
                self.assertEqual(len(foo.value_handler_events), 1)

    def test_multiple_decorators(self):
        # Test when the observe decorator is stacked

        foos = [
            FooWithTextObserver(),
            FooWithExpressionObserver(),
        ]

        for foo in foos:
            with self.subTest(foo=foo):
                # when
                foo.single_value_instance = SingleValue()

                # then
                self.assertEqual(len(foo.multi_observer_handler_events), 1)

                # when
                foo.value += 1

                # then
                self.assertEqual(len(foo.multi_observer_handler_events), 2)

                # when
                foo.single_value_instance.value += 1

                # then
                self.assertEqual(len(foo.multi_observer_handler_events), 3)

    def test_observe_with_list_of_str_or_expression(self):
        # Test when the expression is a list of str or an equivalent expression

        foos = [
            FooWithTextObserver(),
            FooWithExpressionObserver(),
        ]

        for foo in foos:
            with self.subTest(foo=foo):
                # when
                foo.value += 1

                # then
                self.assertEqual(
                    len(foo.value_or_single_value_instance_events), 1)

                # when
                foo.single_value_instance = SingleValue()

                # then
                self.assertEqual(
                    len(foo.value_or_single_value_instance_events), 2)


# Test ``observe`` instance method registers the handlers as expected ---------

class TestHasTraitsObserveInstanceMethod(unittest.TestCase):
    """ Integration tests with the user-facing observe instance method.
    """

    def setUp(self):
        push_exception_handler(reraise_exceptions=True)
        self.addCleanup(pop_exception_handler)

    def test_observe_instance_method_str(self):
        foo = Foo()

        handler = mock.Mock()

        foo.observe(handler, "value")

        # verify
        foo.value += 1
        self.assertEqual(handler.call_count, 1)

    def test_observe_instance_method_expression(self):
        foo = Foo()

        handler = mock.Mock()

        foo.observe(handler, trait("value"))

        # verify
        foo.value += 1
        self.assertEqual(handler.call_count, 1)

    def test_observe_instance_method_list_of_str(self):

        foo = Foo()
        handler = mock.Mock()
        foo.observe(handler, ["value", "single_value_instance"])

        # verify
        foo.value += 1
        self.assertEqual(handler.call_count, 1)
        handler.reset_mock()

        foo.single_value_instance = SingleValue()
        self.assertEqual(handler.call_count, 1)

    def test_remove_decorated_observer(self):
        # Test it is possible to remove a handler used with the observe
        # decorator

        foo = FooWithExpressionObserver()

        # sanity check
        foo.value += 1
        self.assertEqual(len(foo.value_handler_events), 1)
        foo.value_handler_events = []

        # when
        foo.observe(foo.value_handler, trait("value"), remove=True)
        foo.value += 1

        # then
        self.assertEqual(len(foo.value_handler_events), 0)

    def test_observe_dispatch_ui(self):
        foo = Foo()

        handler = mock.Mock()
        foo.observe(handler, trait("value"), dispatch="ui")

        with mock.patch("traits.trait_notifiers.ui_handler") as mocked:
            foo.value += 1

        self.assertEqual(mocked.call_count, 1)
        ((actual_handler, _), _), = mocked.call_args_list
        self.assertIs(actual_handler, handler)


# Test subclass can inherit the observers defined in the base class -----------

class BaseClass(HasTraits):

    name_events = List()

    @observe("name")
    def name_updated(self, event):
        self.name_events.append(event)


class Subclass(BaseClass):

    name = Str()


class SubclassOverriden(BaseClass):

    name = Str()

    name_updated = None


class TestSubclassInheritObserver(unittest.TestCase):

    def test_observer_from_superclass(self):

        instance = Subclass()
        instance.name = "New name"
        self.assertEqual(len(instance.name_events), 1)

    def test_observer_overridden(self):
        # The handler is overriden, no change event should be registered.
        instance = SubclassOverriden()
        instance.name = "New name"
        self.assertEqual(len(instance.name_events), 0)


# Integration tests for post_init ---------------------------------------------


class Manager(HasTraits):
    name = Str()

    name_changed_event = List()

    @observe("name", post_init=True)
    def _name_updated(self, event):
        self.name_changed_event.append(event)


class TestHasTraitsObservePostInit(unittest.TestCase):

    def setUp(self):
        push_exception_handler(reraise_exceptions=True)
        self.addCleanup(pop_exception_handler)

    def test_observe_post_init_true(self):
        manager = Manager(name="Paul")
        self.assertEqual(manager.name_changed_event, [])

        manager.name = "Mary"
        self.assertEqual(len(manager.name_changed_event), 1)


# Integration tests for default initializer -----------------------------------


class Record(HasTraits):
    number = Int(10)

    default_call_count = Int()

    number_change_events = List()

    def _number_default(self):
        self.default_call_count += 1
        return 99

    @observe('number')
    def handle_number_change(self, event):
        self.number_change_events.append(event)


class TestHasTraitsObserverDefaultHandler(unittest.TestCase):

    def setUp(self):
        push_exception_handler(reraise_exceptions=True)
        self.addCleanup(pop_exception_handler)

    def test_default_not_called_if_init_contains_value(self):
        record = Record(number=123)
        # enthought/traits#94
        self.assertEqual(record.default_call_count, 1)
        self.assertEqual(len(record.number_change_events), 1)
        event, = record.number_change_events
        self.assertEqual(event.object, record)
        self.assertEqual(event.name, "number")
        self.assertEqual(event.old, 99)
        self.assertEqual(event.new, 123)

    def test_default_not_called_for_empty_init(self):
        record = Record()
        self.assertEqual(record.default_call_count, 0)


# Integration test for picklability -------------------------------------------


class TestHasTraitsWithObservePickle(unittest.TestCase):

    def test_pickle_has_traits_with_observe(self):
        classes = [
            FooWithTextObserver,
            FooWithExpressionObserver,
        ]

        for class_ in classes:
            with self.subTest(class_=class_):
                foo = class_()
                for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
                    serialized = pickle.dumps(foo, protocol=protocol)
                    deserialized = pickle.loads(serialized)

                    deserialized.value += 1
                    self.assertEqual(len(deserialized.value_handler_events), 1)


# Integration test for deep copy compatibility --------------------------------


class TestHasTraitsWithObserveDeepCopy(unittest.TestCase):
    """ HasTraits with observers can be deep copied.
    """

    def test_deep_copy_has_traits_with_observe(self):
        classes = [
            FooWithTextObserver,
            FooWithExpressionObserver,
        ]

        for class_ in classes:
            with self.subTest(class_=class_):
                foo = class_()

                copied = copy.deepcopy(foo)
                copied.value += 1

                self.assertEqual(len(copied.value_handler_events), 1)
                self.assertEqual(len(foo.value_handler_events), 0)
