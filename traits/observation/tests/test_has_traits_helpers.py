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
from unittest import mock
import warnings

from traits.api import (
    Bool, Dict, HasTraits, List, Instance, Int, Property, Set, Union,
)
from traits.observation import _has_traits_helpers as helpers
from traits.observation import expression
from traits.observation.observe import observe


class Bar(HasTraits):

    count = Int()


class Foo(HasTraits):

    list_of_int = List(Int)

    instance = Instance(Bar)

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
    """ Class for supporting TestHasTraitsHelpersWarning """

    list_values = List(comparison_mode=2)
    dict_values = Dict(comparison_mode=2)
    set_values = Set(comparison_mode=2)
    property_list = Property(List(comparison_mode=2))
    container_in_union = Union(
        None,
        Set(comparison_mode=1),
        comparison_mode=2,
    )


class TestHasTraitsHelpersWarning(unittest.TestCase):

    def test_warn_list_explicit_equality_comparison_mode(self):
        # Test a warning is emitted if the comparison mode is explicitly set to
        # equality. Note that iter_objects is for providing values for the
        # next observers, hence imitates the use case when membership in a
        # container is observed.
        instance = ObjectWithEqualityComparisonMode()

        name_to_type = {
            "list_values": "List",
            "dict_values": "Dict",
            "set_values": "Set",
            "container_in_union": "Union",
        }
        for trait_name, type_name in name_to_type.items():
            with self.subTest(trait_name=trait_name, type_name=type_name):

                with self.assertWarns(RuntimeWarning) as warn_context:
                    list(helpers.iter_objects(instance, trait_name))

                self.assertIn(
                    "Redefine the trait with {}(..., comparison_mode".format(
                        type_name
                    ),
                    str(warn_context.warning)
                )

    def test_union_equality_comparison_mode_prevent_change_event(self):
        # Justification for the warning: Reassess if the warning is still
        # needed if this test fails.
        instance = ObjectWithEqualityComparisonMode()
        instance.container_in_union = {1}
        handler = mock.Mock()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            observe(
                object=instance,
                expression=expression.trait("container_in_union").set_items(),
                handler=handler,
            )

        # New set, but equals to the previous
        instance.container_in_union = {1}
        handler.reset_mock()

        # when
        instance.container_in_union.add(2)

        # The expected value is 1.
        # If this fails with 1 != 0, consider removing the warning.
        self.assertEqual(handler.call_count, 0)

    def test_list_equality_comparison_mode_prevent_change_event(self):
        # Justification for the warning: Reassess if the warning is still
        # needed if this test fails.
        instance = ObjectWithEqualityComparisonMode()
        instance.list_values = [1]
        handler = mock.Mock()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            observe(
                object=instance,
                expression=expression.trait("list_values").list_items(),
                handler=handler,
            )

        # New list, but equals to the previous
        instance.list_values = [1]
        handler.reset_mock()

        # when
        instance.list_values.append(2)

        # The expected value is 1.
        # If this fails with 1 != 0, consider removing the warning.
        self.assertEqual(handler.call_count, 0)

    def test_dict_equality_comparison_mode_prevent_change_event(self):
        # Justification for the warning: Reassess if the warning is still
        # needed if this test fails.
        instance = ObjectWithEqualityComparisonMode()
        instance.dict_values = {"1": 1}
        handler = mock.Mock()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            observe(
                object=instance,
                expression=expression.trait("dict_values").dict_items(),
                handler=handler,
            )

        # New dict, but equals to the previous
        instance.dict_values = {"1": 1}
        handler.reset_mock()

        # when
        instance.dict_values.pop("1")

        # The expected value is 1.
        # If this fails with 1 != 0, consider removing the warning.
        self.assertEqual(handler.call_count, 0)

    def test_set_equality_comparison_mode_prevent_change_event(self):
        # Justification for the warning: Reassess if the warning is still
        # needed if this test fails.
        instance = ObjectWithEqualityComparisonMode()
        instance.set_values = {1}
        handler = mock.Mock()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            observe(
                object=instance,
                expression=expression.trait("set_values").set_items(),
                handler=handler,
            )

        # New set, but equals to the previous
        instance.set_values = {1}
        handler.reset_mock()

        # when
        instance.set_values.add(2)

        # The expected value is 1.
        # If this fails with 1 != 0, consider removing the warning.
        self.assertEqual(handler.call_count, 0)

    def test_no_warn_for_property(self):
        # property is computed and downstream observers are not useful.
        # they do exist in the wild. Do not warn for those.

        instance = ObjectWithEqualityComparisonMode()

        # almost equivalent to assertNoWarns...
        with self.assertRaises(AssertionError):
            with self.assertWarns(RuntimeWarning):
                list(helpers.iter_objects(instance, "property_list"))
