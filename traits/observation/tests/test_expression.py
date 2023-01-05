# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import inspect
import unittest

from traits.observation import expression
from traits.observation._anytrait_filter import anytrait_filter
from traits.observation._dict_item_observer import DictItemObserver
from traits.observation._filtered_trait_observer import FilteredTraitObserver
from traits.observation._list_item_observer import ListItemObserver
from traits.observation._metadata_filter import MetadataFilter
from traits.observation._named_trait_observer import NamedTraitObserver
from traits.observation._set_item_observer import SetItemObserver
from traits.observation._observer_graph import ObserverGraph


def create_graph(*nodes):
    """ Create an ObserverGraph with the given nodes joined one after another.
    Parameters
    ----------
    *nodes : hashable
        Items to be attached as nodes

    Returns
    -------
    ObserverGraph
    """
    node = nodes[-1]
    graph = ObserverGraph(node=node)
    for node in nodes[:-1][::-1]:
        graph = ObserverGraph(node=node, children=[graph])
    return graph


def create_expression(observer):
    """ Create an expression with a dummy observer for testing purposes.

    Parameters
    ----------
    observer : hashable
        Item to be used as a node on ObserverGraph

    Returns
    -------
    expression : ObserverExpression
    """
    return expression.SingleObserverExpression(observer)


