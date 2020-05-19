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

from traits.observers._filtered_trait_observer import (
    FilteredTraitObserver as _FilteredTraitObserver,
)
from traits.observers._named_trait_observer import (
    NamedTraitObserver as _NamedTraitObserver,
)
from traits.observers._observer_graph import (
    ObserverGraph as _ObserverGraph,
)

# Expression is a public user interface for constructing ObserverGraph.


class Expression:
    """
    Expression is an object for describing what traits are being observed
    for change notifications. It can be passed directly to
    ``HasTraits.observe`` method or the ``observe`` decorator.

    An Expression is typically created using one of the top-level functions
    provided in this module, e.g. ``trait``.
    """

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
        the given expression.

        e.g. ``trait("age") | trait("number")`` will match either trait
        **age** or trait **number** on an object.

        Parameters
        ----------
        expression : traits.observers.expression.Expression

        Returns
        -------
        new_expression : traits.observers.expression.Expression
        """
        return ParallelExpression(self, expression)

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
        return SeriesExpression(self, expression)

    def match(self, filter, notify=True):
        """ Create a new expression for observing traits using the
        given filter.

        Events emitted (if any) will be instances of
        :py:class:`~traits.observers.events.TraitChangeEvent`.

        Parameters
        ----------
        filter : callable(str, CTrait) -> boolean
            A callable that receives the name of a trait and the corresponding
            trait definition. The returned boolean indicates whether the trait
            is observed. In order to remove an existing observer with the
            equivalent filter, the filter callables must compare equally. The
            callable must also be hashable.
        notify : boolean, optional
            Whether to notify for changes.

        Returns
        -------
        new_expression : traits.observers.expressions.Expression
        """
        return self.then(match(filter=filter, notify=notify))

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
        return self._create_graphs(branches=[])

    def _create_graphs(self, branches):
        """ Return a list of ObserverGraph with the given branches.

        Parameters
        ----------
        branches : list of ObserverGraph
            Graphs to be used as branches.

        Returns
        -------
        graphs : list of ObserverGraph
        """
        raise NotImplementedError("'_create_graphs' must be implemented.")


class SingleObserverExpression(Expression):
    """ Container of Expression for wrapping a single observer.
    """

    def __init__(self, observer):
        self.observer = observer

    def _create_graphs(self, branches):
        return [
            _ObserverGraph(node=self.observer, children=branches),
        ]


class SeriesExpression(Expression):
    """ Container of Expression for joining expressions in series.

    Parameters
    ----------
    first : traits.observers.expression.Expression
        Left expression to be joined in series.
    second : traits.observers.expression.Expression
        Right expression to be joined in series.
    """

    def __init__(self, first, second):
        self._first = first
        self._second = second

    def _create_graphs(self, branches):
        branches = self._second._create_graphs(branches=branches)
        return self._first._create_graphs(branches=branches)


class ParallelExpression(Expression):
    """ Container of Expression for joining expressions in parallel.

    Parameters
    ----------
    left : traits.observers.expression.Expression
        Left expression to be joined in parallel.
    right : traits.observers.expression.Expression
        Right expression to be joined in parallel.
    """

    def __init__(self, left, right):
        self._left = left
        self._right = right

    def _create_graphs(self, branches):
        left_graphs = self._left._create_graphs(branches=branches)
        right_graphs = self._right._create_graphs(branches=branches)
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


def match(filter, notify=True):
    """ Create a new expression for observing traits using the
    given filter.

    Events emitted (if any) will be instances of
    :py:class:`~traits.observers.events.TraitChangeEvent`.

    Parameters
    ----------
    filter : callable(str, CTrait) -> boolean
        A callable that receives the name of a trait and the corresponding
        trait definition. The returned boolean indicates whether the trait is
        observed. In order to remove an existing observer with the equivalent
        filter, the filter callables must compare equally. The callable must
        also be hashable.
    notify : boolean, optional
        Whether to notify for changes.

    Returns
    -------
    new_expression : traits.observers.expressions.Expression
    """
    observer = _FilteredTraitObserver(notify=notify, filter=filter)
    return SingleObserverExpression(observer)


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
    return SingleObserverExpression(observer)
