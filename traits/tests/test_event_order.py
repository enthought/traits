# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.api import HasTraits, Str, Instance, Any


class TestEventOrder(unittest.TestCase):
    """ Tests that demonstrate that trait events are delivered in LIFO
    order rather than FIFO order.

    Baz receives the "effect" event before it receives the "cause" event.
    """

    def test_lifo_order(self):
        foo = Foo(cause="ORIGINAL")
        bar = Bar(foo=foo, test=self)
        # flake8 complains about unused "baz", but we need to keep it
        # alive for listeners to fire.
        baz = Baz(bar=bar, test=self)  # noqa: F841

        self.events_delivered = []
        foo.cause = "CHANGE"

        lifo = [
            "Bar._caused_changed",
            "Baz._effect_changed",
            "Baz._caused_changed",
        ]

        self.assertEqual(self.events_delivered, lifo)


class Foo(HasTraits):
    cause = Str


class Bar(HasTraits):
    foo = Instance(Foo)
    effect = Str
    test = Any

    def _foo_changed(self, obj, old, new):
        if old is not None and old is not new:
            old.on_trait_change(self._cause_changed, name="cause", remove=True)

        if new is not None:
            new.on_trait_change(self._cause_changed, name="cause")

    def _cause_changed(self, obj, name, old, new):
        self.test.events_delivered.append("Bar._caused_changed")
        self.effect = new.lower()


class Baz(HasTraits):
    bar = Instance(Bar)
    test = Any

    def _bar_changed(self, obj, old, new):
        if old is not None and old is not new:
            old.on_trait_change(
                self._effect_changed, name="effect", remove=True
            )
            old.foo.on_trait_change(
                self._cause_changed, name="cause", remove=True
            )

        if new is not None:
            new.foo.on_trait_change(self._cause_changed, name="cause")
            new.on_trait_change(self._effect_changed, name="effect")

    def _cause_changed(self, obj, name, old, new):
        self.test.events_delivered.append("Baz._caused_changed")

    def _effect_changed(self, obj, name, old, new):
        self.test.events_delivered.append("Baz._effect_changed")
