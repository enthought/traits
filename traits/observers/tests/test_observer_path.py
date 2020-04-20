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

from traits.observers._observer_graph import ObserverGraph


def path_from_nodes(*nodes):
    nodes = nodes[::-1]
    graph = ObserverGraph(node=nodes[0])
    for node in nodes[1:]:
        graph = ObserverGraph(node=node, children=[graph])
    return graph


class TestObserverGraph(unittest.TestCase):
    """ Test generic functions on ObserverGraph."""

    def test_equality(self):
        path1 = path_from_nodes(1, 2, 3)
        path2 = path_from_nodes(1, 2, 3)
        self.assertEqual(path1, path2)
        self.assertEqual(hash(path1), hash(path2))

    def test_equality_different_type(self):
        path1 = path_from_nodes(1, 2, 3)
        self.assertNotEqual(path1, 1)

    def test_equality_different_length_children(self):
        path1 = ObserverGraph(
            node=1,
            children=[
                ObserverGraph(node=2),
                ObserverGraph(node=3),
            ],
        )
        path2 = ObserverGraph(
            node=1,
            children=[
                ObserverGraph(node=2),
            ],
        )
        self.assertNotEqual(path1, path2)

    def test_equality_order_of_children(self):
        # The order of items in children does not matter
        path1 = ObserverGraph(
            node=1,
            children=[
                ObserverGraph(node=2),
                ObserverGraph(node=3),
            ],
        )
        path2 = ObserverGraph(
            node=1,
            children=[
                ObserverGraph(node=3),
                ObserverGraph(node=2),
            ],
        )
        self.assertEqual(path1, path2)
        self.assertEqual(hash(path1), hash(path2))

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