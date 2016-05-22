#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This Software is provided without warranty under the terms of the
#  BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The
#  license
#  is also available online at http://www.enthought.com/licenses/BSD.txt

from __future__ import absolute_import

from traits.testing.unittest_tools import unittest

from ..api import HasTraits, Str, Instance, Any


class TestEventOrder(unittest.TestCase):
    """ Tests that demonstrate that trait events are delivered in LIFO
    order rather than FIFO order.

    Baz receives the "effect" event before it receives the "cause" event.
    """
    def setUp(self):
        foo = Foo(cause='ORIGINAL')
        bar = Bar(foo=foo, test=self)
        baz = Baz(bar=bar, test=self)

        self.events_delivered = []
        foo.cause = 'CHANGE'
        return

    def test_lifo_order(self):
        lifo = ['Bar._caused_changed',
                'Baz._effect_changed',
                'Baz._caused_changed']

        self.assertEqual(self.events_delivered, lifo)
        return

    def test_not_fifo_order(self):
        fifo = ['Bar._caused_changed',
                'Baz._caused_changed',
                'Baz._effect_changed']

        self.assertNotEqual(self.events_delivered, fifo)
        return


class Foo(HasTraits):
    cause = Str


class Bar(HasTraits):
    foo = Instance(Foo)
    effect = Str
    test = Any

    def _foo_changed(self, obj, old, new):
        if old is not None and old is not new:
            old.on_trait_change(self._cause_changed, name='cause', remove=True)

        if new is not None:
            new.on_trait_change(self._cause_changed, name='cause')

        return

    def _cause_changed(self, obj, name, old, new):
        self.test.events_delivered.append('Bar._caused_changed')
        self.effect = new.lower()
        return


class Baz(HasTraits):
    bar = Instance(Bar)
    test = Any

    def _bar_changed(self, obj, old, new):
        if old is not None and old is not new:
            old.on_trait_change(self._effect_changed, name='effect',
                                remove=True)
            old.foo.on_trait_change(self._cause_changed, name='cause',
                                    remove=True)

        if new is not None:
            new.foo.on_trait_change(self._cause_changed, name='cause')
            new.on_trait_change(self._effect_changed, name='effect')

        return

    def _cause_changed(self, obj, name, old, new):
        self.test.events_delivered.append('Baz._caused_changed')
        return

    def _effect_changed(self, obj, name, old, new):
        self.test.events_delivered.append('Baz._effect_changed')
        return

### EOF #######################################################################
