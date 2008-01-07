import sys, unittest

from enthought.testing.api import doctest_for_module

import enthought.util.graph as graph
from enthought.util.graph import *

class GraphDocTestCase(doctest_for_module(graph)):
    pass

class MapTestCase(unittest.TestCase):
    def test_map(self):
        'map'
        self.assertEqual(map(str, {}), {})
        self.assertEqual(map(str, {1:[2,3]}), {'1':['2','3']})
        self.assertEqual(map(lambda x: x, {1:[2,3]}), {1:[2,3]})

class ReachableGraphTestCase(unittest.TestCase):

    def _base(self, graph, nodes, result, error=None):
        if error:
            self.assertRaises(error, lambda: self._base(graph, nodes, result))
        else:
            self.assertEqual(reachable_graph(graph, nodes), result)

    def test_reachable_graph(self):
        'reachable_graph'
        self._base({}, [], {})
        self._base({}, [1], {}, error=KeyError)
        self._base({1:[2,3], 0:[3]}, [1], {1:[2,3]})
        self._base({1:[2,3], 1:[3]}, [1], {1:[2,3], 1:[3]})
        self._base({1:[2,3], 2:[3]}, [1], {1:[2,3], 2:[3]})
        self._base({1:[2,3], 2:[3]}, [2], {2:[3]})
        self._base({1:[2,3], 2:[3]}, [3], {})
        self._base({1:[2], 3:[4]}, [1,3], {1:[2], 3:[4]})

class ReverseGraphTestCase(unittest.TestCase):
    def _base(self, graph, result, error=None):
        if error:
            self.assertRaises(error, lambda: self._base(graph, result))
        else:
            self.assertEqual(reverse(graph), result)

    def test_reverse(self):
        'reverse'
        self._base({}, {})
        self._base({1:[]}, {1:[]})
        self._base({1:[2]}, {2:[1], 1:[]})
        self._base({1:[2,3]}, {2:[1], 3:[1], 1:[]})



if __name__ == '__main__':
    unittest.main(argv=sys.argv)
