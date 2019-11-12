##############################################################################
# Copyright 2014 Enthought, Inc.
##############################################################################

""" Test the persistence behavior of TraitListObjects, TraitDictObjects and
TraitSetObjects.
"""

from __future__ import absolute_import

import copy
import unittest

import six.moves as sm

from traits.has_traits import HasTraits, on_trait_change
from traits.trait_types import Dict, List, Set, Str, Int, Instance


class A(HasTraits):
    alist = List(Int, list(sm.range(5)))
    adict = Dict(Str, Int, dict(a=1, b=2))
    aset = Set(Int, list(sm.range(5)))

    events = List()

    @on_trait_change("alist_items,adict_items,aset_items")
    def _receive_events(self, object, name, old, new):
        self.events.append((name, new))


class B(HasTraits):
    dict = Dict(Str, Instance(A))


class TestTraitListDictSetPersistence(unittest.TestCase):
    def test_trait_list_object_persists(self):
        a = A()
        list = sm.cPickle.loads(sm.cPickle.dumps(a.alist))
        self.assertIsNone(list.object())
        list.append(10)
        self.assertEqual(len(a.events), 0)
        a.alist.append(20)
        self.assertEqual(len(a.events), 1)
        list2 = sm.cPickle.loads(sm.cPickle.dumps(list))
        self.assertIsNone(list2.object())

    def test_trait_dict_object_persists(self):
        a = A()
        dict = sm.cPickle.loads(sm.cPickle.dumps(a.adict))
        self.assertIsNone(dict.object())
        dict["key"] = 10
        self.assertEqual(len(a.events), 0)
        a.adict["key"] = 10
        self.assertEqual(len(a.events), 1)
        dict2 = sm.cPickle.loads(sm.cPickle.dumps(dict))
        self.assertIsNone(dict2.object())

    def test_trait_set_object_persists(self):
        a = A()
        set = sm.cPickle.loads(sm.cPickle.dumps(a.aset))
        self.assertIsNone(set.object())
        set.add(10)
        self.assertEqual(len(a.events), 0)
        a.aset.add(20)
        self.assertEqual(len(a.events), 1)
        set2 = sm.cPickle.loads(sm.cPickle.dumps(set))
        self.assertIsNone(set2.object())

    def test_trait_list_object_copies(self):
        a = A()
        list = copy.deepcopy(a.alist)
        self.assertIsNone(list.object())
        list.append(10)
        self.assertEqual(len(a.events), 0)
        a.alist.append(20)
        self.assertEqual(len(a.events), 1)
        list2 = copy.deepcopy(list)
        list2.append(30)
        self.assertIsNone(list2.object())

    def test_trait_dict_object_copies(self):
        a = A()
        dict = copy.deepcopy(a.adict)
        self.assertIsNone(dict.object())
        dict["key"] = 10
        self.assertEqual(len(a.events), 0)
        a.adict["key"] = 10
        self.assertEqual(len(a.events), 1)
        dict2 = copy.deepcopy(dict)
        dict2["key2"] = 20
        self.assertIsNone(dict2.object())

    def test_trait_set_object_copies(self):
        a = A()
        set1 = copy.deepcopy(a.aset)
        self.assertIsNone(set1.object())
        set1.add(10)
        self.assertEqual(len(a.events), 0)
        a.aset.add(20)
        self.assertEqual(len(a.events), 1)
        set2 = copy.deepcopy(set1)
        set2.add(30)
        self.assertIsNone(set2.object())
        set3 = a.aset.copy()
        self.assertIs(type(set3), set)
        # Should not raise an AttributeError:
        set3.remove(20)

    def test_pickle_whole(self):
        a = A()
        sm.cPickle.loads(sm.cPickle.dumps(a))
        b = B(dict=dict(a=a))
        sm.cPickle.loads(sm.cPickle.dumps(b))

    def test_trait_set_object_operations(self):
        # Regression test for update methods not coercing in the same way as
        # standard set objects (github issue #288)
        a = A()
        a.aset.update({10: "a"})
        self.assertEqual(a.aset, set([0, 1, 2, 3, 4, 10]))
        a.aset.intersection_update({3: "b", 4: "b", 10: "a", 11: "b"})
        self.assertEqual(a.aset, set([3, 4, 10]))
        a.aset.difference_update({10: "a", 11: "b"})
        self.assertEqual(a.aset, set([3, 4]))
        a.aset.symmetric_difference_update({10: "a", 4: "b"})
        self.assertEqual(a.aset, set([3, 10]))

    def test_trait_set_object_inplace(self):
        a = A()
        a.aset |= set([10])
        self.assertEqual(a.aset, set([0, 1, 2, 3, 4, 10]))
        a.aset &= set([3, 4, 10, 11])
        self.assertEqual(a.aset, set([3, 4, 10]))
        a.aset -= set([10, 11])
        self.assertEqual(a.aset, set([3, 4]))
        a.aset ^= set([10, 4])
        self.assertEqual(a.aset, set([3, 10]))
