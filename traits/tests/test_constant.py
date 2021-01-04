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

from traits.api import Constant, HasTraits, TraitError


class TestConstantTrait(unittest.TestCase):

    def test_initial_value(self):
        class TestClass(HasTraits):
            c_atr = Constant(5)

        self.assertEqual(TestClass().c_atr, 5)

    def test_mutable_initial_value(self):
        class TestClass(HasTraits):
            c_atr_1 = Constant([1, 2, 3, 4, 5])
            c_atr_2 = Constant({"a": 1, "b": 2})

        obj = TestClass()

        self.assertEqual(obj.c_atr_1, [1, 2, 3, 4, 5])
        self.assertEqual(obj.c_atr_2, {"a": 1, "b": 2})

    def test_assign_fails(self):
        class TestClass(HasTraits):
            c_atr = Constant(5)

        with self.assertRaises(TraitError):
            TestClass(c_atr=5)
        with self.assertRaises(TraitError):
            del TestClass().c_atr

    def test_mutate_succeeds(self):
        class TestClass(HasTraits):
            c_atr_1 = Constant([1, 2, 3, 4, 5])
            c_atr_2 = Constant({"a": 1, "b": 2})

        obj = TestClass()
        obj.c_atr_1.append(6)
        obj.c_atr_2["c"] = 3

        self.assertEqual(obj.c_atr_1, [1, 2, 3, 4, 5, 6])
        self.assertEqual(obj.c_atr_2, {"a": 1, "b": 2, "c": 3})
