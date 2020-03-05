# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Tests for the PrefixList handler.
"""

import pickle
import unittest

from traits.api import HasTraits, TraitError, PrefixList


class TestPrefixList(unittest.TestCase):
    def test_assignment(self):
        class A(HasTraits):
            foo = PrefixList("zero", "one", "two", default_value="one")

        a = A()

        a.foo = 'z'
        self.assertEqual(a.foo, "zero")

        with self.assertRaises(TraitError):
            a.foo = ''

    def test_repeated_prefix(self):
        class A(HasTraits):
            foo = PrefixList("abc1", "abc2")
        a = A()

        a.foo = "abc1"
        self.assertEqual(a.foo, "abc1")

        with self.assertRaises(TraitError):
            a.foo = "abc"

    def test_invalid_default(self):
        with self.assertRaises(ValueError):
            class A(HasTraits):
                foo = PrefixList("zero", "one", "two", default_value="uno")

    def test_pickle_roundtrip(self):
        class A(HasTraits):
            foo = PrefixList("zero", "one", "two", default_value="one")

        a = A()
        foo_trait = a.traits()["foo"]
        reconstituted = pickle.loads(pickle.dumps(foo_trait))

        self.assertEqual(
            foo_trait.validate(a, "foo", "ze"),
            "zero",
        )
        with self.assertRaises(TraitError):
            foo_trait.validate(a, "foo", "zero-knowledge")

        self.assertEqual(
            reconstituted.validate(a, "foo", "ze"),
            "zero",
        )
        with self.assertRaises(TraitError):
            reconstituted.validate(a, "foo", "zero-knowledge")
