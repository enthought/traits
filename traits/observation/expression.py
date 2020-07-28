# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import functools

from traits.observation._dict_item_observer import DictItemObserver
from traits.observation._filtered_trait_observer import FilteredTraitObserver
from traits.observation._list_item_observer import ListItemObserver
from traits.observation._metadata_filter import MetadataFilter
from traits.observation._named_trait_observer import NamedTraitObserver
from traits.observation._observer_graph import ObserverGraph
from traits.observation._set_item_observer import SetItemObserver

# ObserverExpression is a public user interface for constructing ObserverGraph.


class ObserverExpression:
    """
    ObserverExpression is an object for describing what traits are being
    observed for change notifications. It can be passed directly to
    ``HasTraits.observe`` method or the ``observe`` decorator.

    An ObserverExpression is typically created using one of the top-level
    functions provided in this module, e.g. ``trait``.
    """

    def __eq__(self, other):
        """ Return true if the other value is an ObserverExpression with
        equivalent content.

        Returns
        -------
        bool
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
        expression : ObserverExpression

        Returns
        -------
        new_expression : ObserverExpression
        """
        return ParallelObserverExpression(self, expression)

    def then(self, expression):
        """ Create a new expression by extending this expression with
        the given expression.

        e.g. ``trait("child").then( trait("age") | trait("number") )``
        on an object matches ``child.age`` or ``child.number`` on the object.

        Parameters
        ----------
        expression : ObserverExpression

        Returns
        -------
        new_expression : ObserverExpression
        """
        return SeriesObserverExpression(self, expression)

    def match(self, filter, notify=True):
        """ Create a new expression for observing traits using the
        given filter.

        Events emitted (if any) will be instances of
        :class:`~traits.observation.events.TraitChangeEvent`.

        Parameters
        ----------
        filter : callable(str, CTrait) -> bool
            A callable that receives the name of a trait and the corresponding
            trait definition. The returned bool indicates whether the trait
            is observed. In order to remove an existing observer with the
            equivalent filter, the filter callables must compare equally. The
            callable must also be hashable.
        notify : bool, optional
            Whether to notify for changes. Default is to notify.

        Returns
        -------
        new_expression : ObserverExpression
        """
        return self.then(match(filter=filter, notify=notify))

    def metadata(self, metadata_name, notify=True):
        """ Return a new expression for observing traits where the given
        metadata is not None.

        Events emitted (if any) will be instances of
        :class:`~traits.observation.events.TraitChangeEvent`.

        e.g. ``metadata("age")`` matches traits whose 'age' attribute has a
        non-None value.

        Parameters
        ----------
        metadata_name : str
            Name of the metadata to filter traits with.
        notify : bool, optional
            Whether to notify for changes. Default is to notify.

        Returns
        -------
        new_expression : ObserverExpression
        """
        return self.match(
            filter=MetadataFilter(metadata_name=metadata_name),
            notify=notify,
        )

    def dict_items(self, notify=True, optional=False):
        """ Create a new expression for observing items inside a dict.

        Events emitted (if any) will be instances of
        :class:`~traits.observation.events.DictChangeEvent`.

        If an expression with ``dict_items`` is further extended, the
        **values** of the dict will be given to the next item in the
        expression. For example, the following observes a trait named "number"
        on any object that is one of the values in the dict named "mapping"::

            trait("mapping").dict_items().trait("number")

        Parameters
        ----------
        notify : bool, optional
            Whether to notify for changes. Default is to notify.
        optional : bool, optional
            Whether to ignore this if the upstream object is not a dict.
            Default is false and an error will be raised if the object is not
            a dict.

        Returns
        -------
        new_expression : ObserverExpression
        """
        return self.then(dict_items(notify=notify, optional=optional))

    def list_items(self, notify=True, optional=False):
        """ Create a new expression for observing items inside a list.

        Events emitted (if any) will be instances of
        :class:`~traits.observation.events.ListChangeEvent`.

        e.g. ``trait("containers").list_items()`` for observing mutations
        to a list named ``containers``.

        e.g. ``trait("containers").list_items().trait("value")`` for observing
        the trait ``value`` on any items in the list ``containers``.

        Parameters
        ----------
        notify : bool, optional
            Whether to notify for changes. Default is to notify.
        optional : bool, optional
            Whether to ignore this if the upstream object is not a list.
            Default is false and an error will be raised if the object is not
            a list.

        Returns
        -------
        new_expression : ObserverExpression
        """
        return self.then(list_items(notify=notify, optional=optional))

    def set_items(self, notify=True, optional=False):
        """ Create a new expression for observing items inside a set.

        Events emitted (if any) will be instances of
        :class:`~traits.observation.events.SetChangeEvent`.

        Parameters
        ----------
        notify : bool, optional
            Whether to notify for changes. Default is to notify.
        optional : bool, optional
            Whether to ignore this if the upstream object is not a set.
            Default is false and an error will be raised if the object is not
            a set.

        Returns
        -------
        new_expression : ObserverExpression
        """
        return self.then(set_items(notify=notify, optional=optional))

    def trait(self, name, notify=True, optional=False):
        """ Create a new expression for observing a trait with the exact
        name given.

        Events emitted (if any) will be instances of
        :class:`~traits.observation.events.TraitChangeEvent`.

        Parameters
        ----------
        name : str
            Name of the trait to match.
        notify : bool, optional
            Whether to notify for changes. Default is to notify.
        optional : bool, optional
            If true, skip this observer if the requested trait is not found.
            Default is false, and an error will be raised if the requested
            trait is not found.

        Returns
        -------
        new_expression : ObserverExpression
        """
        return self.then(trait(name=name, notify=notify, optional=optional))

    def _as_graphs(self):
        """ Return all the ObserverGraph for the observer framework to attach
        notifiers.

        This is considered private to the users and to modules outside of the
        ``observation`` subpackage, but public to modules within the
        ``observation`` subpackage.

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


class SingleObserverExpression(ObserverExpression):
    """ Container of ObserverExpression for wrapping a single observer.
    """

    def __init__(self, observer):
        self.observer = observer

    def _create_graphs(self, branches):
        return [
            ObserverGraph(node=self.observer, children=branches),
        ]


class SeriesObserverExpression(ObserverExpression):
    """ Container of ObserverExpression for joining expressions in series.

    Parameters
    ----------
    first : ObserverExpression
        Left expression to be joined in series.
    second : ObserverExpression
        Right expression to be joined in series.
    """

    def __init__(self, first, second):
        self._first = first
        self._second = second

    def _create_graphs(self, branches):
        branches = self._second._create_graphs(branches=branches)
        return self._first._create_graphs(branches=branches)


class ParallelObserverExpression(ObserverExpression):
    """ Container of ObserverExpression for joining expressions in parallel.

    Parameters
    ----------
    left : ObserverExpression
        Left expression to be joined in parallel.
    right : ObserverExpression
        Right expression to be joined in parallel.
    """

    def __init__(self, left, right):
        self._left = left
        self._right = right

    def _create_graphs(self, branches):
        left_graphs = self._left._create_graphs(branches=branches)
        right_graphs = self._right._create_graphs(branches=branches)
        return left_graphs + right_graphs


def join(*expressions):
    """ Convenient function for joining many expressions in series
    using ``ObserverExpression.then``

    Parameters
    ----------
    *expressions : iterable of ObserverExpression

    Returns
    -------
    new_expression : ObserverExpression
        Joined expression.
    """
    return functools.reduce(lambda e1, e2: e1.then(e2), expressions)


def dict_items(notify=True, optional=False):
    """ Create a new expression for observing items inside a dict.

    Events emitted (if any) will be instances of
    :class:`~traits.observation.events.DictChangeEvent`.

    If an expression with ``dict_items`` is further extended, the
    **values** of the dict will be given to the next item in the expression.
    For example, the following observes a trait named "number" on any object
    that is one of the values in the dict named "mapping"::

        trait("mapping").dict_items().trait("number")

    Parameters
    ----------
    notify : bool, optional
        Whether to notify for changes. Default is to notify.
    optional : bool, optional
        Whether to ignore this if the upstream object is not a dict.
        Default is false and an error will be raised if the object is not
        a dict.

    Returns
    -------
    new_expression : ObserverExpression
    """
    observer = DictItemObserver(notify=notify, optional=optional)
    return SingleObserverExpression(observer)


def list_items(notify=True, optional=False):
    """ Create a new expression for observing items inside a list.

    Events emitted (if any) will be instances of
    :class:`~traits.observation.events.ListChangeEvent`.

    e.g. ``trait("containers").list_items()`` for observing mutations
    to a list named ``containers``.

    e.g. ``trait("containers").list_items().trait("value")`` for observing
    the trait ``value`` on any items in the list ``containers``.

    Parameters
    ----------
    notify : bool, optional
        Whether to notify for changes. Default is to notify.
    optional : bool, optional
        Whether to ignore this if the upstream object is not a list.
        Default is false and an error will be raised if the object is not
        a list.

    Returns
    -------
    new_expression : ObserverExpression
    """
    observer = ListItemObserver(notify=notify, optional=optional)
    return SingleObserverExpression(observer)


def match(filter, notify=True):
    """ Create a new expression for observing traits using the
    given filter.

    Events emitted (if any) will be instances of
    :class:`~traits.observation.events.TraitChangeEvent`.

    Parameters
    ----------
    filter : callable(str, CTrait) -> bool
        A callable that receives the name of a trait and the corresponding
        trait definition. The returned bool indicates whether the trait is
        observed. In order to remove an existing observer with the equivalent
        filter, the filter callables must compare equally. The callable must
        also be hashable.
    notify : bool, optional
        Whether to notify for changes.

    Returns
    -------
    new_expression : ObserverExpression
    """
    observer = FilteredTraitObserver(notify=notify, filter=filter)
    return SingleObserverExpression(observer)


def metadata(metadata_name, notify=True):
    """ Return a new expression for observing traits where the given metadata
    is not None.

    Events emitted (if any) will be instances of
    :class:`~traits.observation.events.TraitChangeEvent`.

    e.g. ``metadata("age")`` matches traits whose 'age' attribute has a
    non-None value.

    Parameters
    ----------
    metadata_name : str
        Name of the metadata to filter traits with.
    notify : bool, optional
        Whether to notify for changes. Default is to notify.

    Returns
    -------
    new_expression : ObserverExpression
    """
    return match(
        filter=MetadataFilter(metadata_name=metadata_name),
        notify=notify,
    )


def set_items(notify=True, optional=False):
    """ Create a new expression for observing items inside a set.

    Events emitted (if any) will be instances of
    :class:`~traits.observation.events.SetChangeEvent`.

    Parameters
    ----------
    notify : bool, optional
        Whether to notify for changes. Default is to notify.
    optional : bool, optional
        Whether to ignore this if the upstream object is not a set.
        Default is false and an error will be raised if the object is not
        a set.

    Returns
    -------
    new_expression : ObserverExpression
    """
    observer = SetItemObserver(notify=notify, optional=optional)
    return SingleObserverExpression(observer)


def trait(name, notify=True, optional=False):
    """ Create a new expression for observing a trait with the exact
    name given.

    Events emitted (if any) will be instances of
    :class:`~traits.observation.events.TraitChangeEvent`.

    Parameters
    ----------
    name : str
        Name of the trait to match.
    notify : bool, optional
        Whether to notify for changes. Default is to notify.
    optional : bool, optional
        If true, skip this observer if the requested trait is not found.
        Default is false, and an error will be raised if the requested
        trait is not found.

    Returns
    -------
    new_expression : ObserverExpression
    """
    observer = NamedTraitObserver(
        name=name, notify=notify, optional=optional)
    return SingleObserverExpression(observer)
