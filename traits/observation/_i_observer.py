# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import abc


class IObserver(abc.ABC):
    """ Interface for all observers.

    Each instance of ``IObserver`` can be a node in the
    ``ObserverGraph``. These objects are considered
    low-level objects not to be instantiated directly by the
    user. In order to support equality and hashing on the
    ``ObserverGraph``, ``IObserver`` needs to be hashable
    and it needs to support comparison for equality.

    A subclass of ``IObserver`` is often context specific, e.g. for observing
    a trait on an HasTraits instance, for observing items in a list, etc.

    Given an ``ObserverGraph``, observers are visited from the root node
    to the leaf nodes. The first observer (root node) will be given the object
    the user wants to observe. It knows how to obtain observable(s) for
    attaching notifiers. It also knows what objects should be given to the
    downstream/children observers in the same graph.

    An observer defines the notifier that wraps the user change handler, should
    notification is enabled by the user. This allows the observer to define
    how the user should receive the change event, e.g. what type of event
    object should be created, and whether a given event should be silenced etc.

    An observer also defines a "maintainer" (which is also a notifier from the
    point of view of an observable), for maintaining downstream observers when
    a change happens for an observable. For example, an observerable may not
    have a defined value yet for the children observers to handle. When the
    value is defined, the observable is expected to notify the maintainer,
    which will pass the new value onto the children observers.

    An observer can also contribute more ``ObserverGraph`` via
    ``iter_extra_graphs`` if they require support from other observers.
    """

    def __hash__(self):
        """ Return a hash of this object."""
        raise NotImplementedError("__hash__ must be implemented.")

    def __eq__(self, other):
        """ Return true if this observer is equal to the given one."""
        raise NotImplementedError("__eq__ must be implemented.")

    @property
    def notify(self):
        """ A boolean for whether this observer will notify for changes.
        """
        raise NotImplementedError("notify property must be implemented.")

    def iter_observables(self, object):
        """ Yield observables for adding or removing notifiers.

        The notifiers are contributed by this observer's ``get_notifier``
        and ``get_maintainer`` methods.

        An observer may observe many items, e.g. multiple traits for a given
        instance of HasTraits, then the observer will yield many items here.

        An observer may also observe just one thing, e.g. a single trait, or an
        instance of TraitListObject, then the observer may yield just that.

        An observer may also find nothing to be observed and does not need to
        complain about that, and it will yield nothing here.

        Observers are allowed to raise here if it is appropriate to do so,
        e.g. to help catch usage errors.

        Parameters
        ----------
        object: object
            Object provided by the ``iter_objects`` methods from another
            observers or directly by the user.
            No guarantee can be made about the type of the object.
            Concrete implementations should do the sanity check where
            appropriate.

        Yields
        ------
        IObservable
        """
        raise NotImplementedError("iter_observables must be implemented.")

    def iter_objects(self, object):
        """ Yield objects for the next observer following this observer, in an
        ObserverGraph.

        An observer may yield many items for the next observer, e.g. the
        observer is observing many traits on the given instance of HasTraits
        or the observer is observing items in a container. The observer can
        evaluate whether the value is appropriate to be passed on, or skip some
        if the observer is expected to do so.

        An observer may yield one item if that is what should be passed onto
        the next observer.

        An observer may find nothing to be passed onto the next observer, and
        has no need to complain about that. Then the observer may yield
        nothing.

        Observers are allowed to raise here if it is appropriate to do so,
        e.g. to help catch usage errors.

        Parameters
        ----------
        object: object
            Object provided by the ``iter_objects`` methods from another
            observers or directly by the user.
            No guarantee can be made about the type of the object.
            Concrete implementations should do the sanity check where
            appropriate.

        Yields
        ------
        value : object
        """
        raise NotImplementedError("iter_objects must be implemented.")

    def get_notifier(self, handler, target, dispatcher):
        """ Return a notifier for calling the user handler with the change
        event. This is needed if ``notify`` is true.

        Parameters
        ----------
        handler : callable
            User handler.
        target : object
            Object seen by the user as the owner of the observer.
        dispatcher : callable
            Callable for dispatching the handler.

        Returns
        -------
        notifier : INotifier
        """
        raise NotImplementedError("get_notifier must be implemented.")

    def get_maintainer(self, graph, handler, target, dispatcher):
        """ Return a notifier for maintaining downstream observers in an
        ObserverGraph, when the object observed by this observer changes.

        Parameters
        ----------
        graph : ObserverGraph
            Description for the *downstream* observers, i.e. excluding self.
        handler : callable
            User handler.
        target : object
            Object seen by the user as the owner of the observer.
        dispatcher : callable
            Callable for dispatching the handler.

        Returns
        -------
        notifier : INotifier
        """
        raise NotImplementedError("get_maintainer must be implemented.")

    def iter_extra_graphs(self, graph):
        """ Yield additional ObserverGraph for adding/removing notifiers when
        this observer is encountered in a given ObserverGraph.

        If an observer needs support from another observer(s), e.g.
        for observing 'trait_added' event, then this method can yield any
        number of ObserverGraph containing those additional observer(s).

        If an observer does not need additional support from other observers,
        this method can yield nothing.

        Parameters
        ----------
        graph : ObserverGraph
            The graph where this observer is the root node.

        Yields
        ------
        graph : ObserverGraph
        """
        raise NotImplementedError("iter_extra_graphs must be implemented.")
