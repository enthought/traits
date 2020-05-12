# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import functools as _functools

from traits.observers._observer_graph import (
    ObserverGraph as _ObserverGraph,
)


class Expression:
    """
    Expression is an object for describing what traits are being observed
    for change notifications. It can be passed directly to
    ``HasTraits.observe`` method or the ``observe`` decorator.
    """
    def __init__(self):
        # ``_levels`` is a list of list of IObserver.
        # Each item corresponds to a layer of branches in the ObserverGraph.
        # The last item is the most nested level.
        # e.g. _levels = [[observer1, observer2], [observer3, observer4]]
        # observer3 and observer4 are both leaf nodes of a tree, and they are
        # "siblings" of each other. Each of observer3 and observer4 has two
        # parents: observer1 and observer2.
        # When ObserverGraph(s) are constructured from this expression, one
        # starts from the end of this list, to the top, and then continues to
        # the prior_expressions
        self._levels = []

        # Represent prior expressions to be combined in series (JOIN)
        # or in parallel (OR). This is either an instance of _SeriesExpression
        # or an instance of _ParallelExpression.
        self._prior_expression = None

    def __eq__(self, other):
        """ Return true if the other value is an Expression with equivalent
        content.

        Returns
        -------
        boolean
        """
        if type(other) is not type(self):
            return False
        return self._as_graphs() == other._as_graphs()

    def __or__(self, expression):
        """ Create a new expression that matches this expression OR
        the given expression. Equivalent expressions will be ignored.

        e.g. ``trait("age") | trait("number")`` will match either trait
        **age** or trait **number** on an object.

        Parameters
        ----------
        expression : traits.observers.expression.Expression

        Returns
        -------
        new_expression : traits.observers.expression.Expression
        """
        if self == expression:
            return self._copy()
        new = Expression()
        new._prior_expression = _ParallelExpression([self, expression])
        return new

    def then(self, expression):
        """ Create a new expression by extending this expression with
        the given expression.

        e.g. ``trait("child").then( trait("age") | trait("number") )``
        on an object matches ``child.age`` or ``child.number`` on the object.

        Parameters
        ----------
        expression : traits.observers.expression.Expression

        Returns
        -------
        new_expression : traits.observers.expression.Expression
        """

        if self._prior_expression is None and not self._levels:
            # this expression is empty...
            new = expression._copy()
        else:
            new = Expression()
            new._prior_expression = _SeriesExpression([self, expression])
        return new

    def _as_graphs(self):
        """ Return all the ObserverGraph for the observer framework to attach
        notifiers.

        This is considered private to the users and to modules outside of the
        ``observers`` subpackage, but public to modules within the
        ``observers`` subpackage.

        Returns
        -------
        graphs : list of ObserverGraph
        """
        return _create_graphs(self)

    def _new_with_branches(self, nodes):
        """ Create a new Expression with a new leaf nodes.

        Parameters
        ----------
        nodes : list of IObserver

        Returns
        -------
        new_expression : traits.observers.expression.Expression
        """
        expression = self._copy()
        expression._levels.append(nodes)
        return expression

    def _copy(self):
        """ Return a copy of this expression.

        Returns
        -------
        new_expression : traits.observers.expression.Expression
        """
        expression = Expression()
        expression._levels = self._levels.copy()
        if self._prior_expression is not None:
            expression._prior_expression = self._prior_expression._copy()
        return expression


def _create_graphs(expression, graphs=None):
    """ Create ObserverGraphs from a given expression.

    Parameters
    ----------
    expression : traits.observers.expression.Expression
    graphs : collection of ObserverGraph
        Leaf graphs to be added.
        Needed when this function is called recursively.

    Returns
    -------
    graphs : list of ObserverGraph
        New graphs
    """
    if graphs is None:
        graphs = []

    for nodes in expression._levels[::-1]:
        graphs = [
            _ObserverGraph(node=node, children=graphs) for node in nodes
        ]

    if expression._prior_expression is not None:
        graphs = expression._prior_expression._create_graphs(
            graphs=graphs,
        )
    return graphs


# _SeriesExpression and _ParallelExpression share an undeclared interface
# which require the classes to have implemented ``copy`` and ``_create_graphs``

class _SeriesExpression:
    """ Container of Expression for joining expressions in series.
    Used internally in this module.

    Parameters
    ----------
    expressions : list of Expression
        List of Expression to be combined in series.
    """

    def __init__(self, expressions):
        self.expressions = expressions.copy()

    def _copy(self):
        """ Return a copy of this instance.
        The internal ``expressions`` list is copied so it can be mutated.

        Returns
        -------
        series_expression : _SeriesExpression
        """
        return _SeriesExpression(self.expressions)

    def _create_graphs(self, graphs):
        """
        Create new ObserverGraph(s) from the joined expressions.

        Parameters
        ----------
        graphs : collection of ObserverGraph
            Leaf graphs to be added.
            Needed when this function is called recursively.

        Returns
        -------
        graphs : list of ObserverGraph
            New graphs
        """
        for expr in self.expressions[::-1]:
            graphs = _create_graphs(
                expr,
                graphs=graphs,
            )
        return graphs


class _ParallelExpression:
    """ Container of Expression for joining expressions in parallel.
    Used internally in this module.

    Parameters
    ----------
    expressions : list of Expression
        List of Expression to be combined in parallel.
    """

    def __init__(self, expressions):
        self.expressions = expressions.copy()

    def _copy(self):
        """ Return a copy of this instance.
        The internal ``expressions`` list is copied so it can be mutated.

        Returns
        -------
        parallel_expression : _ParallelExpression
        """
        return _ParallelExpression(self.expressions)

    def _create_graphs(self, graphs):
        """
        Create new ObserverGraph(s) from the joined expressions.

        Parameters
        ----------
        graphs : collection of ObserverGraph
            Leaf graphs to be added.
            Needed when this function is called recursively.

        Returns
        -------
        graphs : list of ObserverGraph
            New graphs
        """
        new_graphs = []
        for expr in self.expressions:
            or_graphs = _create_graphs(
                expr,
                graphs=graphs,
            )
            new_graphs.extend(or_graphs)
        return new_graphs


def join_(*expressions):
    """ Convenient function for joining many expressions in series
    using ``Expression.then``

    Parameters
    ----------
    *expressions : iterable of traits.observers.expression.Expression

    Returns
    -------
    new_expression : traits.observers.expression.Expression
        Joined expression.
    """
    return _functools.reduce(lambda e1, e2: e1.then(e2), expressions)
