# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest
from unittest import mock
import weakref

from traits.api import HasTraits, Instance, Int
from traits.observation._observer_change_notifier import ObserverChangeNotifier
from traits.observation._observer_graph import ObserverGraph
from traits.observation.exceptions import NotifierNotFound


def dispatch_here(handler, event):
    handler(event)


def create_notifier(**kwargs):
    """ Convenient function for creating an instance of ObserverChangeNotifier
    for testing purposes.
    """
    values = dict(
        graph=mock.Mock(),
        observer_handler=mock.Mock(),
        event_factory=mock.Mock(),
        prevent_event=lambda event: False,
        handler=mock.Mock(),
        target=mock.Mock(),
        dispatcher=dispatch_here,
    )
    values.update(kwargs)
    return ObserverChangeNotifier(**values)


class DummyClass:

    def __init__(self):
        self.notifiers = []

    def _notifiers(self, force_create):
        return self.notifiers

    def dummy_method(self):
        pass


class TestObserverChangeNotifierCall(unittest.TestCase):
    """ Tests for the notifier being a callable."""

    def test_init_and_call(self):
        graph = mock.Mock()
        observer_handler = mock.Mock()
        event_factory = mock.Mock(return_value="Event")
        handler = mock.Mock()
        target = mock.Mock()
        dispatcher = mock.Mock()

        notifier = create_notifier(
            observer_handler=observer_handler,
            graph=graph,
            handler=handler,
            target=target,
            dispatcher=dispatcher,
            event_factory=event_factory,
        )
        notifier(a=1, b=2)

        event_factory.assert_called_once_with(a=1, b=2)
        observer_handler.assert_called_once_with(
            event="Event",
            graph=graph,
            handler=handler,
            target=target,
            dispatcher=dispatcher,
        )

    def test_call_with_prevent_event(self):

        observer_handler = mock.Mock()
        handler = mock.Mock()
        target = mock.Mock()

        notifier = create_notifier(
            observer_handler=observer_handler,
            handler=handler,
            target=target,
            event_factory=lambda value: value,
            prevent_event=lambda event: event != "Fire",
        )

        # when
        notifier("Hello")

        # then
        # silenced by prevent_event
        self.assertEqual(observer_handler.call_count, 0)

        # when
        notifier("Fire")

        # then
        # it got through
        self.assertEqual(observer_handler.call_count, 1)


class TestObserverChangeNotifierWeakrefTarget(unittest.TestCase):
    """ Tests for weak references on targets.
    """

    def test_target_can_be_garbage_collected(self):
        # It is a common use case that the target is an instance
        # of HasTraits and the notifier is attached to an internal
        # object inside target. The notifier should not prevent
        # the target from being garbage collected.
        target = mock.Mock()
        target_ref = weakref.ref(target)

        # Holding reference to the notifier does not prevent
        # the target from being deleted.
        notifier = create_notifier(target=target)  # noqa: F841

        # when
        del target

        # then
        self.assertIsNone(target_ref())

    def test_deleted_target_silence_notifier(self):
        # If the target is deleted, the notifier is silenced
        target = mock.Mock()
        observer_handler = mock.Mock()

        notifier = create_notifier(
            observer_handler=observer_handler, target=target)

        # when
        del target
        notifier(a=1, b=2)

        # then
        observer_handler.assert_not_called()


class TestObserverChangeNotifierWeakrefHandler(unittest.TestCase):
    """ Test for using weak references when the user handler is a method
    of an instance.
    """

    def test_instance_can_be_garbage_collected(self):
        # It is a common use case the user's handler is an instance method.
        # The notifier should not prevent the instance from being
        # garbage collected.
        instance = DummyClass()
        instance_ref = weakref.ref(instance)

        notifier = create_notifier(handler=instance.dummy_method)  # noqa: F841

        # when
        del instance

        # then
        self.assertIsNone(instance_ref())

    def test_deleted_handler_silence_notifier(self):
        # If the handler is an instance method and the instance is garbage
        # collected, the notifier is silenced.

        # Create a dummy observer_handler otherwise the default mock object
        # keep references to call argument during the sanity check.
        def observer_handler(*args, **kwargs):
            pass

        instance = DummyClass()
        method_ref = weakref.WeakMethod(instance.dummy_method)
        target = mock.Mock()
        event_factory = mock.Mock()
        notifier = create_notifier(
            observer_handler=observer_handler,
            target=target,
            handler=instance.dummy_method,
            event_factory=event_factory,
        )

        # sanity check
        notifier(b=3)
        self.assertEqual(event_factory.call_count, 1)
        event_factory.reset_mock()

        # when
        del instance
        self.assertIsNone(method_ref())
        notifier(a=1, b=2)

        # then
        event_factory.assert_not_called()


