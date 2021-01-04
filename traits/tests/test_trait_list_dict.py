# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Test the persistence behavior of TraitListObjects, TraitDictObjects and
TraitSetObjects.
"""

import copy
import pickle
import unittest

from traits.has_traits import HasTraits, on_trait_change
from traits.trait_types import Dict, List, Set, Str, Int, Instance


class A(HasTraits):
    alist = List(Int, list(range(5)))
    adict = Dict(Str, Int, dict(a=1, b=2))
    aset = Set(Int, set(range(5)))

    events = List()

    @on_trait_change("alist_items,adict_items,aset_items")
    def _receive_events(self, object, name, old, new):
        self.events.append((name, new))


class B(HasTraits):
    dict = Dict(Str, Instance(A))


class TestTraitListDictSetPersistence(unittest.TestCase):
    def test_trait_list_object_persists(self):
        a = A()
        list = pickle.loads(pickle.dumps(a.alist))
        self.assertIsNone(list.object())
        list.append(10)
        self.assertEqual(len(a.events), 0)
        a.alist.append(20)
        self.assertEqual(len(a.events), 1)
        list2 = pickle.loads(pickle.dumps(list))
        self.assertIsNone(list2.object())

    def test_trait_dict_object_persists(self):
        a = A()
        dict = pickle.loads(pickle.dumps(a.adict))
        self.assertIsNone(dict.object())
        dict["key"] = 10
        self.assertEqual(len(a.events), 0)
        a.adict["key"] = 10
        self.assertEqual(len(a.events), 1)
        dict2 = pickle.loads(pickle.dumps(dict))
        self.assertIsNone(dict2.object())

    def test_trait_set_object_persists(self):
        a = A()
        set = pickle.loads(pickle.dumps(a.aset))
        self.assertIsNone(set.object())
        set.add(10)
        self.assertEqual(len(a.events), 0)
        a.aset.add(20)
        self.assertEqual(len(a.events), 1)
        set2 = pickle.loads(pickle.dumps(set))
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
        pickle.loads(pickle.dumps(a))
        b = B(dict=dict(a=a))
        pickle.loads(pickle.dumps(b))

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

    def test_trait_list_default_kind(self):
        a = A()
        list_trait = a.traits()["alist"]
        self.assertEqual(list_trait.default_kind, "list")

    def test_trait_dict_default_kind(self):
        a = A()
        dict_trait = a.traits()["adict"]
        self.assertEqual(dict_trait.default_kind, "dict")

    def test_trait_set_default_kind(self):
        a = A()
        set_trait = a.traits()["aset"]
        self.assertEqual(set_trait.default_kind, "set")

    def test_trait_list_default(self):
        a = A()
        list_trait = a.traits()["alist"]
        self.assertEqual(list_trait.default, [0, 1, 2, 3, 4])

        # The default property should have returned a copy, so
        # modifying it doesn't change the actual default.
        list_trait.default.append(5)
        self.assertEqual(a.alist, [0, 1, 2, 3, 4])

    def test_trait_dict_default(self):
        a = A()
        dict_trait = a.traits()["adict"]
        self.assertEqual(dict_trait.default, {"a": 1, "b": 2})

        # The default property should have returned a copy, so
        # modifying it doesn't change the actual default.
        dict_trait.default.pop("a")
        self.assertEqual(a.adict, {"a": 1, "b": 2})

    def test_trait_set_default(self):
        a = A()
        set_trait = a.traits()["aset"]
        self.assertEqual(set_trait.default, {0, 1, 2, 3, 4})

        # The default property should have returned a copy, so
        # modifying it doesn't change the actual default.
        set_trait.default.remove(2)
        self.assertEqual(a.aset, {0, 1, 2, 3, 4})
