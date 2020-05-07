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

from traits.has_traits import HasTraits
from traits.trait_types import Int
from traits.observers._trait_observer_event import (
    trait_event_factory,
    TraitObserverEvent,
)


class TestTraitObserverEvent(unittest.TestCase):
    """ Test initialization and repr of TraitObserverEvent. """

    def test_trait_observer_event_repr(self):
        event = TraitObserverEvent(
            object=None,
            name="name",
            old=1,
            new=2,
        )
        actual = repr(event)
        self.assertEqual(
            actual,
            "<TraitObserverEvent(object=None, name='name', old=1, new=2)>"
        )


class TestTraitEventFactory(unittest.TestCase):
    """ Test event factory compatibility with CTrait."""

    def test_trait_change_notification_compat(self):

        class Foo(HasTraits):
            number = Int()

        events = []

        def notifier(*args, **kwargs):
            event = trait_event_factory(*args, **kwargs)
            events.append(event)

        foo = Foo(number=0)
        trait = foo.trait("number")

        trait._notifiers(True).append(notifier)

        # when
        foo.number += 1

        # then
        event, = events

        self.assertIs(event.object, foo)
        self.assertEqual(event.name, "number")
        self.assertEqual(event.old, 0)
        self.assertEqual(event.new, 1)
