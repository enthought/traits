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

from traits.observers.trait_event_notifier import TraitEventNotifier


def basic_dispatcher(function, event):
    function(event)


def not_prevent_event(event):
    return False


class DummyObservable:

    def __init__(self):
        self.notifiers = []

    def _notifiers(self, force_create):
        return self.notifiers


class TestTraitEventNotifierCall(unittest.TestCase):
    """ Test calling an instance of TraitEventNotifier. """

    def test_init_and_call(self):

        handler = mock.Mock()

        def event_factory(*args, **kwargs):
            return "Event"

        notifier = TraitEventNotifier(
            handler=handler,
            target=None,
            dispatcher=basic_dispatcher,
            prevent_event=not_prevent_event,
            event_factory=event_factory,
        )

        # when
        notifier(a=1, b=2)

        # then
        self.assertEqual(handler.call_count, 1)
        (args, _), = handler.call_args_list
        self.assertEqual(args, ("Event", ))

    def test_capture_exception(self):
        # Any exception from the handler will be captured and
        # logged. This is such that failure in one handler
        # does not prevent other notifiers to be called.

        def misbehaving_handler(event):
            raise ZeroDivisionError("lalalala")

        notifier = TraitEventNotifier(
            handler=misbehaving_handler,
            target=None,
            dispatcher=basic_dispatcher,
            prevent_event=not_prevent_event,
            event_factory=mock.Mock(),
        )

        # when
        with self.assertLogs("traits", level="ERROR") as log_cm:
            notifier(a=1, b=2)

        # then
        content, = log_cm.output
        self.assertIn(
            "Exception occurred in traits notification handler",
            content,
        )
        # The tracback should be included
        self.assertIn("ZeroDivisionError", content)


class TestTraitEventNotifierEqual(unittest.TestCase):
    """ Test comparing two instances of TraitEventNotifier. """

    def test_equals_use_handler_and_target(self):
        # Check the notifier can identify an equivalence
        # using the handler and the target

        def handler1(event):
            pass

        def handler2(event):
            pass

        target1 = mock.Mock()
        target2 = mock.Mock()

        notifier1 = TraitEventNotifier(
            handler=handler1,
            target=target1,
            event_factory=mock.Mock(),
            prevent_event=not_prevent_event,
            dispatcher=basic_dispatcher,
        )
        notifier2 = TraitEventNotifier(
            handler=handler1,
            target=target1,
            event_factory=mock.Mock(),
            prevent_event=not_prevent_event,
            dispatcher=basic_dispatcher,
        )
        notifier3 = TraitEventNotifier(
            handler=handler1,
            target=target2,
            event_factory=mock.Mock(),
            prevent_event=not_prevent_event,
            dispatcher=basic_dispatcher,
        )
        notifier4 = TraitEventNotifier(
            handler=handler2,
            target=target1,
            event_factory=mock.Mock(),
            prevent_event=not_prevent_event,
            dispatcher=basic_dispatcher,
        )
        # then
        self.assertTrue(
            notifier1.equals(notifier2),
            "The two notifiers should consider each other as equal."
        )
        self.assertTrue(
            notifier2.equals(notifier1),
            "The two notifiers should consider each other as equal."
        )
        self.assertFalse(
            notifier3.equals(notifier1),
            "Expected the notifiers to be different because targets are "
            "not identical."
        )
        self.assertFalse(
            notifier4.equals(notifier1),
            "Expected the notifiers to be different because the handlers "
            "do not compare equally."
        )

    def test_equals_compared_to_different_type(self):
        notifier = TraitEventNotifier(
            handler=mock.Mock(),
            target=None,
            event_factory=mock.Mock(),
            prevent_event=not_prevent_event,
            dispatcher=basic_dispatcher,
        )
        self.assertFalse(notifier.equals(float))


