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


class TestTraitEventNotifier(unittest.TestCase):

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
