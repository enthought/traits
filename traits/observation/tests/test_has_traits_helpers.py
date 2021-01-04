# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest
from unittest import mock

from traits.api import (
    Any, Bool, ComparisonMode, Dict, HasTraits, List, Instance, Int, Property,
    Set,
)
from traits.observation import _has_traits_helpers as helpers
from traits.observation import expression
from traits.observation.observe import observe


class Bar(HasTraits):

    count = Int()


class Foo(HasTraits):

    list_of_int = List(Int)

    instance = Instance(Bar)

    any_value = Any()

    int_with_default = Int()

    int_with_default_computed = Bool()

    def _int_with_default(self):
        self.int_with_default_computed = True
        return 10

    property_value = Property()

    property_n_calculations = Int()

    def _get_property_value(self):
        self.property_n_calculations += 1
        return 1


class ClassWithInstanceDefault(HasTraits):

    instance_with_default = Instance(Bar, ())


class TestHasTraitsHelpersHasNamedTrait(unittest.TestCase):
    """ Test object_has_named_trait."""

    def test_object_has_named_trait_false_for_trait_list(self):
        foo = Foo()

        # TraitListObject that has `trait` attribute
        self.assertFalse(
            helpers.object_has_named_trait(foo.list_of_int, "bar"),
            "Expected object_has_named_trait to return false for {!r}".format(
                type(foo.list_of_int)
            )
        )

    def test_object_has_named_trait_true_basic(self):
        foo = Foo()
        self.assertTrue(
            helpers.object_has_named_trait(foo, "list_of_int"),
            "The named trait should exist."
        )

    def test_object_has_named_trait_false(self):
        foo = Foo()
        self.assertFalse(
            helpers.object_has_named_trait(foo, "not_existing"),
            "Expected object_has_named_trait to return False for a"
            "nonexisting trait name."
        )

    def test_object_has_named_trait_does_not_trigger_property(self):
        foo = Foo()
        helpers.object_has_named_trait(foo, "property_value")
        self.assertEqual(
            foo.property_n_calculations, 0
        )


class CannotCompare:

    def __eq__(self, other):
        raise TypeError("Cannot be compared for equality.")


class TestHasTraitsHelpersIterObjects(unittest.TestCase):
    """ Test iter_objects."""

    def test_iter_objects_avoid_undefined(self):
        foo = Foo()
        # sanity check
        self.assertNotIn("instance", foo.__dict__)

        actual = list(helpers.iter_objects(foo, "instance"))
        self.assertEqual(actual, [])

    def test_iter_objects_no_sideeffect(self):
        foo = Foo()
        # sanity check
        self.assertNotIn("instance", foo.__dict__)

        list(helpers.iter_objects(foo, "instance"))

        self.assertNotIn("instance", foo.__dict__)

    def test_iter_objects_avoid_none(self):
        foo = Foo()
        foo.instance = None

        actual = list(helpers.iter_objects(foo, "instance"))
        self.assertEqual(actual, [])

    def test_iter_objects_allow_object_cannot_compare_for_equality(self):
        # see enthought/traits#1277
        foo = Foo()
        foo.any_value = CannotCompare()

        actual = list(helpers.iter_objects(foo, "any_value"))
        self.assertEqual(actual, [foo.any_value])

    def test_iter_objects_accepted_values(self):
        foo = Foo(instance=Bar(), list_of_int=[1, 2])
        actual = list(helpers.iter_objects(foo, "instance"))

        self.assertEqual(actual, [foo.instance])

    def test_iter_objects_does_not_evaluate_default(self):
        foo = Foo()
        list(helpers.iter_objects(foo, "int_with_default"))
        self.assertFalse(
            foo.int_with_default_computed,
            "Expect the default not to have been computed."
        )

    def test_iter_objects_does_not_trigger_property(self):
        foo = Foo()
        list(helpers.iter_objects(foo, "property_value"))
        self.assertEqual(foo.property_n_calculations, 0)


class ObjectWithEqualityComparisonMode(HasTraits):
    """ Class for supporting TestHasTraitsHelpersComparisonMode """

    list_values = List(comparison_mode=ComparisonMode.equality)
    dict_values = Dict(comparison_mode=ComparisonMode.equality)
    set_values = Set(comparison_mode=ComparisonMode.equality)
    number = Any(comparison_mode=ComparisonMode.equality)
    calculated = Property(depends_on="number")

    def _get_calculated(self):
        return None


