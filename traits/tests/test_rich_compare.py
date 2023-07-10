# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest
import warnings

from traits.api import (
    Any, cached_property, ComparisonMode, HasTraits, Property, Str,
)


class IdentityCompare(HasTraits):
    bar = Any(comparison_mode=ComparisonMode.identity)


class RichCompare(HasTraits):
    bar = Any(comparison_mode=ComparisonMode.equality)


class RichCompareTests:
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

    def test_id_first_assignment(self):
        ic = IdentityCompare()
        ic.on_trait_change(self.bar_changed, "bar")

        self.reset_change_tracker()

        default_value = ic.bar
        ic.bar = self.a
        self.check_tracker(ic, "bar", default_value, self.a, 1)

    def test_rich_first_assignment(self):
        rich = RichCompare()
        rich.on_trait_change(self.bar_changed, "bar")

        self.reset_change_tracker()

        default_value = rich.bar
        rich.bar = self.a
        self.check_tracker(rich, "bar", default_value, self.a, 1)

    def test_id_same_object(self):
        ic = IdentityCompare()
        ic.on_trait_change(self.bar_changed, "bar")

        self.reset_change_tracker()

        default_value = ic.bar
        ic.bar = self.a
        self.check_tracker(ic, "bar", default_value, self.a, 1)

        ic.bar = self.a
        self.check_tracker(ic, "bar", default_value, self.a, 1)

    def test_rich_same_object(self):
        rich = RichCompare()
        rich.on_trait_change(self.bar_changed, "bar")

        self.reset_change_tracker()

        default_value = rich.bar
        rich.bar = self.a
        self.check_tracker(rich, "bar", default_value, self.a, 1)

        rich.bar = self.a
        self.check_tracker(rich, "bar", default_value, self.a, 1)

    def test_id_different_object(self):
        ic = IdentityCompare()
        ic.on_trait_change(self.bar_changed, "bar")

        self.reset_change_tracker()

        default_value = ic.bar
        ic.bar = self.a
        self.check_tracker(ic, "bar", default_value, self.a, 1)

        ic.bar = self.different_from_a
        self.check_tracker(ic, "bar", self.a, self.different_from_a, 2)

    def test_rich_different_object(self):
        rich = RichCompare()
        rich.on_trait_change(self.bar_changed, "bar")

        self.reset_change_tracker()

        default_value = rich.bar
        rich.bar = self.a
        self.check_tracker(rich, "bar", default_value, self.a, 1)

        rich.bar = self.different_from_a
        self.check_tracker(rich, "bar", self.a, self.different_from_a, 2)

    def test_id_different_object_same_as(self):
        ic = IdentityCompare()
        ic.on_trait_change(self.bar_changed, "bar")

        self.reset_change_tracker()

        default_value = ic.bar
        ic.bar = self.a
        self.check_tracker(ic, "bar", default_value, self.a, 1)

        ic.bar = self.same_as_a
        self.check_tracker(ic, "bar", self.a, self.same_as_a, 2)

    def test_rich_different_object_same_as(self):
        rich = RichCompare()
        rich.on_trait_change(self.bar_changed, "bar")

        self.reset_change_tracker()

        default_value = rich.bar
        rich.bar = self.a
        self.check_tracker(rich, "bar", default_value, self.a, 1)

        # Values of a and same_as_a are the same and should therefore not
        # be considered a change.
        rich.bar = self.same_as_a
        self.check_tracker(rich, "bar", default_value, self.a, 1)


class Foo(HasTraits):
    name = Str

    def __ne__(self, other):
        # Traits uses != to do the rich compare.  The default implementation
        # of __ne__ is to compare the object identities.
        return self.name != other.name

    def __eq__(self, other):
        # Not required, but a good idea to make __eq__ and __ne__ compatible
        return self.name == other.name


class RichCompareHasTraitsTestCase(unittest.TestCase, RichCompareTests):
    def setUp(self):
        self.a = Foo(name="a")
        self.same_as_a = Foo(name="a")
        self.different_from_a = Foo(name="not a")

    def test_assumptions(self):
        self.assertIsNot(self.a, self.same_as_a)
        self.assertIsNot(self.a, self.different_from_a)

        self.assertEqual(self.a.name, self.same_as_a.name)
        self.assertNotEqual(self.a.name, self.different_from_a.name)


class OldRichCompareTestCase(unittest.TestCase):
    def test_rich_compare_false(self):
        with warnings.catch_warnings(record=True) as warn_msgs:
            warnings.simplefilter("always", DeprecationWarning)

            class OldRichCompare(HasTraits):
                bar = Any(rich_compare=False)

        # Check for a DeprecationWarning.
        self.assertEqual(len(warn_msgs), 1)
        warn_msg = warn_msgs[0]
        self.assertIs(warn_msg.category, DeprecationWarning)
        self.assertIn(
            "'rich_compare' metadata has been deprecated",
            str(warn_msg.message)
        )
        _, _, this_module = __name__.rpartition(".")
        self.assertIn(this_module, warn_msg.filename)

        # Behaviour matches comparison_mode=ComparisonMode.identity.
        old_compare = OldRichCompare()
        events = []
        old_compare.on_trait_change(lambda: events.append(None), "bar")

        some_list = [1, 2, 3]

        self.assertEqual(len(events), 0)
        old_compare.bar = some_list
        self.assertEqual(len(events), 1)
        old_compare.bar = some_list
        self.assertEqual(len(events), 1)
        old_compare.bar = [1, 2, 3]
        self.assertEqual(len(events), 2)
        old_compare.bar = [4, 5, 6]
        self.assertEqual(len(events), 3)

    def test_rich_compare_true(self):
        with warnings.catch_warnings(record=True) as warn_msgs:
            warnings.simplefilter("always", DeprecationWarning)

            class OldRichCompare(HasTraits):
                bar = Any(rich_compare=True)

        # Check for a DeprecationWarning.
        self.assertEqual(len(warn_msgs), 1)
        warn_msg = warn_msgs[0]
        self.assertIs(warn_msg.category, DeprecationWarning)
        self.assertIn(
            "'rich_compare' metadata has been deprecated",
            str(warn_msg.message)
        )
        _, _, this_module = __name__.rpartition(".")
        self.assertIn(this_module, warn_msg.filename)

        # Behaviour matches comparison_mode=ComparisonMode.identity.
        old_compare = OldRichCompare()
        events = []
        old_compare.on_trait_change(lambda: events.append(None), "bar")

        some_list = [1, 2, 3]

        self.assertEqual(len(events), 0)
        old_compare.bar = some_list
        self.assertEqual(len(events), 1)
        old_compare.bar = some_list
        self.assertEqual(len(events), 1)
        old_compare.bar = [1, 2, 3]
        self.assertEqual(len(events), 1)
        old_compare.bar = [4, 5, 6]
        self.assertEqual(len(events), 2)

    def test_rich_compare_with_cached_property(self):
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
