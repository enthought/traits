# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import sys
import unittest.mock
import warnings
import weakref

from traits.api import HasTraits
from traits.constants import (
    ComparisonMode, DefaultValue, TraitKind, MAXIMUM_DEFAULT_VALUE_TYPE
)
from traits.ctrait import CTrait
from traits.trait_errors import TraitError
from traits.trait_types import Any, Int, List


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

        trait.property_fields = (getter, setter, validator)

        self.assertTrue(trait.is_property)

        with self.assertRaises(AttributeError):
            trait.is_property = False

    def test_get_set_property(self):
        trait = CTrait(TraitKind.trait)

        # Get the property, ensure None
        self.assertIsNone(trait.property_fields)

        def value_get(self):
            return self.__dict__.get("_value", 0)

        def value_set(self, value):
            old_value = self.__dict__.get("_value", 0)
            if value != old_value:
                self._value = value
                self.trait_property_changed("value", old_value, value)

        # Set the callables
        trait.property_fields = (value_get, value_set, None)

        fget, fset, validate = trait.property_fields

        self.assertIs(fget, value_get)
        self.assertIs(fset, value_set)
        self.assertIsNone(validate)

        # Ensure that _get_property does not accept arguments.
        with self.assertRaises(TypeError):
            trait._get_property(fget)

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

    def test_assign_post_setattr_none(self):
        old_value = "old_value"
        new_value = "new_value"

        def post_setattr_func(obj, name, value):
            obj.output_variable = value

        trait = CTrait(TraitKind.trait)

        class TestClass(HasTraits):
            atr = trait

        trait.post_setattr = post_setattr_func
        self.assertIsNotNone(trait.post_setattr)

        obj = TestClass()
        obj.atr = old_value
        self.assertEqual(old_value, obj.output_variable)

        trait.post_setattr = None
        self.assertIsNone(trait.post_setattr)
        obj.atr = new_value
        self.assertEqual(old_value, obj.output_variable)

        trait.post_setattr = post_setattr_func
        obj.atr = old_value
        self.assertEqual(old_value, obj.output_variable)

        with self.assertRaises(ValueError):
            trait.post_setattr = "Invalid"

    def test_unsafe_set_value(self):
        # Regression test for enthought/traits#832. The test below causes
        # a segfault (on at least some systems) before the fix.

        def get_handler_refcount():
            sys.getrefcount(tr.handler)

        # Anything that we can create a weakref to works here.
        weakrefable_object = {1, 2, 3}

        tr = CTrait(0)
        tr.handler = Any(weakrefable_object)
        finalizer = weakref.finalize(weakrefable_object, get_handler_refcount)
        del weakrefable_object

        # Reassigning the handler should trigger the finaliser.
        self.assertTrue(finalizer.alive)
        tr.handler = None
        self.assertFalse(finalizer.alive)
        self.assertIsNone(tr.handler)

    def test_invalid_initialization(self):
        with self.assertRaises(TraitError):
            CTrait(max(TraitKind) + 1)

    def test_initialization_with_keywords_fails(self):
        with self.assertRaises(TraitError):
            CTrait(kind=0)

    def test_default_initialization(self):
        ctrait = CTrait()

        validate = unittest.mock.MagicMock(return_value="baz")
        ctrait.set_validate(validate)

        class Foo(HasTraits):
            bar = ctrait

            bar_changed = List

            def _bar_changed(self, new):
                self.bar_changed.append(new)

        foo = Foo()

        self.assertEqual(len(foo.bar_changed), 0)

        foo.bar = 1

        validate.assert_called_once_with(foo, "bar", 1)
        self.assertEqual(foo.bar, "baz")
        self.assertEqual(len(foo.bar_changed), 1)
        self.assertEqual(foo.bar_changed[0], "baz")

    def test_failed_attribute_access(self):
        ctrait = CTrait(0)
        self.assertIsNone(ctrait.non_existent)

    def test_exception_from_attribute_access(self):
        # Regression test for enthought/traits#946.

        # Danger: we're (temporarily) mutating global state here! Check that
        # we're not touching an attribute that actually exists.
        self.assertFalse(hasattr(CTrait, "badattr_test"))

        CTrait.badattr_test = property(lambda self: 1 / 0)
        try:
            ctrait = CTrait(0)
            with self.assertRaises(ZeroDivisionError):
                ctrait.badattr_test
        finally:
            del CTrait.badattr_test


class TestCTraitNotifiers(unittest.TestCase):
    """ Test calling trait notifiers and object notifiers. """

    def test_notifiers_empty(self):

        class Foo(HasTraits):
            x = Int()

        foo = Foo(x=1)
        x_ctrait = foo.trait("x")

        self.assertEqual(x_ctrait._notifiers(True), [])

    def test_notifiers_on_trait(self):

        class Foo(HasTraits):
            x = Int()

            def _x_changed(self):
                pass

        foo = Foo(x=1)
        x_ctrait = foo.trait("x")

        tnotifiers = x_ctrait._notifiers(True)
        self.assertEqual(len(tnotifiers), 1)
        notifier, = tnotifiers
        self.assertEqual(notifier.handler, Foo._x_changed)
