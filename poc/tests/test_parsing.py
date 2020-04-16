import unittest

import lark.exceptions

from poc import parsing
from poc import expressions


class TestParsing(unittest.TestCase):

    def test_simple(self):
        actual = parsing.parse("a")
        expected = expressions.t("a")
        self.assertEqual(actual, expected)

    def test_join(self):
        actual = parsing.parse("a.b.c")
        expected = expressions.t("a").t("b").t("c")
        self.assertEqual(actual, expected)

    def test_join_with_colon(self):
        actual = parsing.parse("a:b:c")
        expected = expressions.t("a", False).t("b", False).t("c")
        self.assertEqual(actual, expected)

    def test_or_with_commas(self):
        actual = parsing.parse("a,b,c")
        expected = (
            expressions.t("a")
            | expressions.t("b")
            | expressions.t("c")
        )
        self.assertEqual(actual, expected)

    def test_or_with_join_nested(self):
        actual = parsing.parse("a.b.c,d.e")
        expected = (
            expressions.t("a").t("b").t("c")
            | expressions.t("d").t("e")
        )
        self.assertEqual(actual, expected)

    def test_items_support(self):
        actual = parsing.parse("a.items:b")

        items_attr_or_items = (
            expressions.t("items", notify=False, optional=True)
            | expressions.items(notify=False)
        )
        expected = (
            expressions.t("a").then(
                items_attr_or_items).t(
                    "b")
        )
        self.assertEqual(actual, expected)

    def test_grouped_or(self):
        actual = parsing.parse("root.[left,right]")
        expected = (
            expressions.t("root").then(
                expressions.t("left") | expressions.t("right"))
        )
        self.assertEqual(actual, expected)

    def test_grouped_or_extended(self):
        actual = parsing.parse("root.[left,right].value")
        expected = (
            expressions.t("root").then(
                expressions.t("left") | expressions.t("right")).t(
                    "value")
        )
        self.assertEqual(actual, expected)

    def test_unparse_content(self):
        with self.assertRaises(lark.exceptions.UnexpectedCharacters):
            parsing.parse("a.b.c^abc")

    def test_recursion_support(self):
        actual = parsing.parse("root.[left,right]*.value")
        expected = (
            expressions.t("root").recursive(
                expressions.t("left") | expressions.t("right")).t(
                    "value")
        )
        self.assertEqual(actual, expected)

    def test_recurse_twice(self):
        actual = parsing.parse("[b:c*]*")
        expected = expressions.recursive(
            expressions.t("b", False).recursive(expressions.t("c"))
        )
        self.assertEqual(actual, expected)

    def test_group_and_join(self):
        actual = parsing.parse("[a:b,c].d")
        expected = (
            expressions.t("a", False).t("b")
            | expressions.t("c")
        ).t("d")
        self.assertEqual(actual, expected)

    def test_group_followed_by_colon(self):
        actual = parsing.parse("[a:b,c]:d")
        expected = (
            expressions.t("a", False).t("b", False)
            | expressions.t("c", False)
        ).t("d")
        self.assertEqual(actual, expected)

    def test_join_double_recursion_modify_last(self):
        actual = parsing.parse("a.[b:c*]*.d")
        expected = (
            expressions.t("a").recursive(
                expressions.t("b", False).recursive(
                    expressions.t("c"))).t("d")
        )
        self.assertEqual(actual, expected)

    def test_multi_branch_then_or_modify_last(self):
        actual = parsing.parse("root.[a.b.c.d,value]:g")
        expected = (
            expressions.t("root").then(
                expressions.t("a").t("b").t("c").t("d", False)
                | expressions.t("value", False)
            ).t("g")
        )
        self.assertEqual(actual, expected)
