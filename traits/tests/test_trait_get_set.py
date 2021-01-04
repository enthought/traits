# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Test the 'trait_set', 'trait_get' interface to the HasTraits class.

"""
import unittest

from traits.api import HasTraits, Str, Int
from traits.testing.unittest_tools import UnittestTools


class TraitsObject(HasTraits):

    string = Str
    integer = Int


class TestTraitGet(UnittestTools, unittest.TestCase):
    def test_trait_set(self):
        obj = TraitsObject()
        obj.trait_set(string="foo")
        self.assertEqual(obj.string, "foo")
        self.assertEqual(obj.integer, 0)

    def test_trait_get(self):
        obj = TraitsObject()
        obj.trait_set(string="foo")
        values = obj.trait_get("string", "integer")
        self.assertEqual(values, {"string": "foo", "integer": 0})

    def test_trait_set_deprecated(self):
        obj = TraitsObject()

        with self.assertNotDeprecated():
            obj.trait_set(integer=1)

        with self.assertDeprecated():
            obj.set(string="foo")

        self.assertEqual(obj.string, "foo")
        self.assertEqual(obj.integer, 1)

    def test_trait_get_deprecated(self):
        obj = TraitsObject()
        obj.string = "foo"
        obj.integer = 1

        with self.assertNotDeprecated():
            values = obj.trait_get("integer")
        self.assertEqual(values, {"integer": 1})

        with self.assertDeprecated():
            values = obj.get("string")
        self.assertEqual(values, {"string": "foo"})

    def test_trait_set_quiet(self):
        obj = TraitsObject()
        obj.string = "foo"

        with self.assertTraitDoesNotChange(obj, "string"):
            obj.trait_set(trait_change_notify=False, string="bar")

        self.assertEqual(obj.string, "bar")

    def test_trait_setq(self):
        obj = TraitsObject()
        obj.string = "foo"

        with self.assertTraitDoesNotChange(obj, "string"):
            obj.trait_setq(string="bar")

        self.assertEqual(obj.string, "bar")
