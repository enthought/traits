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
Tests for the TraitPrefixList handler.
"""

import pickle
import unittest

from traits.api import HasTraits, TraitError, TraitPrefixList, Trait


class TestTraitPrefixList(unittest.TestCase):
    def test_pickle_roundtrip(self):
        with self.assertWarns(DeprecationWarning):
            class A(HasTraits):
                foo = Trait("one", TraitPrefixList("zero", "one", "two"))

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
