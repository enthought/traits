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

from traits.api import (
    HasTraits,
    Any,
    Bool,
    Delegate,
    Event,
    Instance,
    Property,
    Str,
)


class Foo(HasTraits):

    a = Any
    b = Bool
    s = Str
    i = Instance(HasTraits)
    e = Event
    d = Delegate("i")

    p = Property

    def _get_p(self):
        return self._p

    def _set_p(self, p):
        self._p = p

    # Read Only Property
    p_ro = Property

    def _get_p_ro(self):
        return id(self)

    # Write-only property
    p_wo = Property

    def _set_p_wo(self, p_wo):
        self._p_wo = p_wo


class TestCopyableTraitNames(unittest.TestCase):
    """ Validate that copyable_trait_names returns the appropriate result.
    """

    def setUp(self):
        foo = Foo()
        self.names = foo.copyable_trait_names()

    def test_events_not_copyable(self):
        self.assertNotIn("e", self.names)

    def test_read_only_property_not_copyable(self):
        self.assertNotIn("p_ro", self.names)

    def test_write_only_property_not_copyable(self):
        self.assertNotIn("p_wo", self.names)

    def test_any_copyable(self):
        self.assertIn("a", self.names)

    def test_bool_copyable(self):
        self.assertIn("b", self.names)

    def test_str_copyable(self):
        self.assertIn("s", self.names)

    def test_instance_copyable(self):
        self.assertIn("i", self.names)

    def test_delegate_copyable(self):
        self.assertIn("d", self.names)

    def test_property_copyable(self):
        self.assertIn("p", self.names)


class TestCopyableTraitNameQueries(unittest.TestCase):
    def setUp(self):
        self.foo = Foo()

    def test_type_query(self):
        names = self.foo.copyable_trait_names(**{"type": "trait"})

        self.assertEqual(["a", "b", "i", "s"], sorted(names))

        names = self.foo.copyable_trait_names(
            **{"type": lambda t: t in ("trait", "property")}
        )

        self.assertEqual(["a", "b", "i", "p", "s"], sorted(names))

    def test_property_query(self):
        names = self.foo.copyable_trait_names(
            **{"property_fields": lambda p: p and p[1].__name__ == "_set_p"}
        )

        self.assertEqual(["p"], names)

    def test_unmodified_query(self):
        names = self.foo.copyable_trait_names(
            **{"is_trait_type": lambda f: f(Str)}
        )

        self.assertEqual(["s"], names)

    def test_queries_not_combined(self):
        """ Verify that metadata is not merged with metadata to find the
            copyable traits.
        """

        eval_true = lambda x: True

        names = self.foo.copyable_trait_names(
            property=eval_true, type=eval_true, transient=eval_true
        )

        self.assertEqual(
            [
                "a",
                "b",
                "d",
                "e",
                "i",
                "p",
                "p_ro",
                "p_wo",
                "s",
                "trait_added",
                "trait_modified",
            ],
            sorted(names),
        )
