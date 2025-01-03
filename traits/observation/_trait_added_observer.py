# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.observation._has_traits_helpers import (
    iter_objects,
    object_has_named_trait,
)
from traits.observation._i_observer import IObserver
from traits.observation._observe import add_or_remove_notifiers
from traits.observation._observer_change_notifier import ObserverChangeNotifier
from traits.observation._observer_graph import ObserverGraph
from traits.observation._trait_change_event import trait_event_factory


@IObserver.register
class TraitAddedObserver:
    """ An observer for observing the trait_added event.

    This observer only offers the "maintainer". When this observer is used in
    an ObserverGraph, its subgraphs are the graphs to be hooked up when a new
    trait is added, provided that the trait satisfies a given criterion.
    The criterion should align with the root observer(s) in these subgraph(s).

    Parameters
    ----------
    match_func : callable(str, CTrait) -> bool
        A callable that receives the name of the trait added and the
        corresponding trait. The returned boolean indicates whether
        notifiers should be added/removed for the added trait.
        This callable is used for equality check and must be hashable.
    optional : boolean
        Whether to skip this observer if the trait_added trait cannot be
        found on the incoming object.
    """

    def __init__(self, match_func, optional):
        self.match_func = match_func
        self.optional = optional

    def __hash__(self):
        """ Return a hash of this object."""
        return hash((type(self).__name__, self.match_func, self.optional))

    def __eq__(self, other):
        """ Return true if this observer is equal to the given one."""
        return (
            type(self) is type(other)
            and self.match_func == other.match_func
            and self.optional == other.optional
        )

    @property
    def notify(self):
        """ A boolean for whether this observer will notify for changes.
        """
        return False

    def iter_observables(self, object):
        """ Yield observables for notifiers to be attached to or detached from.

        Parameters
        ----------
        object: object
            Object provided by the ``iter_objects`` methods from another
            observers or directly by the user.

        Yields
        ------
        IObservable

        Raises
        ------
        ValueError
            If the given object cannot be handled by this observer.
        """
        if not object_has_named_trait(object, "trait_added"):
            if self.optional:
                return
            raise ValueError(
                "Unable to observe 'trait_added' event on {!r}".format(object))
        yield object._trait("trait_added", 2)

    def iter_objects(self, object):
        """ Yield objects for the next observer following this observer, in an
        ObserverGraph.

        Parameters
        ----------
        object: object
            Object provided by the ``iter_objects`` methods from another
            observers or directly by the user.

        Yields
        ------
        value : object
        """
        # children graphs are used in the maintainer only.
        yield from ()

    # get_notifier is not implemented as notify is always false.

    def get_maintainer(self, graph, handler, target, dispatcher):
        """ Return a notifier for maintaining downstream observers when
        trait_added event happens.

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
        notifier : ObserverChangeNotifier
        """
        return ObserverChangeNotifier(
            observer_handler=self.observer_change_handler,
            event_factory=trait_event_factory,
            prevent_event=self.prevent_event,
            graph=graph,
            handler=handler,
            target=target,
            dispatcher=dispatcher,
        )

    def prevent_event(self, event):
        """ Return true if the added trait should not be handled.

        Parameters
        ----------
        event : TraitChangeEvent
            Event triggered by add_trait.
        """
        object = event.object
        name = event.new
        trait = object.trait(name=name)
        return not self.match_func(name, trait)

    @staticmethod
    def observer_change_handler(event, graph, handler, target, dispatcher):
        """ Handler for maintaining observers.

        Parameters
        ----------
        event : TraitChangeEvent
            Event triggered by add_trait.
        graph : ObserverGraph
            Description for the *downstream* observers, i.e. excluding self.
        handler : callable
            User handler.
        target : object
            Object seen by the user as the owner of the observer.
        dispatcher : callable
            Callable for dispatching the handler.
        """
        new_graph = ObserverGraph(
            node=_RestrictedNamedTraitObserver(
                name=event.new,
                wrapped_observer=graph.node,
            ),
            children=graph.children
        )
        add_or_remove_notifiers(
            object=event.object,
            graph=new_graph,
            handler=handler,
            target=target,
            dispatcher=dispatcher,
            remove=False,
        )
        # There is no mirrored action to this.
        # ``remove_trait`` does not fire a change event.
        # see enthought/traits#1047

    def iter_extra_graphs(self, graph):
        """ Yield new ObserverGraph to be contributed by this observer.

        Parameters
        ----------
        graph : ObserverGraph
            The graph this observer is part of.

        Yields
        ------
        ObserverGraph
        """
        yield from ()


@IObserver.register
class _RestrictedNamedTraitObserver:
    """ An observer to support TraitAddedObserver in order to add
    notifiers for one specific named trait. The notifiers should be
    contributed by the original observer.

    Parameters
    ----------
    name : str
        Name of the trait to be observed.
    wrapped_observer : IObserver
        The observer from which notifers are obtained.
    """

    def __init__(self, name, wrapped_observer):
        self.name = name
        self._wrapped_observer = wrapped_observer

    def __hash__(self):
        return hash((type(self), self.name, self._wrapped_observer))

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and self.name == other.name
            and self._wrapped_observer == other._wrapped_observer
        )

    @property
    def notify(self):
        """ A boolean for whether this observer will notify for changes. """
        return self._wrapped_observer.notify

    def iter_observables(self, object):
        """ Yield only the observable for the named trait."""
        yield object._trait(self.name, 2)

    def iter_objects(self, object):
        """ Yield only the value for the named trait."""
        yield from iter_objects(object, self.name)

    def get_notifier(self, handler, target, dispatcher):
        """ Return the notifier from the wrapped observer."""
        return self._wrapped_observer.get_notifier(handler, target, dispatcher)

    def get_maintainer(self, graph, handler, target, dispatcher):
        """ Return the maintainer from the wrapped observer."""
        return self._wrapped_observer.get_maintainer(
            graph, handler, target, dispatcher)

    def iter_extra_graphs(self, graph):
        yield from ()
