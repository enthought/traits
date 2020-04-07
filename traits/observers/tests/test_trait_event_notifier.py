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
