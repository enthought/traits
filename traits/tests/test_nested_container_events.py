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

from traits.api import (HasTraits, List, Dict, Set, Str, Union, TraitDictEvent,
                        TraitSetObject, TraitListEvent, TraitListObject)


class TestClass(HasTraits):
    list_of_sets = List(Set())

    list_of_lists = List(List())

    list_of_list_of_list = List(List(List()))

    dict_str_list_or_set = Dict(Str(), Union(Set(), List()))

    events_list = List()

    def _list_of_sets_items_changed(self, event):
        self.events_list.append(event)

    def _list_of_lists_items_changed(self, event):
        self.events_list.append(event)

    def _dict_str_list_or_set_items_changed(self, event):
        self.events_list.append(event)

    def _list_of_list_of_list_changed(self, event):
        self.events_list.append(event)


class TestNestedContainers(unittest.TestCase):
    def test_list_of_sets(self):
        obj = TestClass()
        obj.list_of_sets = [set([1, 2, 3]), set(['a', 'b', 'c'])]

        # Add an item to the internal set
        obj.list_of_sets[0].add(4)
        # Ensure that no notification is fired
        self.assertListEqual(obj.events_list, [])

        # Add an item to the root list container
        obj.list_of_sets.append(set(['r', 'g']))

        # Ensure that only a TraitListEvent is fired
        event, = obj.events_list
        self.assertIsInstance(event, TraitListEvent)
        self.assertEqual(1, len(event.added))
        self.assertIsInstance(event.added[0], TraitSetObject)

    def test_list_of_lists(self):
        obj = TestClass()
        obj.list_of_lists = [[1, 2, 3], ['a', 'b', 'c']]

        # Ensure that no notification is fired
        self.assertListEqual(obj.events_list, [])

        # Add an item to the internal list
        obj.list_of_lists[0].append(4)

        # Ensure that no notification is fired
        self.assertListEqual(obj.events_list, [])

        # Add an item to the outer list
        obj.list_of_lists.append(['apples', 'oranges'])

        # Ensure that a TraitListEvent is fired
        event, = obj.events_list
        self.assertIsInstance(event, TraitListEvent)
        self.assertEqual(1, len(event.added))
        self.assertIsInstance(event.added[0], TraitListObject)

    @unittest.skip("TODO: Why isn't this working?")
    def test_list_of_list_of_list(self):
        obj = TestClass()

        obj.list_of_list_of_list = [[[1, 2]]]

        # Add an item to the innermost list
        obj.list_of_list_of_list[0][0].append(2)

        # Ensure that no notification is fired
        self.assertListEqual(obj.events_list, [])

    def test_dict_str_to_list(self):
        obj = TestClass()
        obj.dict_str_list_or_set = {"nums": [1, 2, 3, 4],
                                    "alpha": {'a', 'b', 'c'}}

        self.assertListEqual(obj.events_list, [])

        # Add an item to the internal value
        obj.dict_str_list_or_set['nums'].append(4)

        # Ensure that no notification is fired
        self.assertListEqual(obj.events_list, [])

        # Add a key
        obj.dict_str_list_or_set['fruit'] = {'apples', 'mangoes'}

        # Ensure event is fired
        event, = obj.events_list
        self.assertIsInstance(event, TraitDictEvent)
        self.assertEqual(1, len(event.added))
        for k, v in event.added.items():
            self.assertIsInstance(k, str)
            self.assertIsInstance(v, TraitSetObject)
