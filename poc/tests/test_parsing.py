import unittest

from poc.generated_parser import (
    UnexpectedCharacters,
    UnexpectedToken,
)

from poc import parsing
from poc import expressions


class TestParsing(unittest.TestCase):

    def test_simple(self):
        actual = parsing.parse("a")
        expected = expressions.trait("a")
        self.assertEqual(actual, expected)

    def test_join(self):
        actual = parsing.parse("a.b.c")
        expected = expressions.trait("a").trait("b").trait("c")
        self.assertEqual(actual, expected)

    def test_join_with_colon(self):
        actual = parsing.parse("a:b:c")
        expected = expressions.trait("a", False).trait("b", False).trait("c")
        self.assertEqual(actual, expected)

    def test_or_with_commas(self):
        actual = parsing.parse("a,b,c")
        expected = (
            expressions.trait("a")
            | expressions.trait("b")
            | expressions.trait("c")
        )
        self.assertEqual(actual, expected)

    def test_or_with_join_nested(self):
        actual = parsing.parse("a.b.c,d.e")
        expected = (
            expressions.trait("a").trait("b").trait("c")
            | expressions.trait("d").trait("e")
        )
        self.assertEqual(actual, expected)

    def test_items_support(self):
        actual = parsing.parse("a.items:b")

        items_attr_or_items = (
            expressions.trait("items", notify=False, optional=True)
            | expressions.list_items(notify=False, optional=True)
            | expressions.dict_items(notify=False, optional=True)
            | expressions.set_items(notify=False, optional=True)
        )
        expected = (
            expressions.trait("a").then(
                items_attr_or_items).trait(
                    "b")
        )
        self.assertEqual(actual, expected)

    def test_grouped_or(self):
        actual = parsing.parse("root.[left,right]")
        expected = (
            expressions.trait("root").then(
                expressions.trait("left") | expressions.trait("right"))
        )
        self.assertEqual(actual, expected)

    def test_grouped_or_extended(self):
        actual = parsing.parse("root.[left,right].value")
        expected = (
            expressions.trait("root").then(
                expressions.trait("left") | expressions.trait("right")).trait(
                    "value")
        )
        self.assertEqual(actual, expected)

    def test_unparse_content(self):
        with self.assertRaises(UnexpectedCharacters):
            parsing.parse("a.b.c^abc")

    def test_error_empty_string(self):
        with self.assertRaises(UnexpectedToken):
            parsing.parse("")

    def test_error_unconnected_expressions(self):
        with self.assertRaises(UnexpectedToken):
            parsing.parse("[a.b]c")

    def test_recursion_support(self):
        actual = parsing.parse("root.[left,right]*.value")
        expected = (
            expressions.trait("root").recursive(
                expressions.trait("left") | expressions.trait("right")).trait(
                    "value")
        )
        self.assertEqual(actual, expected)

    def test_recurse_twice(self):
        actual = parsing.parse("[b:c*]*")
        expected = expressions.recursive(
            expressions.trait("b", False).recursive(expressions.trait("c"))
        )
        self.assertEqual(actual, expected)

    def test_group_and_join(self):
        actual = parsing.parse("[a:b,c].d")
        expected = (
            expressions.trait("a", False).trait("b")
            | expressions.trait("c")
        ).trait("d")
        self.assertEqual(actual, expected)

    def test_group_followed_by_colon(self):
        actual = parsing.parse("[a:b,c]:d")
        expected = (
            expressions.trait("a", False).trait("b", False)
            | expressions.trait("c", False)
        ).trait("d")
        self.assertEqual(actual, expected)

    def test_join_double_recursion_modify_last(self):
        actual = parsing.parse("a.[b:c*]*.d")
        expected = (
            expressions.trait("a").recursive(
                expressions.trait("b", False).recursive(
                    expressions.trait("c"))).trait("d")
        )
        self.assertEqual(actual, expected)

    def test_multi_branch_then_or_modify_last(self):
        actual = parsing.parse("root.[a.b.c.d,value]:g")
        expected = (
            expressions.trait("root").then(
                expressions.trait("a").trait("b").trait("c").trait("d", False)
                | expressions.trait("value", False)
            ).trait("g")
        )
        self.assertEqual(actual, expected)
