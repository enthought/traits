# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Test cases for TraitListEvent, TraitDictEvent, TraitSetEvent. """

import unittest

from traits.api import (
    HasTraits, List, Dict, Set, on_trait_change,
    TraitListEvent, TraitDictEvent, TraitSetEvent
)


class Foo(HasTraits):

    alist = List([1, 2, 3])
    adict = Dict({'red': 255, 'blue': 0, 'green': 127})
    aset = Set({1, 2, 3})

    @on_trait_change(["alist_items", "adict_items", "aset_items"])
    def _receive_events(self, event):
        self.event = event


class TestTraitEvent(unittest.TestCase):

    foo = Foo()

    def check_repr(self, event, event_str):
        self.assertEqual(event.__repr__(), event_str)
        self.assertEqual(eval(event_str).__repr__(), event_str)

    def test_list_repr(self):
        self.foo.alist[0] = 2
        event = self.foo.event
        event_str = "TraitListEvent(index=0, removed=[1], added=[2])"
        self.check_repr(event, event_str)

    def test_dict_event_repr(self):
        self.foo.adict.update({'blue': 10, 'black': 0})
        event = self.foo.event
        event_str = ("TraitDictEvent(added={'black': 0}, "
                     "changed={'blue': 0}, removed={})")
        self.check_repr(event, event_str)

    def test_set_event_repr(self):
        self.foo.aset.symmetric_difference_update({3, 4})
        event = self.foo.event
        event_str = "TraitSetEvent(removed={3}, added={4})"
        self.check_repr(event, event_str)