class TestTraitEventNotifierAddRemove(unittest.TestCase):
    """ Test TraitEventNotifier capability of adding/removing
    itself to/from an observable.
    """

    def test_add_to_observable(self):
        dummy = DummyObservable()

        notifier = TraitEventNotifier(
            handler=mock.Mock(),
            target=None,
            event_factory=mock.Mock(),
            prevent_event=not_prevent_event,
            dispatcher=basic_dispatcher,
        )

        # when
        notifier.add_to(dummy)

        # then
        self.assertEqual(dummy.notifiers, [notifier])

    def test_add_to_observable_twice_increase_count(self):
        # Test trying to add the "same" notifier results in
        # the existing notifier bumping its own reference
        # count.
        dummy = DummyObservable()

        def handler(event):
            pass

        notifier1 = TraitEventNotifier(
            handler=handler,
            target=None,
            event_factory=mock.Mock(),
            prevent_event=not_prevent_event,
            dispatcher=basic_dispatcher,
        )
        notifier2 = TraitEventNotifier(
            handler=handler,
            target=None,
            event_factory=mock.Mock(),
            prevent_event=not_prevent_event,
            dispatcher=basic_dispatcher,
        )

        # when
        notifier1.add_to(dummy)
        notifier2.add_to(dummy)

        # then
        self.assertEqual(dummy.notifiers, [notifier1])
        self.assertEqual(notifier1._ref_count, 2)

    def test_add_to_observable_different_notifier(self):
        dummy = DummyObservable()

        def handler(event):
            pass

        notifier1 = TraitEventNotifier(
            handler=handler,
            target=None,
            event_factory=mock.Mock(),
            prevent_event=not_prevent_event,
            dispatcher=basic_dispatcher,
        )
        # The target is different!
        notifier2 = TraitEventNotifier(
            handler=handler,
            target=dummy,
            event_factory=mock.Mock(),
            prevent_event=not_prevent_event,
            dispatcher=basic_dispatcher,
        )

        # when
        notifier1.add_to(dummy)
        notifier2.add_to(dummy)

        # then
        self.assertEqual(dummy.notifiers, [notifier1, notifier2])

    def test_remove_from_observable(self):
        # Test creating two equivalent notifiers.
        # The second notifier is able to remove the first one
        # from the observable as if the first one was itself.
        dummy = DummyObservable()

        def handler(event):
            pass

        notifier1 = TraitEventNotifier(
            handler=handler,
            target=None,
            event_factory=mock.Mock(),
            prevent_event=not_prevent_event,
            dispatcher=basic_dispatcher,
        )
        notifier2 = TraitEventNotifier(
            handler=handler,
            target=None,
            event_factory=mock.Mock(),
            prevent_event=not_prevent_event,
            dispatcher=basic_dispatcher,
        )

        # when
        notifier1.add_to(dummy)
        self.assertEqual(dummy.notifiers, [notifier1])
        notifier2.remove_from(dummy)

        # then
        self.assertEqual(dummy.notifiers, [])

    def test_remove_from_observable_with_ref_count(self):
        # Test reference counting logic in remove_from
        dummy = DummyObservable()

        def handler(event):
            pass

        notifier1 = TraitEventNotifier(
            handler=handler,
            target=None,
            event_factory=mock.Mock(),
            prevent_event=not_prevent_event,
            dispatcher=basic_dispatcher,
        )
        notifier2 = TraitEventNotifier(
            handler=handler,
            target=None,
            event_factory=mock.Mock(),
            prevent_event=not_prevent_event,
            dispatcher=basic_dispatcher,
        )

        # when
        # add_to is called twice.
        notifier1.add_to(dummy)
        notifier1.add_to(dummy)
        self.assertEqual(dummy.notifiers, [notifier1])

        # when
        # removing it once
        notifier2.remove_from(dummy)

        # then
        self.assertEqual(dummy.notifiers, [notifier1])

        # when
        # removing it the second time
        notifier2.remove_from(dummy)

        # then
        # will remove the callable.
        self.assertEqual(dummy.notifiers, [])


class TestTraitEventNotifierWeakref(unittest.TestCase):
    """ Test weakref handling in TraitEventNotifier."""

    def test_notifier_does_not_prevent_object_deletion(self):
        # Typical use case: target is an instance of HasTraits
        # and the notifier is attached to an internal object
        # inside the target.
        # The reverse reference to target should not prevent
        # the target from being garbage collected when not in use.
        target = DummyObservable()
        target.internal_object = DummyObservable()
        target_ref = weakref.ref(target)

        notifier = TraitEventNotifier(
            handler=mock.Mock(),
            target=target,
            event_factory=mock.Mock(),
            prevent_event=not_prevent_event,
            dispatcher=basic_dispatcher,
        )
        notifier.add_to(target.internal_object)

        # when
        del target

        # then
        self.assertIsNone(target_ref())

    def test_equals_differentiate_no_target_tracked(self):
        # Test differentiation between when the target is deleted
        # and when there is no target being tracked.
        dummy = DummyObservable()

        def handler(event):
            pass

        notifier1 = TraitEventNotifier(
            handler=handler,
            target=dummy,
            event_factory=mock.Mock(),
            prevent_event=not_prevent_event,
            dispatcher=basic_dispatcher,
        )
        notifier2 = TraitEventNotifier(
            handler=handler,
            target=None,
            event_factory=mock.Mock(),
            prevent_event=not_prevent_event,
            dispatcher=basic_dispatcher,
        )

        del dummy

        self.assertIsNone(notifier1.target())
        self.assertFalse(notifier1.equals(notifier2))

    def test_callable_disabled_if_target_removed(self):
        target = mock.Mock()

        handler = mock.Mock()

        notifier = TraitEventNotifier(
            handler=handler,
            target=target,
            event_factory=mock.Mock(),
            prevent_event=not_prevent_event,
            dispatcher=basic_dispatcher,
        )

        # sanity check
        notifier(a=1, b=2)
        self.assertEqual(handler.call_count, 1)
        handler.reset_mock()

        # when
        del target

        # then
        notifier(a=1, b=2)
        handler.assert_not_called()
