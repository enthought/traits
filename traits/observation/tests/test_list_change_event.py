# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.observation._list_change_event import (
    ListChangeEvent,
    list_event_factory,
)
from traits.trait_list_object import TraitList


class TestListChangeEvent(unittest.TestCase):

    def test_list_change_event_repr(self):
        event = ListChangeEvent(
            object=[],
            index=3,
            removed=[1, 2],
            added=[3, 4],
        )
        actual = repr(event)
        self.assertEqual(
            actual,
            "ListChangeEvent("
            "object=[], index=3, removed=[1, 2], added=[3, 4])"
        )


class TestListEventFactory(unittest.TestCase):
    """ Test event factory compatibility with TraitList.notify """

    def test_trait_list_notification_compat(self):

        events = []

        def notifier(*args, **kwargs):
            event = list_event_factory(*args, **kwargs)
            events.append(event)

        trait_list = TraitList(
            [0, 1, 2],
            notifiers=[notifier],
        )

        # when
        trait_list[1:] = [3, 4]

        # then
        event, = events
        self.assertIsInstance(event, ListChangeEvent)
        self.assertIs(event.object, trait_list)
        self.assertEqual(event.index, 1)
        self.assertEqual(event.removed, [1, 2])
        self.assertEqual(event.added, [3, 4])