class TestObserverChangeEquals(unittest.TestCase):
    """ Test ObserverChangeNotifier.equals """

    def test_notifier_equals(self):
        observer_handler = mock.Mock()
        handler = mock.Mock()
        graph = mock.Mock()
        target = mock.Mock()

        notifier1 = create_notifier(
            observer_handler=observer_handler,
            handler=handler,
            graph=graph,
            target=target,
            dispatcher=dispatch_here,
        )
        notifier2 = create_notifier(
            observer_handler=observer_handler,
            handler=handler,
            graph=graph,
            target=target,
            dispatcher=dispatch_here,
        )
        self.assertTrue(
            notifier1.equals(notifier2),
            "Expected notifier1 to see notifier2 as equals."
        )
        self.assertTrue(
            notifier2.equals(notifier1),
            "Expected notifier2 to see notifier1 as equals."
        )

    def test_notifier_observer_handler_not_equal(self):
        # Test notifier differentiates the identity of
        # the observer_handler.
        handler = mock.Mock()
        graph = mock.Mock()
        target = mock.Mock()

        notifier1 = create_notifier(
            observer_handler=mock.Mock(),
            handler=handler,
            graph=graph,
            target=target,
            dispatcher=dispatch_here,
        )
        notifier2 = create_notifier(
            observer_handler=mock.Mock(),
            handler=handler,
            graph=graph,
            target=target,
            dispatcher=dispatch_here,
        )
        self.assertFalse(
            notifier1.equals(notifier2),
            "Expected notifier1 to see notifier2 as different."
        )
        self.assertFalse(
            notifier2.equals(notifier1),
            "Expected notifier2 to see notifier1 as different."
        )

    def test_notifier_handler_not_equal(self):
        # Test notifier differentiates the identity of the
        # user's handler
        observer_handler = mock.Mock()
        graph = mock.Mock()
        target = mock.Mock()

        notifier1 = create_notifier(
            observer_handler=observer_handler,
            handler=mock.Mock(),
            graph=graph,
            target=target,
            dispatcher=dispatch_here,
        )
        notifier2 = create_notifier(
            observer_handler=observer_handler,
            handler=mock.Mock(),
            graph=graph,
            target=target,
            dispatcher=dispatch_here,
        )
        self.assertFalse(
            notifier1.equals(notifier2),
            "Expected notifier1 to see notifier2 as different."
        )
        self.assertFalse(
            notifier2.equals(notifier1),
            "Expected notifier2 to see notifier1 as different."
        )

    def test_notifier_graph_not_equal(self):
        # Test notifier differentiates the identity of the
        # graph.
        observer_handler = mock.Mock()
        handler = mock.Mock()
        target = mock.Mock()

        notifier1 = create_notifier(
            observer_handler=observer_handler,
            handler=handler,
            graph=mock.Mock(),
            target=target,
            dispatcher=dispatch_here,
        )
        notifier2 = create_notifier(
            observer_handler=observer_handler,
            handler=handler,
            graph=mock.Mock(),
            target=target,
            dispatcher=dispatch_here,
        )
        self.assertFalse(
            notifier1.equals(notifier2),
            "Expected notifier1 to see notifier2 as different."
        )
        self.assertFalse(
            notifier2.equals(notifier1),
            "Expected notifier2 to see notifier1 as different."
        )

    def test_notifier_target_not_equals(self):
        # Test notifier differentiates the identity of target.

        observer_handler = mock.Mock()
        handler = mock.Mock()
        graph = mock.Mock()
        target1 = mock.Mock()
        target2 = mock.Mock()

        notifier1 = create_notifier(
            observer_handler=observer_handler,
            handler=handler,
            graph=graph,
            target=target1,
            dispatcher=dispatch_here,
        )
        notifier2 = create_notifier(
            observer_handler=observer_handler,
            handler=handler,
            graph=graph,
            target=target2,
            dispatcher=dispatch_here,
        )
        self.assertFalse(
            notifier1.equals(notifier2),
            "Expected notifier1 to see notifier2 as different."
        )
        self.assertFalse(
            notifier2.equals(notifier1),
            "Expected notifier2 to see notifier1 as different."
        )

    def test_notifier_dispatcher_not_equals(self):
        # Test notifier differentiates the dispatchers.

        observer_handler = mock.Mock()
        handler = mock.Mock()
        graph = mock.Mock()
        target = mock.Mock()
        dispatcher1 = mock.Mock()
        dispatcher2 = mock.Mock()

        notifier1 = create_notifier(
            observer_handler=observer_handler,
            handler=handler,
            graph=graph,
            target=target,
            dispatcher=dispatcher1,
        )
        notifier2 = create_notifier(
            observer_handler=observer_handler,
            handler=handler,
            graph=graph,
            target=target,
            dispatcher=dispatcher2,
        )
        self.assertFalse(
            notifier1.equals(notifier2),
            "Expected notifier1 to see notifier2 as different."
        )
        self.assertFalse(
            notifier2.equals(notifier1),
            "Expected notifier2 to see notifier1 as different."
        )

    def test_notifier_equals_graphs_compared_for_equality(self):
        # New graph can be created that will compare true for equality but not
        # for identity
        graph1 = tuple([1, 2, 3])
        graph2 = tuple([1, 2, 3])
        observer_handler = mock.Mock()
        handler = mock.Mock()
        target = mock.Mock()

        notifier1 = create_notifier(
            observer_handler=observer_handler,
            handler=handler,
            graph=graph1,
            target=target,
            dispatcher=dispatch_here,
        )
        notifier2 = create_notifier(
            observer_handler=observer_handler,
            handler=handler,
            graph=graph2,
            target=target,
            dispatcher=dispatch_here,
        )
        self.assertTrue(
            notifier1.equals(notifier2),
            "Expected notifier1 to see notifier2 as equals."
        )
        self.assertTrue(
            notifier2.equals(notifier1),
            "Expected notifier2 to see notifier1 as equals."
        )

    def test_notifier_equals_with_different_type(self):
        # test the notifier can handle callables of different types.
        notifier = create_notifier()
        self.assertFalse(notifier.equals(str))

    def test_notifier_instance_method_handler_equal(self):
        # Instance methods are descriptors
        observer_handler = mock.Mock()
        graph = mock.Mock()
        target = mock.Mock()
        instance = DummyClass()

        notifier1 = create_notifier(
            observer_handler=observer_handler,
            handler=instance.dummy_method,
            graph=graph,
            target=target,
            dispatcher=dispatch_here,
        )
        notifier2 = create_notifier(
            observer_handler=observer_handler,
            handler=instance.dummy_method,
            graph=graph,
            target=target,
            dispatcher=dispatch_here,
        )
        self.assertTrue(
            notifier1.equals(notifier2),
            "Expected notifier1 to see notifier2 as equals."
        )
        self.assertTrue(
            notifier2.equals(notifier1),
            "Expected notifier2 to see notifier1 as equals."
        )


