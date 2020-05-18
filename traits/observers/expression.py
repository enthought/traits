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

from traits.observers._named_trait_observer import (
    NamedTraitObserver as _NamedTraitObserver,
)
from traits.observers._observer_graph import (
    ObserverGraph as _ObserverGraph,
)

# Expression is a public user interface for constructing ObserverGraph.
# It wraps an instance of _IExpression which is hidden from the user.
# Despite the name, Expression itself is not an instance of _IExpression.


class Expression:
    """
    Expression is an object for describing what traits are being observed
    for change notifications. It can be passed directly to
    ``HasTraits.observe`` method or the ``observe`` decorator.

    An Expression is typically created using one of the top-level functions
    provided in this module, e.g.``trait``.
    """
    def __init__(self, _expression=None):
        if _expression is None:
            _expression = _EmptyExpression()
        self._expression = _expression

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
            return self
        return Expression(
            _ParallelExpression(self._expression, expression._expression)
        )

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
        return Expression(
            _SeriesExpression(self._expression, expression._expression)
        )

    def trait(self, name, notify=True, optional=False):
        """ Create a new expression for observing a trait with the exact
        name given.

        Events emitted (if any) will be instances of ``TraitChangeEvent``.

        Parameters
        ----------
        name : str
            Name of the trait to match.
        notify : boolean, optional
            Whether to notify for changes.
        optional : boolean, optional
            If true, skip this observer if the requested trait is not found.

        Returns
        -------
        new_expression : traits.observers.expression.Expression
        """
        return self.then(trait(name=name, notify=notify, optional=optional))

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
        return self._expression.create_graphs(branches=[])


class _IExpression:
    """ Interface to be implemented for objects to be wrapped in
    Expression. Such objects are responsible for constructing an ObserverGraph
    with the given information and context.

    All these objects are used internally.
    """

    def create_graphs(self, branches):
        """ Return a list of ObserverGraph with the given branches.

        Parameters
        ----------
        branches : list of ObserverGraph
            Graphs to be used as branches.
        """
        raise NotImplementedError("'create_graphs' must be implemented.")


class _EmptyExpression:
    """ Empty expression as a placeholder."""

    def create_graphs(self, branches):
        return []


class _SingleObserverExpression:
    """ Container of Expression for wrapping a single observer.
    Used internally in this module.
    """

    def __init__(self, observer):
        self.observer = observer

    def create_graphs(self, branches):
        return [
            _ObserverGraph(node=self.observer, children=branches),
        ]


class _SeriesExpression:
    """ Container of Expression for joining expressions in series.
    Used internally in this module.

    Parameters
    ----------
    first : _IExpression
        Left expression to be joined in series.
    second : _IExpression
        Right expression to be joined in series.
    """

    def __init__(self, first, second):
        self._first = first
        self._second = second

    def create_graphs(self, branches):
        branches = self._second.create_graphs(branches=branches)
        return self._first.create_graphs(branches=branches)


class _ParallelExpression:
    """ Container of Expression for joining expressions in parallel.
    Used internally in this module.

    Parameters
    ----------
    left : _IExpression
        Left expression to be joined in parallel.
    right : _IExpression
        Right expression to be joined in parallel.
    """

    def __init__(self, left, right):
        self._left = left
        self._right = right

    def create_graphs(self, branches):
        left_graphs = self._left.create_graphs(branches=branches)
        right_graphs = self._right.create_graphs(branches=branches)
        return left_graphs + right_graphs


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


def trait(name, notify=True, optional=False):
    """ Create a new expression for observing a trait with the exact
    name given.

    Events emitted (if any) will be instances of ``TraitChangeEvent``.

    Parameters
    ----------
    name : str
        Name of the trait to match.
    notify : boolean, optional
        Whether to notify for changes.
    optional : boolean, optional
        If true, skip this observer if the requested trait is not found.

    Returns
    -------
    new_expression : traits.observers.expression.Expression
    """
    observer = _NamedTraitObserver(
        name=name, notify=notify, optional=optional)
    return Expression(_SingleObserverExpression(observer))
