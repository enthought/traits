# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" A simple topological sort on a dictionary graph.
"""


class CyclicGraph(Exception):
    """
    Exception for cyclic graphs.
    """

    def __init__(self):
        Exception.__init__(self, "Graph is cyclic")


def topological_sort(graph):
    """
    Returns the nodes in the graph in topological order.
    """
    discovered = {}
    explored = {}
    order = []

    def explore(node):
        children = graph.get(node, [])
        for child in children:
            if child in explored:
                pass
            elif child in discovered:
                raise CyclicGraph()
            else:
                discovered[child] = 1
                explore(child)
        explored[node] = 1
        order.append(node)

    for node in graph.keys():
        if node not in explored:
            explore(node)
    order.reverse()
    return order