class TestObserverChangeNotifierAdd(unittest.TestCase):
    """ Test ObserverChangeNotifier.add_to """

    def test_add_notifier(self):
        instance = DummyClass()

        notifier = create_notifier()

        # when
        notifier.add_to(instance)

        # then
        self.assertEqual(instance.notifiers, [notifier])

    def test_add_to_ignore_same_notifier(self):
        # add_to always appends even if the notifier looks the same.
        handler = mock.Mock()
        observer_handler = mock.Mock()
        graph = mock.Mock()
        target = mock.Mock()
        notifier1 = create_notifier(
            observer_handler=observer_handler,
            graph=graph,
            handler=handler,
            target=target,
        )
        notifier2 = create_notifier(
            observer_handler=observer_handler,
            graph=graph,
            handler=handler,
            target=target,
        )
        instance = DummyClass()

        # when
        notifier1.add_to(instance)
        notifier2.add_to(instance)

        # then
        self.assertEqual(instance.notifiers, [notifier1, notifier2])


class TestObserverChangeNotifierRemove(unittest.TestCase):
    """ Test ObserverChangeNotifier.remove_from """

    def test_remove_notifier(self):
        instance = DummyClass()
        notifier = create_notifier()
        notifier.add_to(instance)

        # when
        notifier.remove_from(instance)

        # then
        self.assertEqual(instance.notifiers, [])

    def test_remove_from_error_if_not_found(self):
        # Test remove_from raises if a notifier is not found.
        instance = DummyClass()
        notifier = create_notifier()
        with self.assertRaises(NotifierNotFound):
            notifier.remove_from(instance)

    def test_remove_from_recognize_equivalent_notifier(self):
        # Test remove_from will remove an equivalent notifier
        instance = DummyClass()

        handler = mock.Mock()
        observer_handler = mock.Mock()
        graph = mock.Mock()
        target = mock.Mock()

        notifier1 = create_notifier(
            handler=handler,
            observer_handler=observer_handler,
            graph=graph,
            target=target,
        )
        notifier2 = create_notifier(
            handler=handler,
            observer_handler=observer_handler,
            graph=graph,
            target=target,
        )

        # when
        notifier1.add_to(instance)
        notifier2.remove_from(instance)

        # then
        self.assertEqual(instance.notifiers, [])


