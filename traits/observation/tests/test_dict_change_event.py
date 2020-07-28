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

from traits.observation._dict_change_event import (
    DictChangeEvent,
    dict_event_factory,
)
from traits.trait_dict_object import TraitDict


class TestDictChangeEvent(unittest.TestCase):

    def test_dict_change_event_repr(self):
        event = DictChangeEvent(
            object=dict(),
            added={1: 1},
            removed={"2": 2},
        )
        actual = repr(event)
        self.assertEqual(
            actual,
            "DictChangeEvent(object={}, removed={'2': 2}, added={1: 1})"
        )


class TestDictEventFactory(unittest.TestCase):
    """ Test event factory compatibility with TraitDict.notify """

    def test_trait_dict_notification_compat(self):

        events = []

        def notifier(*args, **kwargs):
            event = dict_event_factory(*args, **kwargs)
            events.append(event)

        trait_dict = TraitDict(
            {"3": 3, "4": 4},
            notifiers=[notifier],
        )

        # when
        del trait_dict["4"]

        # then
        event, = events
        self.assertIs(event.object, trait_dict)
        self.assertEqual(event.removed, {"4": 4})

        # when
        events.clear()
        trait_dict.update({"3": None, "1": 1})

        # then
        event, = events
        self.assertEqual(event.removed, {"3": 3})
        self.assertEqual(event.added, {"3": None, "1": 1})
