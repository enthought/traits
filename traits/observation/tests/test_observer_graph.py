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

from traits.observation._observer_graph import ObserverGraph


def graph_from_nodes(*nodes):
    nodes = nodes[::-1]
    graph = ObserverGraph(node=nodes[0])
    for node in nodes[1:]:
        graph = ObserverGraph(node=node, children=[graph])
    return graph


class TestObserverGraph(unittest.TestCase):
    """ Test generic functions on ObserverGraph."""

    def test_equality(self):
        graph1 = graph_from_nodes(1, 2, 3)
        graph2 = graph_from_nodes(1, 2, 3)
        self.assertEqual(graph1, graph2)
        self.assertEqual(hash(graph1), hash(graph2))

    def test_equality_different_type(self):
        graph1 = graph_from_nodes(1, 2, 3)
        self.assertNotEqual(graph1, 1)

    def test_equality_different_length_children(self):
        graph1 = ObserverGraph(
            node=1,
            children=[
                ObserverGraph(node=2),
                ObserverGraph(node=3),
            ],
        )
        graph2 = ObserverGraph(
            node=1,
            children=[
                ObserverGraph(node=2),
            ],
        )
        self.assertNotEqual(graph1, graph2)

    def test_equality_order_of_children(self):
        # The order of items in children does not matter
        graph1 = ObserverGraph(
            node=1,
            children=[
                ObserverGraph(node=2),
                ObserverGraph(node=3),
            ],
        )
        graph2 = ObserverGraph(
            node=1,
            children=[
                ObserverGraph(node=3),
                ObserverGraph(node=2),
            ],
        )
        self.assertEqual(graph1, graph2)
        self.assertEqual(hash(graph1), hash(graph2))

    def test_children_ordered(self):
        child_graph = ObserverGraph(node=2)
        graph = ObserverGraph(
            node=1,
            children=[
                child_graph,
                ObserverGraph(node=3),
            ],
        )
        self.assertIs(graph.children[0], child_graph)

    def test_children_unique(self):
        child_graph = ObserverGraph(node=2)

        with self.assertRaises(ValueError) as exception_cm:
            ObserverGraph(
                node=1,
                children=[
                    child_graph,
                    ObserverGraph(node=2),
                ],
            )

        self.assertEqual(
            str(exception_cm.exception), "Not all children are unique.")
