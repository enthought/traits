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
