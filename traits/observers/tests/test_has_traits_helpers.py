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
    Bool, HasTraits, List, Instance, Int, Property,
)
from traits.observers import _has_traits_helpers as helpers


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
