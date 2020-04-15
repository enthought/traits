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
from unittest import mock
import weakref

from traits.observers._observer_change_notifier import ObserverChangeNotifier


def create_notifier(**kwargs):
    """ Convenient function for creating an instance of ObserverChangeNotifier
    for testing purposes.
    """
    values = dict(
        path=mock.Mock(),
        observer_handler=mock.Mock(),
        event_factory=mock.Mock(),
        handler=mock.Mock(),
        target=mock.Mock(),
        dispatcher=mock.Mock(),
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

    def test_init_and_call(self):
        path = mock.Mock()
        observer_handler = mock.Mock()
        event_factory = mock.Mock(return_value="Event")
        handler = mock.Mock()
        target = mock.Mock()
        dispatcher = mock.Mock()

        notifier = create_notifier(
            observer_handler=observer_handler,
            path=path,
            handler=handler,
            target=target,
            dispatcher=dispatcher,
            event_factory=event_factory,
        )
        notifier(a=1, b=2)

        event_factory.assert_called_once_with(a=1, b=2)
        observer_handler.assert_called_once_with(
            event="Event",
            path=path,
            handler=handler,
            target=target,
            dispatcher=dispatcher,
        )


class TestObserverChangeNotifierWeakrefTarget(unittest.TestCase):

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


class TestObserverChangeNotifierAddRemove(unittest.TestCase):

    def test_add_notifier(self):
        instance = DummyClass()

        notifier = create_notifier()

        # when
        notifier.add_to(instance)

        # then
        self.assertEqual(instance.notifiers, [notifier])

    def test_remove_notifier(self):
        instance = DummyClass()
        notifier = create_notifier()
        notifier.add_to(instance)

        # when
        notifier.remove_from(instance)

        # then
        self.assertEqual(instance.notifiers, [])