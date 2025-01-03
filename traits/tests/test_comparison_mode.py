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
    Any,
    cached_property,
    ComparisonMode,
    HasTraits,
    Property,
    Str,
)


class NoneCompare(HasTraits):
    bar = Any(comparison_mode=ComparisonMode.none)


class IdentityCompare(HasTraits):
    bar = Any(comparison_mode=ComparisonMode.identity)


class EqualityCompare(HasTraits):
    bar = Any(comparison_mode=ComparisonMode.equality)


class Foo(HasTraits):
    """
    Class implementing custom equality.
    """

    name = Str

    def __eq__(self, other):
        return self.name == other.name


class TestComparisonMode(unittest.TestCase):
    def setUp(self):
        self.a = Foo(name="a")
        self.same_as_a = Foo(name="a")
        self.different_from_a = Foo(name="not a")

    def bar_changed(self, object, trait, old, new):
        self.changed_object = object
        self.changed_trait = trait
        self.changed_old = old
        self.changed_new = new
        self.changed_count += 1

    def reset_change_tracker(self):
        self.changed_object = None
        self.changed_trait = None
        self.changed_old = None
        self.changed_new = None
        self.changed_count = 0

    def check_tracker(self, object, trait, old, new, count):
        self.assertEqual(count, self.changed_count)
        self.assertIs(object, self.changed_object)
        self.assertEqual(trait, self.changed_trait)
        self.assertIs(old, self.changed_old)
        self.assertIs(new, self.changed_new)

    def test_none_first_assignment(self):
        nc = NoneCompare()
        nc.on_trait_change(self.bar_changed, "bar")

        self.reset_change_tracker()

        default_value = nc.bar
        nc.bar = self.a
        self.check_tracker(nc, "bar", default_value, self.a, 1)

    def test_identity_first_assignment(self):
        ic = IdentityCompare()
        ic.on_trait_change(self.bar_changed, "bar")

        self.reset_change_tracker()

        default_value = ic.bar
        ic.bar = self.a
        self.check_tracker(ic, "bar", default_value, self.a, 1)

    def test_equality_first_assignment(self):
        ec = EqualityCompare()
        ec.on_trait_change(self.bar_changed, "bar")

        self.reset_change_tracker()

        default_value = ec.bar
        ec.bar = self.a
        self.check_tracker(ec, "bar", default_value, self.a, 1)

    def test_none_same_object(self):
        nc = NoneCompare()
        nc.on_trait_change(self.bar_changed, "bar")

        self.reset_change_tracker()

        default_value = nc.bar
        nc.bar = self.a
        self.check_tracker(nc, "bar", default_value, self.a, 1)

        nc.bar = self.a
        self.check_tracker(nc, "bar", self.a, self.a, 2)

    def test_identity_same_object(self):
        ic = IdentityCompare()
        ic.on_trait_change(self.bar_changed, "bar")

        self.reset_change_tracker()

        default_value = ic.bar
        ic.bar = self.a
        self.check_tracker(ic, "bar", default_value, self.a, 1)

        ic.bar = self.a
        self.check_tracker(ic, "bar", default_value, self.a, 1)

    def test_equality_same_object(self):
        ec = EqualityCompare()
        ec.on_trait_change(self.bar_changed, "bar")

        self.reset_change_tracker()

        default_value = ec.bar
        ec.bar = self.a
        self.check_tracker(ec, "bar", default_value, self.a, 1)

        ec.bar = self.a
        self.check_tracker(ec, "bar", default_value, self.a, 1)

    def test_none_different_object(self):
        nc = NoneCompare()
        nc.on_trait_change(self.bar_changed, "bar")

        self.reset_change_tracker()

        default_value = nc.bar
        nc.bar = self.a
        self.check_tracker(nc, "bar", default_value, self.a, 1)

        nc.bar = self.different_from_a
        self.check_tracker(nc, "bar", self.a, self.different_from_a, 2)

    def test_identity_different_object(self):
        ic = IdentityCompare()
        ic.on_trait_change(self.bar_changed, "bar")

        self.reset_change_tracker()

        default_value = ic.bar
        ic.bar = self.a
        self.check_tracker(ic, "bar", default_value, self.a, 1)

        ic.bar = self.different_from_a
        self.check_tracker(ic, "bar", self.a, self.different_from_a, 2)

    def test_equality_different_object(self):
        ec = EqualityCompare()
        ec.on_trait_change(self.bar_changed, "bar")

        self.reset_change_tracker()

        default_value = ec.bar
        ec.bar = self.a
        self.check_tracker(ec, "bar", default_value, self.a, 1)

        ec.bar = self.different_from_a
        self.check_tracker(ec, "bar", self.a, self.different_from_a, 2)

    def test_none_different_object_same_as(self):
        nc = NoneCompare()
        nc.on_trait_change(self.bar_changed, "bar")

        self.reset_change_tracker()

        default_value = nc.bar
        nc.bar = self.a
        self.check_tracker(nc, "bar", default_value, self.a, 1)

        nc.bar = self.same_as_a
        self.check_tracker(nc, "bar", self.a, self.same_as_a, 2)

    def test_identity_different_object_same_as(self):
        ic = IdentityCompare()
        ic.on_trait_change(self.bar_changed, "bar")

        self.reset_change_tracker()

        default_value = ic.bar
        ic.bar = self.a
        self.check_tracker(ic, "bar", default_value, self.a, 1)

        ic.bar = self.same_as_a
        self.check_tracker(ic, "bar", self.a, self.same_as_a, 2)

    def test_equality_different_object_same_as(self):
        ec = EqualityCompare()
        ec.on_trait_change(self.bar_changed, "bar")

        self.reset_change_tracker()

        default_value = ec.bar
        ec.bar = self.a
        self.check_tracker(ec, "bar", default_value, self.a, 1)

        # Values of a and same_as_a are the same and should therefore not
        # be considered a change.
        ec.bar = self.same_as_a
        self.check_tracker(ec, "bar", default_value, self.a, 1)

    def test_comparison_mode_none_with_cached_property(self):
        # Even though the property is cached such that old value equals new
        # value, its change event is tied to the dependent.

        class Model(HasTraits):
            value = Property(depends_on="name")
            name = Str(comparison_mode=ComparisonMode.none)

            @cached_property
            def _get_value(self):
                return self.trait_names

        instance = Model()
        events = []
        instance.on_trait_change(lambda: events.append(None), "value")

        instance.name = "A"

        events.clear()

        # when
        instance.name = "A"

        # then
        self.assertEqual(len(events), 1)
