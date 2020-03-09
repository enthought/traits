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

from traits.api import (
    HasTraits,
    Int,
    Str,
    TraitError,
)


class Foo(HasTraits):
    num = Int
    bar = Str


class Bar(HasTraits):
    # Default is visible.
    PubT1 = Str
    # Change to invisible.
    PubT2 = Str(visible=False)
    # New behaviour makes private traits invisible.
    PrivT1 = Str(private=True)
    # Force visibility of a private trait.
    PrivT2 = Str(private=True, visible=True)


class FooBar(HasTraits):
    num = Int
    baz = "non-trait class attribute"


class GetTraitTestCase(unittest.TestCase):
    def test_trait_set_bad(self):
        b = Foo(num=23)
        # This should fail before and after #234.
        with self.assertRaises(TraitError):
            b.num = "first"
        self.assertEqual(b.num, 23)

    def test_trait_set_replaced(self):
        b = Foo()
        # Overriding the trait with a new type should work.
        b.add_trait("num", Str())
        b.num = "first"
        self.assertEqual(b.num, "first")

    def test_trait_set_replaced_and_check(self):
        b = Foo()
        b.add_trait("num", Str())
        b.num = "first"
        self.assertEqual(b.num, "first")

        # Check that the "traits" call picks up the new instance trait. (See
        # #234.)
        self.assertEqual(b.trait("num"), b.traits()["num"])

    def test_trait_names_returned_by_visible_traits(self):
        b = Bar()
        self.assertEqual(
            sorted(b.visible_traits()), sorted(["PubT1", "PrivT2"])
        )

    def test_dir(self):
        b = FooBar()
        names = dir(b)
        self.assertIn("baz", names)
        self.assertIn("num", names)
        self.assertIn("edit_traits", names)

        # Issue 925: _notifiers not shown in dir()
        self.assertIn("_notifiers", names)

        # Ensure no duplicates
        self.assertEqual(len(set(names)), len(names))