class TestObserverExpressionComposition(unittest.TestCase):
    """ Test composition of ObserverExpression with generic observers."""

    def test_new_with_branches(self):
        observer = 1
        expr = create_expression(observer)
        expected = [
            create_graph(observer),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_or_operator(self):
        observer1 = 1
        observer2 = 2
        expr1 = create_expression(observer1)
        expr2 = create_expression(observer2)

        expr = expr1 | expr2
        expected = [
            create_graph(observer1),
            create_graph(observer2),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_or_maintain_order(self):
        # Test __or__ will maintain the order provided by the user.
        observer1 = 1
        observer2 = 2
        expr1 = create_expression(observer1)
        expr2 = create_expression(observer2)

        combined1 = expr1 | expr2
        combined2 = expr2 | expr1

        self.assertEqual(combined1._as_graphs(), combined2._as_graphs()[::-1])

    def test_then_operator(self):
        observer1 = 1
        observer2 = 2
        expr1 = create_expression(observer1)
        expr2 = create_expression(observer2)
        expr = expr1.then(expr2)

        expected = [
            create_graph(
                observer1,
                observer2,
            )
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_chained_then_or(self):
        observer1 = 1
        observer2 = 2
        observer3 = 3
        observer4 = 4
        expr1 = create_expression(observer1)
        expr2 = create_expression(observer2)
        expr3 = create_expression(observer3)
        expr4 = create_expression(observer4)

        expr = (expr1.then(expr2)) | (expr3.then(expr4))

        expected = [
            create_graph(
                observer1,
                observer2,
            ),
            create_graph(
                observer3,
                observer4,
            ),

        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_or_then_chained(self):
        observer1 = 1
        observer2 = 2
        observer3 = 3
        observer4 = 4
        expr1 = create_expression(observer1)
        expr2 = create_expression(observer2)
        expr3 = create_expression(observer3)
        expr4 = create_expression(observer4)

        expr = (expr1 | expr2).then(expr3 | expr4)

        expected = [
            ObserverGraph(
                node=observer1,
                children=[
                    create_graph(observer3),
                    create_graph(observer4),
                ],
            ),
            ObserverGraph(
                node=observer2,
                children=[
                    create_graph(observer3),
                    create_graph(observer4),
                ],
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_join_expressions(self):
        observer1 = 1
        observer2 = 2
        expr1 = create_expression(observer1)
        expr2 = create_expression(observer2)

        expr = expression.join(expr1, expr2)

        expected = [
            create_graph(
                observer1,
                observer2,
            )
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)


class TestObserverExpressionAnytrait(unittest.TestCase):
    """ Test anytrait function and method. """

    def test_anytrait_function_notify_true(self):
        expr = expression.anytrait(notify=True)
        expected = [
            create_graph(
                FilteredTraitObserver(filter=anytrait_filter, notify=True),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_anytrait_function_notify_false(self):
        expr = expression.anytrait(notify=False)
        expected = [
            create_graph(
                FilteredTraitObserver(filter=anytrait_filter, notify=False),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_anytrait_method_notify_true(self):
        expr = expression.trait("name").anytrait(notify=True)
        expected = [
            create_graph(
                NamedTraitObserver(name="name", notify=True, optional=False),
                FilteredTraitObserver(filter=anytrait_filter, notify=True),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_anytrait_method_notify_false(self):
        expr = expression.trait("name").anytrait(notify=False)
        expected = [
            create_graph(
                NamedTraitObserver(name="name", notify=True, optional=False),
                FilteredTraitObserver(filter=anytrait_filter, notify=False),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)


class TestObserverExpressionFilter(unittest.TestCase):
    """ Test ObserverExpression.match """

    def setUp(self):

        def anytrait(name, trait):
            return True

        self.anytrait = anytrait

    def test_match_notify_true(self):
        # Test the top-level function
        expr = expression.match(filter=self.anytrait)
        expected = [
            create_graph(
                FilteredTraitObserver(filter=self.anytrait, notify=True),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_match_notify_false(self):
        # Test the top-level function
        expr = expression.match(filter=self.anytrait, notify=False)
        expected = [
            create_graph(
                FilteredTraitObserver(filter=self.anytrait, notify=False),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_match_method_notify_true(self):
        # Test the instance method calls the top-level function correctly.
        expr = expression.match(filter=self.anytrait).match(
            filter=self.anytrait
        )
        expected = [
            create_graph(
                FilteredTraitObserver(filter=self.anytrait, notify=True),
                FilteredTraitObserver(filter=self.anytrait, notify=True),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_match_method_notify_false(self):
        # Test the instance method calls the top-level function correctly.
        expr = expression.match(filter=self.anytrait).match(
            filter=self.anytrait, notify=False,
        )
        expected = [
            create_graph(
                FilteredTraitObserver(filter=self.anytrait, notify=True),
                FilteredTraitObserver(filter=self.anytrait, notify=False),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_call_signatures(self):
        # Test to help developers keeping the two function signatures in-sync.
        # Remove this if the two need to divert in the future.
        top_level = expression.match
        method = expression.ObserverExpression().match
        self.assertEqual(
            inspect.signature(top_level), inspect.signature(method)
        )


class TestObserverExpressionFilterMetadata(unittest.TestCase):
    """ Test ObserverExpression.metadata """

    def test_metadata_notify_true(self):
        # Test the top-level function
        expr = expression.metadata("butterfly")
        expected = [
            create_graph(
                FilteredTraitObserver(
                    filter=MetadataFilter(metadata_name="butterfly"),
                    notify=True,
                ),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_metadata_notify_false(self):
        # Test the top-level function
        expr = expression.metadata("butterfly", notify=False)
        expected = [
            create_graph(
                FilteredTraitObserver(
                    filter=MetadataFilter(metadata_name="butterfly"),
                    notify=False,
                ),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_metadata_method_notify_true(self):
        # Test the instance method calls the top-level function correctly.
        expr = expression.metadata("bee").metadata("ant")
        expected = [
            create_graph(
                FilteredTraitObserver(
                    filter=MetadataFilter(metadata_name="bee"),
                    notify=True,
                ),
                FilteredTraitObserver(
                    filter=MetadataFilter(metadata_name="ant"),
                    notify=True,
                ),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_metadata_method_notify_false(self):
        # Test the instance method calls the top-level function correctly.
        expr = expression.metadata("bee").metadata("ant", notify=False)
        expected = [
            create_graph(
                FilteredTraitObserver(
                    filter=MetadataFilter(metadata_name="bee"),
                    notify=True,
                ),
                FilteredTraitObserver(
                    filter=MetadataFilter(metadata_name="ant"),
                    notify=False,
                ),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_call_signatures(self):
        # Test to help developers keeping the two function signatures in-sync.
        # Remove this if the two need to divert in the future.
        top_level = expression.metadata
        method = expression.ObserverExpression().metadata
        self.assertEqual(
            inspect.signature(top_level), inspect.signature(method)
        )


class TestObserverExpressionTrait(unittest.TestCase):
    """ Test ObserverExpression.trait """

    def test_trait_name(self):
        # Test the top-level function
        expr = expression.trait("name")
        expected = [
            create_graph(
                NamedTraitObserver(name="name", notify=True, optional=False)
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_trait_name_notify_false(self):
        # Test the top-level function
        expr = expression.trait("name", notify=False)
        expected = [
            create_graph(
                NamedTraitObserver(name="name", notify=False, optional=False)
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_trait_name_optional_true(self):
        # Test the top-level function
        expr = expression.trait("name", optional=True)
        expected = [
            create_graph(
                NamedTraitObserver(name="name", notify=True, optional=True)
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_trait_method(self):
        # Test the instance method calls the top-level function correctly.
        expr = expression.trait("name").trait("attr")
        expected = [
            create_graph(
                NamedTraitObserver(name="name", notify=True, optional=False),
                NamedTraitObserver(name="attr", notify=True, optional=False),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_trait_method_notify_false(self):
        # Test the instance method calls the top-level function correctly.
        expr = expression.trait("name").trait("attr", notify=False)
        expected = [
            create_graph(
                NamedTraitObserver(name="name", notify=True, optional=False),
                NamedTraitObserver(name="attr", notify=False, optional=False),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_trait_method_optional_true(self):
        # Test the instance method calls the top-level function correctly.
        expr = expression.trait("name").trait("attr", optional=True)
        expected = [
            create_graph(
                NamedTraitObserver(name="name", notify=True, optional=False),
                NamedTraitObserver(name="attr", notify=True, optional=True),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_call_signatures(self):
        # Test to help developers keeping the two function signatures in-sync.
        # Remove this if the two need to divert in the future.
        top_level_trait = expression.trait
        method_trait = expression.ObserverExpression().trait
        self.assertEqual(
            inspect.signature(top_level_trait), inspect.signature(method_trait)
        )


class TestObserverExpressionDictItem(unittest.TestCase):
    """ Test ObserverExpression.dict_items """

    def test_dict_items(self):
        expr = expression.dict_items()
        expected = [
            create_graph(
                DictItemObserver(notify=True, optional=False),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_dict_items_notify_false(self):
        expr = expression.dict_items(notify=False)
        expected = [
            create_graph(
                DictItemObserver(notify=False, optional=False),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_dict_items_optional_true(self):
        expr = expression.dict_items(optional=True)
        expected = [
            create_graph(
                DictItemObserver(notify=True, optional=True),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_dict_items_method_notify(self):
        # Test the instance method calls the top-level function correctly.
        expr = expression.dict_items().dict_items(notify=False)
        expected = [
            create_graph(
                DictItemObserver(notify=True, optional=False),
                DictItemObserver(notify=False, optional=False),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_dict_items_method_optional(self):
        # Test the instance method calls the top-level function correctly.
        expr = expression.dict_items().dict_items(optional=True)
        expected = [
            create_graph(
                DictItemObserver(notify=True, optional=False),
                DictItemObserver(notify=True, optional=True),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_call_signatures(self):
        # Test to help developers keeping the two function signatures in-sync.
        # Remove this if the two need to divert in the future.
        top_level = expression.dict_items
        method = expression.ObserverExpression().dict_items
        self.assertEqual(
            inspect.signature(top_level), inspect.signature(method)
        )


class TestObserverExpressionListItem(unittest.TestCase):
    """ Test ObserverExpression.list_items """

    def test_list_items(self):
        expr = expression.list_items()
        expected = [
            create_graph(
                ListItemObserver(notify=True, optional=False),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_list_items_notify_false(self):
        expr = expression.list_items(notify=False)
        expected = [
            create_graph(
                ListItemObserver(notify=False, optional=False),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_list_items_optional_true(self):
        expr = expression.list_items(optional=True)
        expected = [
            create_graph(
                ListItemObserver(notify=True, optional=True),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_list_items_method_notify(self):
        # Test the instance method calls the top-level function correctly.
        expr = expression.list_items().list_items(notify=False)
        expected = [
            create_graph(
                ListItemObserver(notify=True, optional=False),
                ListItemObserver(notify=False, optional=False),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_list_items_method_optional(self):
        # Test the instance method calls the top-level function correctly.
        expr = expression.list_items().list_items(optional=True)
        expected = [
            create_graph(
                ListItemObserver(notify=True, optional=False),
                ListItemObserver(notify=True, optional=True),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_call_signatures(self):
        # Test to help developers keeping the two function signatures in-sync.
        # Remove this if the two need to divert in the future.
        top_level = expression.list_items
        method = expression.ObserverExpression().list_items
        self.assertEqual(
            inspect.signature(top_level), inspect.signature(method)
        )


class TestObserverExpressionSetItem(unittest.TestCase):
    """ Test ObserverExpression.set_items """

    def test_set_items(self):
        expr = expression.set_items()
        expected = [
            create_graph(
                SetItemObserver(notify=True, optional=False),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_set_items_notify_false(self):
        expr = expression.set_items(notify=False)
        expected = [
            create_graph(
                SetItemObserver(notify=False, optional=False),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_set_items_optional_true(self):
        expr = expression.set_items(optional=True)
        expected = [
            create_graph(
                SetItemObserver(notify=True, optional=True),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_set_items_method_notify(self):
        # Test the instance method calls the top-level function correctly.
        expr = expression.set_items().set_items(notify=False)
        expected = [
            create_graph(
                SetItemObserver(notify=True, optional=False),
                SetItemObserver(notify=False, optional=False),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_set_items_method_optional(self):
        # Test the instance method calls the top-level function correctly.
        expr = expression.set_items().set_items(optional=True)
        expected = [
            create_graph(
                SetItemObserver(notify=True, optional=False),
                SetItemObserver(notify=True, optional=True),
            ),
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)

    def test_call_signatures(self):
        # Test to help developers keeping the two function signatures in-sync.
        # Remove this if the two need to divert in the future.
        top_level = expression.set_items
        method = expression.ObserverExpression().set_items
        self.assertEqual(
            inspect.signature(top_level), inspect.signature(method)
        )


class TestObserverExpressionEqualityAndHashing(unittest.TestCase):
    """ Test ObserverExpression.__eq__ and ObserverExpression.__hash__. """

    def test_trait_equality(self):
        expr1 = create_expression(1)
        expr2 = create_expression(1)
        self.assertEqual(expr1, expr2)
        self.assertEqual(hash(expr1), hash(expr2))

    def test_join_equality_with_then(self):
        # The following all result in the same graphs
        expr1 = create_expression(1)
        expr2 = create_expression(2)

        combined1 = expression.join(expr1, expr2)
        combined2 = expr1.then(expr2)

        self.assertEqual(combined1, combined2)
        self.assertEqual(hash(combined1), hash(combined2))

    def test_equality_of_parallel_expressions(self):
        expr1 = create_expression(1) | create_expression(2)
        expr2 = create_expression(1) | create_expression(2)
        self.assertEqual(expr1, expr2)
        self.assertEqual(hash(expr1), hash(expr2))

    def test_equality_different_type(self):
        expr = create_expression(1)
        self.assertNotEqual(expr, "1")


class TestObserverExpressionSlots(unittest.TestCase):
    """ Check that expressions use __slots__. """

    def test_single_expression(self):
        expr = create_expression(1)
        self.assertFalse(hasattr(expr, "__dict__"))

    def test_series_expression(self):
        expr = create_expression(1).then(create_expression(2))
        self.assertFalse(hasattr(expr, "__dict__"))

    def test_parallel_expression(self):
        expr = create_expression(1) | create_expression(2)
        self.assertFalse(hasattr(expr, "__dict__"))


class TestCompileFromExpr(unittest.TestCase):
    """ Tests for compile_expr. """

    # The complicated pieces are already tested; we just need to double
    # check that "_as_graphs" corresponds to "compile_expr" for a
    # handful of cases.

    def test_compile_expr(self):
        observer1 = 1
        observer2 = 2
        observer3 = 3
        observer4 = 4
        expr1 = create_expression(observer1)
        expr2 = create_expression(observer2)
        expr3 = create_expression(observer3)
        expr4 = create_expression(observer4)

        test_expressions = [
            expr1,
            expr1 | expr2,
            expr1 | expr2 | expr3,
            expr1.then(expr2),
            expr1.then(expr2).then(expr3),
            (expr1.then(expr2)) | (expr3.then(expr4)),
            expr1.list_items(),
            expr1.dict_items(),
            expr1.set_items(),
            expr1.anytrait(notify=False),
            expr1.anytrait(notify=True),
        ]
        for test_expression in test_expressions:
            with self.subTest(expression=test_expression):
                self.assertEqual(
                    expression.compile_expr(test_expression),
                    test_expression._as_graphs(),
                )
