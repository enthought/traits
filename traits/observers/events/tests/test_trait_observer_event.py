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
from traits.observers.events._trait_observer_event import (
    trait_event_factory,
    TraitObserverEvent,
)


def get_notifier(event_factory):
    """ Dummy notifier for collecting events created by the event factory so
    that the events can then be inspected in tests.

    Parameters
    ----------
    event_factory : callable
        The event factory to be tested.

    Returns
    -------
    events : list
        A list for collecting events. New events will be appended to it.
    notifier : callable
        Notifier to be given to an observable so that it is called when
        a change occurs.
    """
    events = []

    def notifier(*args, **kwargs):
        event = event_factory(*args, **kwargs)
        events.append(event)

    return events, notifier


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

        events, notifier = get_notifier(trait_event_factory)

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
