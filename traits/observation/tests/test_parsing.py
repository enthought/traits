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

from traits.observation.parsing import parse
from traits.observation.expression import (
    dict_items,
    list_items,
    metadata,
    set_items,
    trait,
)


class TestParsingSeriesJoin(unittest.TestCase):

    def test_join(self):
        actual = parse("a.b.c")
        expected = trait("a").trait("b").trait("c")
        self.assertEqual(actual, expected)

    def test_join_with_colon(self):
        actual = parse("a:b:c")
        expected = trait("a", False).trait("b", False).trait("c")
        self.assertEqual(actual, expected)


class TestParsingOr(unittest.TestCase):

    def test_or_with_commas(self):
        actual = parse("a,b,c")
        expected = trait("a") | trait("b") | trait("c")
        self.assertEqual(actual, expected)

    def test_or_with_join_nested(self):
        actual = parse("a.b.c,d.e")
        expected = (
            trait("a").trait("b").trait("c")
            | trait("d").trait("e")
        )
        self.assertEqual(actual, expected)


class TestParsingGroup(unittest.TestCase):

    def test_grouped_or(self):
        actual = parse("root.[left,right]")
        expected = trait("root").then(trait("left") | trait("right"))

        self.assertEqual(actual, expected)

    def test_grouped_or_extended(self):
        actual = parse("root.[left,right].value")
        expected = (
            trait("root").then(
                trait("left") | trait("right")).trait("value")
        )
        self.assertEqual(actual, expected)

    def test_multi_branch_then_or_apply_notify_flag_to_last_item(self):
        actual = parse("root.[a.b.c.d,value]:g")
        expected = (
            trait("root").then(
                trait("a").trait("b").trait("c").trait("d", False)
                | trait("value", False)
            ).trait("g")
        )
        self.assertEqual(actual, expected)


class TestParsingMetadata(unittest.TestCase):

    def test_metadata(self):
        actual = parse("+name")
        expected = metadata("name", notify=True)
        self.assertEqual(actual, expected)

    def test_metadata_notify_false(self):
        actual = parse("+name:+attr")
        expected = metadata("name", notify=False).metadata("attr", notify=True)
        self.assertEqual(actual, expected)


class TestParsingTrait(unittest.TestCase):

    def test_simple_trait(self):
        actual = parse("a")
        expected = trait("a")
        self.assertEqual(actual, expected)

    def test_trait_not_notifiy(self):
        actual = parse("a:b")
        expected = trait("a", notify=False).trait("b")
        self.assertEqual(actual, expected)


class TestParsingItems(unittest.TestCase):

    def test_items(self):
        actual = parse("items")
        expected = (
            trait("items", optional=True)
            | dict_items(optional=True)
            | list_items(optional=True)
            | set_items(optional=True)
        )
        self.assertEqual(actual, expected)

    def test_items_not_notify(self):
        actual = parse("items:attr")
        expected = (
            trait("items", notify=False, optional=True)
            | dict_items(notify=False, optional=True)
            | list_items(notify=False, optional=True)
            | set_items(notify=False, optional=True)
        ).trait("attr")
        self.assertEqual(actual, expected)
