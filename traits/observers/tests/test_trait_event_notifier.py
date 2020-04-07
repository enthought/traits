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


class TestTraitEventNotifier(unittest.TestCase):

    def test_init_trait_event_notifier(self):

        handler = mock.Mock()

        def dispatcher(callable, event):
            handler(event)

        target = mock.Mock()

        def prevent_event(event):
            return False

        def event_factory(*args, **kwargs):
            return "Event"

        notifier = TraitEventNotifier(
            handler=handler,
            target=target,
            dispatcher=dispatcher,
            prevent_event=prevent_event,
            event_factory=event_factory,
        )

        # when
        notifier(a=1, b=2)

        # then
        self.assertEqual(handler.call_count, 1)
        (args, _), = handler.call_args_list
        self.assertEqual(args, ("Event", ))
