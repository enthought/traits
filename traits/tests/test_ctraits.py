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
import warnings

from traits.constants import (
    ComparisonMode, DefaultValue, TraitKind, MAXIMUM_DEFAULT_VALUE_TYPE
)
from traits.ctrait import CTrait


def getter():
    """ Trivial getter. """
    return True


def setter(value):
    """ Trivial setter. """
    pass


def validator(value):
    """ Trivial validator. """
    return value


class TestCTrait(unittest.TestCase):
    """ Tests for the CTrait class. """

    def test_initial_default_value(self):
        trait = CTrait(TraitKind.trait)
        self.assertEqual(
            trait.default_value(), (DefaultValue.constant, None),
        )

    def test_set_and_get_default_value(self):
        trait = CTrait(TraitKind.trait)
        trait.set_default_value(DefaultValue.constant, 2.3)
        self.assertEqual(trait.default_value(), (DefaultValue.constant, 2.3))

        trait.set_default_value(DefaultValue.list_copy, [1, 2, 3])
        self.assertEqual(
            trait.default_value(), (DefaultValue.list_copy, [1, 2, 3])
        )

    def test_default_value_for_set_is_deprecated(self):
        trait = CTrait(TraitKind.trait)
        with warnings.catch_warnings(record=True) as warn_msgs:
            warnings.simplefilter("always", DeprecationWarning)
            trait.default_value(DefaultValue.constant, 3.7)

        self.assertEqual(len(warn_msgs), 1)
        warn_msg = warn_msgs[0]
        self.assertIn(
            "default_value method with arguments is deprecated",
            str(warn_msg.message),
        )
        _, _, this_module = __name__.rpartition(".")
        self.assertIn(this_module, warn_msg.filename)

    def test_bad_default_value_type(self):
        trait = CTrait(TraitKind.trait)

        with self.assertRaises(ValueError):
            trait.set_default_value(-1, None)

        with self.assertRaises(ValueError):
            trait.set_default_value(MAXIMUM_DEFAULT_VALUE_TYPE + 1, None)

    def test_is_property(self):
        trait = CTrait(TraitKind.trait)

        self.assertFalse(trait.is_property)

        trait.set_property(getter, setter, validator)

        self.assertTrue(trait.is_property)

        with self.assertRaises(AttributeError):
            trait.is_property = False

    def test_modify_delegate(self):
        trait = CTrait(TraitKind.trait)

        self.assertFalse(trait.modify_delegate)

        trait.modify_delegate = True

        self.assertTrue(trait.modify_delegate)

    def test_setattr_original_value(self):
        trait = CTrait(TraitKind.trait)

        self.assertFalse(trait.setattr_original_value)

        trait.setattr_original_value = True

        self.assertTrue(trait.setattr_original_value)

    def test_post_setattr_original_value(self):
        trait = CTrait(TraitKind.trait)

        self.assertFalse(trait.post_setattr_original_value)

        trait.post_setattr_original_value = True

        self.assertTrue(trait.post_setattr_original_value)

    def test_is_mapped(self):
        trait = CTrait(TraitKind.trait)

        self.assertFalse(trait.is_mapped)

        trait.is_mapped = True

        self.assertTrue(trait.is_mapped)

    def test_default_comparison_mode(self):
        trait = CTrait(TraitKind.trait)

        self.assertIsInstance(trait.comparison_mode, ComparisonMode)
        self.assertEqual(trait.comparison_mode, ComparisonMode.equality)

    def test_invalid_comparison_mode(self):
        trait = CTrait(TraitKind.trait)

        # comparison modes other than {0,1,2}
        # are invalid
        with self.assertRaises(ValueError):
            trait.comparison_mode = -1

        with self.assertRaises(ValueError):
            trait.comparison_mode = 3

    def test_comparison_mode_unchanged_if_invalid(self):
        trait = CTrait(TraitKind.trait)
        default_comparison_mode = trait.comparison_mode

        self.assertNotEqual(default_comparison_mode, ComparisonMode.none)

        trait.comparison_mode = ComparisonMode.none

        with self.assertRaises(ValueError):
            trait.comparison_mode = -1

        self.assertEqual(trait.comparison_mode, ComparisonMode.none)

    def test_comparison_mode_int(self):
        trait = CTrait(TraitKind.trait)

        trait.comparison_mode = 0

        self.assertIsInstance(trait.comparison_mode, ComparisonMode)
        self.assertEqual(trait.comparison_mode, ComparisonMode.none)

        trait.comparison_mode = 1

        self.assertIsInstance(trait.comparison_mode, ComparisonMode)
        self.assertEqual(trait.comparison_mode, ComparisonMode.identity)

        trait.comparison_mode = 2

        self.assertIsInstance(trait.comparison_mode, ComparisonMode)
        self.assertEqual(trait.comparison_mode, ComparisonMode.equality)

    def test_comparison_mode_enum(self):
        trait = CTrait(TraitKind.trait)

        trait.comparison_mode = ComparisonMode.none

        self.assertIsInstance(trait.comparison_mode, ComparisonMode)
        self.assertEqual(trait.comparison_mode, ComparisonMode.none)

        trait.comparison_mode = ComparisonMode.identity

        self.assertIsInstance(trait.comparison_mode, ComparisonMode)
        self.assertEqual(trait.comparison_mode, ComparisonMode.identity)

        trait.comparison_mode = ComparisonMode.equality

        self.assertIsInstance(trait.comparison_mode, ComparisonMode)
        self.assertEqual(trait.comparison_mode, ComparisonMode.equality)

    def test_set_property(self):
        trait = CTrait(TraitKind.trait)

        def __value_get(self):
            return self.__dict__.get("_value", 0)

        def __value_set(self, value):
            old_value = self.__dict__.get("_value", 0)
            if value != old_value:
                self._value = value
                self.trait_property_changed("value", old_value, value)

        trait.set_property(__value_get, __value_set, None)

    def test_set_invalid_property(self):
        trait = CTrait(TraitKind.trait)

        with self.assertRaises(ValueError):
            trait.set_property()

    def test_get_property(self):
        trait = CTrait(TraitKind.trait)

        self.assertIsNone(trait.get_property())
