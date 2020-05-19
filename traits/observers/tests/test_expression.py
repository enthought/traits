# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
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

from traits.observers import expression
from traits.observers._named_trait_observer import NamedTraitObserver
from traits.observers._observer_graph import ObserverGraph


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
    expression : Expression
    """
    return expression.SingleObserverExpression(observer)


class TestExpressionComposition(unittest.TestCase):
    """ Test composition of Expression with generic observers."""

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

        expr = expression.join_(expr1, expr2)

        expected = [
            create_graph(
                observer1,
                observer2,
            )
        ]
        actual = expr._as_graphs()
        self.assertEqual(actual, expected)


class TestExpressionTrait(unittest.TestCase):
    """ Test Expression.trait """

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
        method_trait = expression.Expression().trait
        self.assertEqual(
            inspect.signature(top_level_trait), inspect.signature(method_trait)
        )


class TestExpressionEquality(unittest.TestCase):
    """ Test Expression.__eq__ """

    def test_trait_equality(self):
        expr1 = create_expression(1)
        expr2 = create_expression(1)
        self.assertEqual(expr1, expr2)

    def test_join_equality_with_then(self):
        # The following all result in the same graphs
        expr1 = create_expression(1)
        expr2 = create_expression(2)

        combined1 = expression.join_(expr1, expr2)
        combined2 = expr1.then(expr2)

        self.assertEqual(combined1, combined2)

    def test_equality_different_type(self):
        expr = create_expression(1)
        self.assertNotEqual(expr, "1")
