# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
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

    def test_mutate_affects_all_instances(self):
        # Mutable values are allowed for the 'Constant' trait because it's
        # impractical to do otherwise - many things are mutable but not
        # intended to be mutated, and there's no practical way to test for
        # "not-intended-to-be-mutated". Nevertheless, actually mutating the
        # value for 'Constant' is inadvisable in practice, despite the
        # existence of this test.
        class TestClass(HasTraits):
            c_atr = Constant([1, 2, 3, 4, 5])

        obj1 = TestClass()
        obj2 = TestClass()

        # Mutate obj2; check that obj1 is affected.
        obj2.c_atr.append(6)
        self.assertEqual(obj1.c_atr, [1, 2, 3, 4, 5, 6])

        # Check directly that both refer to the same object.
        self.assertIs(obj1.c_atr, obj2.c_atr)
