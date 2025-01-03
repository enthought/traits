# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.observation.api import SetChangeEvent
from traits.observation._set_change_event import set_event_factory
from traits.trait_set_object import TraitSet


class TestSetChangeEvent(unittest.TestCase):

    def test_set_change_event_repr(self):
        event = SetChangeEvent(
            object=set(),
            added={1},
            removed={3},
        )
        actual = repr(event)
        self.assertEqual(
            actual,
            "SetChangeEvent(object=set(), removed={3}, added={1})",
        )


class TestSetEventFactory(unittest.TestCase):
    """ Test event factory compatibility with TraitSet.notify """

    def test_trait_set_notification_compat(self):

        events = []

        def notifier(*args, **kwargs):
            event = set_event_factory(*args, **kwargs)
            events.append(event)

        trait_set = TraitSet(
            [1, 2, 3],
            notifiers=[notifier],
        )

        # when
        trait_set.add(4)

        # then
        event, = events
        self.assertIs(event.object, trait_set)
        self.assertEqual(event.added, {4})
        self.assertEqual(event.removed, set())

        # when
        events.clear()
        trait_set.remove(4)

        # then
        event, = events
        self.assertEqual(event.added, set())
        self.assertEqual(event.removed, {4})
