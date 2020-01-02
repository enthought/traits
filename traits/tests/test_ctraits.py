# ------------------------------------------------------------------------------
# Copyright (c) 2019, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# ------------------------------------------------------------------------------


import unittest
import warnings

from traits.traits import CTrait
from traits.trait_handlers import (
    CONSTANT_DEFAULT_VALUE,
    LIST_COPY_DEFAULT_VALUE,
    MAXIMUM_DEFAULT_VALUE_TYPE,
)


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
        trait = CTrait(0)
        self.assertEqual(
            trait.default_value(), (CONSTANT_DEFAULT_VALUE, None),
        )

    def test_set_and_get_default_value(self):
        trait = CTrait(0)
        trait.set_default_value(CONSTANT_DEFAULT_VALUE, 2.3)
        self.assertEqual(trait.default_value(), (CONSTANT_DEFAULT_VALUE, 2.3))

        trait.set_default_value(LIST_COPY_DEFAULT_VALUE, [1, 2, 3])
        self.assertEqual(
            trait.default_value(), (LIST_COPY_DEFAULT_VALUE, [1, 2, 3])
        )

    def test_default_value_for_set_is_deprecated(self):
        trait = CTrait(0)
        with warnings.catch_warnings(record=True) as warn_msgs:
            warnings.simplefilter("always", DeprecationWarning)
            trait.default_value(CONSTANT_DEFAULT_VALUE, 3.7)

        self.assertEqual(len(warn_msgs), 1)
        warn_msg = warn_msgs[0]
        self.assertIn(
            "default_value method with arguments is deprecated",
            str(warn_msg.message),
        )
        _, _, this_module = __name__.rpartition(".")
        self.assertIn(this_module, warn_msg.filename)

    def test_bad_default_value_type(self):
        trait = CTrait(0)

        with self.assertRaises(ValueError):
            trait.set_default_value(-1, None)

        with self.assertRaises(ValueError):
            trait.set_default_value(MAXIMUM_DEFAULT_VALUE_TYPE + 1, None)

    def test_property_flag(self):
        trait = CTrait(0)

        self.assertFalse(trait.property_flag)

        trait.property(getter, 0, setter, 1, validator, 1)

        self.assertTrue(trait.property_flag)

        with self.assertRaises(AttributeError):
            trait.property_flag = False

    def test_modify_delegate_flag(self):
        trait = CTrait(0)

        self.assertFalse(trait.modify_delegate_flag)

        trait.modify_delegate_flag = True

        self.assertTrue(trait.modify_delegate_flag)

    def test_object_identity_flag(self):
        trait = CTrait(0)

        self.assertFalse(trait.object_identity_flag)

        trait.comparison_mode(1)

        self.assertTrue(trait.object_identity_flag)

        with self.assertRaises(AttributeError):
            trait.object_identity_flag = False

    def test_setattr_original_value_flag(self):
        trait = CTrait(0)

        self.assertFalse(trait.setattr_original_value_flag)

        trait.setattr_original_value_flag = True

        self.assertTrue(trait.setattr_original_value_flag)

    def test_post_setattr_original_value_flag(self):
        trait = CTrait(0)

        self.assertFalse(trait.post_setattr_original_value_flag)

        trait.post_setattr_original_value_flag = True

        self.assertTrue(trait.post_setattr_original_value_flag)

    def test_is_mapped_flag(self):
        trait = CTrait(0)

        self.assertFalse(trait.is_mapped_flag)

        trait.is_mapped_flag = True

        self.assertTrue(trait.is_mapped_flag)

    def test_no_value_test_flag(self):
        trait = CTrait(0)

        self.assertFalse(trait.no_value_test_flag)

        trait.comparison_mode(0)

        self.assertTrue(trait.no_value_test_flag)

        with self.assertRaises(AttributeError):
            trait.no_value_test_flag = False
