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

from traits.observers._observer_path import ObserverPath
from traits.observers._observers import NamedTraitObserver


def path_from_nodes(node, *nodes):
    root = path = ObserverPath(node=node)
    for node in nodes:
        next_path = ObserverPath(node=node)
        path.nexts.add(next_path)
        path = next_path
    return root


class TestObserverPath(unittest.TestCase):
    """ Test generic functions on ObserverPath."""

    def test_equality(self):
        path1 = path_from_nodes(1, 2, 3)
        path2 = path_from_nodes(1, 2, 3)
        self.assertEqual(path1, path2)
        self.assertEqual(hash(path1), hash(path2))

    def test_equality_different_type(self):
        path1 = path_from_nodes(1, 2, 3)
        self.assertNotEqual(path1, 1)

    def test_equality_different_length_nexts(self):
        path1 = ObserverPath(
            node=1,
            nexts=[path_from_nodes(2), path_from_nodes(3)],
        )
        path2 = ObserverPath(
            node=1,
            nexts=[path_from_nodes(2)],
        )
        self.assertNotEqual(path1, path2)
        self.assertNotEqual(hash(path1), hash(path2))

    def test_equality_order_of_nexts(self):
        # The order of items in nexts does not matter
        path1 = ObserverPath(
            node=1,
            nexts=[path_from_nodes(2), path_from_nodes(3)],
        )
        path2 = ObserverPath(
            node=1,
            nexts=[path_from_nodes(3), path_from_nodes(2)],
        )
        self.assertEqual(path1, path2)
        self.assertEqual(hash(path1), hash(path2))

    def test_equality_with_loop(self):
        path1 = ObserverPath(
            node=1, nexts=[ObserverPath(node=2)])
        path1.nexts.add(path1)

        path2 = ObserverPath(
            node=1, nexts=[ObserverPath(node=2)]
        )
        path2.nexts.add(path2)

        self.assertEqual(path1, path2)
        self.assertEqual(hash(path1), hash(path2))


class TestObserverPathIntegrateNamedTraitObserver(unittest.TestCase):
    """ Test integrating ObserverPath with NamedTraitObserver as nodes.
    """

    def test_observer_path_hash_with_named_listener(self):
        # Test equality + hashing using set passes.

        path1 = ObserverPath(
            node=NamedTraitObserver(name="foo", notify=True),
            nexts=[
                ObserverPath(
                    node=NamedTraitObserver(name="bar", notify=True),
                ),
            ],
        )
        path2 = ObserverPath(
            node=NamedTraitObserver(name="foo", notify=True),
            nexts=[
                ObserverPath(
                    node=NamedTraitObserver(name="bar", notify=True),
                ),
            ],
        )
        # This tests __eq__
        self.assertEqual(path1, path2)