class TestIntegrationHasTraits(unittest.TestCase):
    """ Semi-integration tests with HasTraits notifications.
    """

    def setUp(self):
        self.event_args_list = []

    def handler(self, *args):
        self.event_args_list.append(args)

    def event_factory(self, object, name, old, new):
        event = mock.Mock()
        event.object = object
        event.name = name
        event.old = old
        event.new = new
        return event

    def test_basic_instance_change(self):

        class Bar(HasTraits):
            value = Int()

        class Foo(HasTraits):
            bar = Instance(Bar)

        on_bar_value_changed = self.handler

        bar = Bar()
        foo1 = Foo(bar=bar)
        foo2 = Foo(bar=bar)

        def observer_handler(event, graph, handler, target, dispatcher):
            # Very stupid handler for maintaining notifiers.
            old_notifiers = event.old._trait("value", 2)._notifiers(True)
            old_notifiers.remove(handler)
            new_notifiers = event.new._trait("value", 2)._notifiers(True)
            new_notifiers.append(handler)
            # Ignore graph, which would have been used for propagating
            # notifiers in nested objects.
            # Ignore target, which would have been used as the context
            # for the user handler.
            # Ignore dispatcher, which would otherwise wrap the user handler.

        # Two notifiers are added to bar
        # One "belongs" to foo1, the second one "belongs" to foo2
        bar._trait("value", 2)._notifiers(True).extend([
            on_bar_value_changed,
            on_bar_value_changed,
        ])

        # this is for maintaining notifiers that belong to foo1
        notifier_foo1 = create_notifier(
            observer_handler=observer_handler,
            event_factory=self.event_factory,
            graph=ObserverGraph(node=None),
            handler=on_bar_value_changed,
            target=foo1,
            dispatcher=dispatch_here,
        )
        notifier_foo1.add_to(foo1._trait("bar", 2))

        # this is for maintaining notifiers that belong to foo2
        notifier_foo2 = create_notifier(
            observer_handler=observer_handler,
            event_factory=self.event_factory,
            graph=ObserverGraph(node=None),
            handler=on_bar_value_changed,
            target=foo2,
            dispatcher=dispatch_here,
        )
        notifier_foo2.add_to(foo2._trait("bar", 2))

        # when
        # the bar is changed, the ObserverChangeNotifier is fired so that
        # user handler on Bar.value is maintained.
        self.event_args_list.clear()
        new_bar = Bar(value=1)
        foo1.bar = new_bar
        foo2.bar = new_bar
        new_bar.value += 1

        # then
        self.assertEqual(len(self.event_args_list), 2)

        # when
        # changes on the old bar will not be captured
        self.event_args_list.clear()
        bar.value += 1

        # then
        self.assertEqual(len(self.event_args_list), 0)