class TestHasTraitsHelpersComparisonMode(unittest.TestCase):
    """ Test the effect of ctrait_prevent_event """

    def test_basic_trait_equality_prevent_change_event(self):
        instance = ObjectWithEqualityComparisonMode()
        instance.number = 1

        handler = mock.Mock()
        observe(
            object=instance,
            expression=expression.trait("number"),
            handler=handler,
        )

        # when
        instance.number = 1.0

        # then
        self.assertEqual(handler.call_count, 0)

        # when
        instance.number = True

        # then
        self.assertEqual(handler.call_count, 0)

        # when
        instance.number = 2.0

        # then
        self.assertEqual(handler.call_count, 1)
        handler.reset_mock()

        # when
        # This instance cannot be compared with 2.0 for equality.
        instance.number = CannotCompare()

        # then
        self.assertEqual(handler.call_count, 1)

    def test_property_equality_no_effect(self):
        instance = ObjectWithEqualityComparisonMode()
        instance.number = 1
        handler = mock.Mock()
        observe(
            object=instance,
            expression=expression.trait("calculated"),
            handler=handler,
        )

        # when
        instance.number = 2

        # then
        self.assertEqual(handler.call_count, 1)

    def test_list_equality_prevent_change_event(self):
        instance = ObjectWithEqualityComparisonMode()
        instance.list_values = [1]
        handler = mock.Mock()

        observe(
            object=instance,
            expression=expression.trait("list_values").list_items(),
            handler=handler,
        )

        # New list, but equals to the previous
        instance.list_values = [1]

        # then
        self.assertEqual(handler.call_count, 0)

        # when
        instance.list_values.append(2)

        # then
        self.assertEqual(handler.call_count, 1)

    def test_set_equality_prevent_change_event(self):
        instance = ObjectWithEqualityComparisonMode()
        instance.set_values = {1}
        handler = mock.Mock()

        observe(
            object=instance,
            expression=expression.trait("set_values").set_items(),
            handler=handler,
        )

        # New set, but equals to the previous
        instance.set_values = {1}

        # then
        self.assertEqual(handler.call_count, 0)

        # when
        instance.set_values.add(2)

        # then
        self.assertEqual(handler.call_count, 1)

    def test_dict_equality_prevent_change_event(self):
        instance = ObjectWithEqualityComparisonMode()
        instance.dict_values = {"1": 1}
        handler = mock.Mock()

        observe(
            object=instance,
            expression=expression.trait("dict_values").dict_items(),
            handler=handler,
        )

        # New dict, but equals to the previous
        instance.dict_values = {"1": 1}

        # then
        self.assertEqual(handler.call_count, 0)

        # when
        instance.dict_values["2"] = 2

        # then
        self.assertEqual(handler.call_count, 1)


class TestHasTraitsHelpersMaintainerHandler(unittest.TestCase):

    def test_any_value_followed_by_list_items_new_bad_value(self):
        # see enthought/traits#1277
        foo = Foo()
        handler = mock.Mock()

        # list_items(optional=True) will excuse the CannotCompare which isn't
        # a TraitList
        observe(
            object=foo,
            expression=expression.trait("any_value").list_items(optional=True),
            handler=handler,
        )

        # when
        # this triggers observer_change_handler
        foo.any_value = CannotCompare()

        # then
        # no errors

    def test_any_value_followed_by_list_items_old_bad_value(self):
        # see enthought/traits#1277
        foo = Foo()
        foo.any_value = CannotCompare()
        handler = mock.Mock()

        # list_items(optional=True) will excuse the CannotCompare which isn't
        # a TraitList
        observe(
            object=foo,
            expression=expression.trait("any_value").list_items(optional=True),
            handler=handler,
        )

        # when
        # this triggers observer_change_handler
        foo.any_value = foo.list_of_int  # a TraitList

        # then
        # no errors

        # when
        handler.reset_mock()
        foo.any_value.append(1)

        # then
        self.assertEqual(handler.call_count, 1)
