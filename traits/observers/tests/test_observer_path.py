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

from traits.observers.observer_path import ObserverPath


def path_from_nodes(node, *nodes):
    root = path = ObserverPath(node=node)
    for node in nodes:
        next_path = ObserverPath(node=node)
        path.nexts = [next_path]
        path = next_path
    return root


class TestObserverPath(unittest.TestCase):

    def test_equality(self):
        path1 = path_from_nodes(1, 2, 3)
        path2 = path_from_nodes(1, 2, 3)
        self.assertEqual(path1, path2)

    def test_equality_different_type(self):
        path1 = path_from_nodes(1, 2, 3)
        self.assertNotEqual(path1, 1)