# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.observers._list_change_event import list_event_factory
from traits.observers._i_observer import IObserver
from traits.observers._trait_event_notifier import TraitEventNotifier
from traits.observers._observe import add_or_remove_notifiers
from traits.observers._observer_change_notifier import ObserverChangeNotifier
from traits.trait_list_object import TraitList


@IObserver.register
class ListItemObserver:
    """ Observer for observing mutations on a list.

    Parameters
    ----------
    notify : boolean
        Whether to notify for changes.
    optional : boolean
        If False, this observer will complain if the incoming object is not
        an observable list. If True and the incoming object is not a list, this
        observer will do nothing. Useful for the 'items' keyword in the text
        parser, where the source container type is ambiguous.
    """

    def __init__(self, *, notify, optional):
        self._notify = notify
        self._optional = optional

    def __hash__(self):
        """ Return a hash of this object."""
        return hash((type(self), self.notify))

    def __eq__(self, other):
        """ Return true if this observer is equal to the given one."""
        return (
            type(self) is type(other)
            and self.notify == other.notify
            and self.optional == other.optional
        )

    @property
    def notify(self):
        """ A boolean for whether this observer will notify
        for changes.
        """
        return self._notify

    @property
    def optional(self):
        """ A boolean for whether this observer is optional when the incoming
        object is not a list.
        """
        return self._optional

    def iter_observables(self, object):
        """ If the given object is an observable list, yield that list.
        Otherwise, raise an error unless the observer is optional.

        Parameters
        ----------
        object: object
            Object provided by another observers or by the user.

        Yields
        ------
        IObservable

        Raises
        ------
        ValueError
            If the given object is not a list.
        """
        if not isinstance(object, TraitList):
            if self.optional:
                return
            raise ValueError(
                "Expected a TraitList to be observed, "
                "got {!r} (type: {!r})".format(object, type(object)))
        yield object

    def iter_objects(self, object):
        """ Yield the content of the list if the given object is an observable
        list. Otherwise, raise an error, unless the observer is optional.

        The content of the list will be passed onto the next observer following
        this one in an ObserverGraph.

        Parameters
        ----------
        object: object
            Object provided by another observers or by the user.

        Yields
        ------
        value : object

        Raises
        ------
        ValueError
            If the given object is not a list.
        """
        if not isinstance(object, TraitList):
            if self.optional:
                return
            raise ValueError(
                "Expected a TraitList to be observed, "
                "got {!r} (type: {!r})".format(object, type(object)))

        yield from object

    def get_notifier(self, handler, target, dispatcher):
        """ Return a notifier for calling the user handler with the change
        event.

        Returns
        -------
        notifier : TraitEventNotifier
        """
        # Unlike CTrait, when default list is created, there isn't a change
        # event where the old value is Uninitialized.
        return TraitEventNotifier(
            handler=handler,
            target=target,
            dispatcher=dispatcher,
            event_factory=list_event_factory,
            prevent_event=lambda event: False,
        )

    def get_maintainer(self, graph, handler, target, dispatcher):
        """ Return a notifier for maintaining downstream observers when
        a list is mutated.

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
            observer_handler=_observer_change_handler,
            event_factory=list_event_factory,
            prevent_event=lambda event: False,
            graph=graph,
            handler=handler,
            target=target,
            dispatcher=dispatcher,
        )

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
        # Unlike CTrait, no need to handle trait_added
        yield from ()


def _observer_change_handler(event, graph, handler, target, dispatcher):
    """ Handler for maintaining observers. Used by ObserverChangeNotifier.

    The downstream notifiers are removed from items removed from the list.
    Likewise, downstream notifiers are added to items added to the list.

    Parameters
    ----------
    event : ListChangeEvent
        Change event that triggers the maintainer.
    graph : ObserverGraph
        Description for the *downstream* observers, i.e. excluding self.
    handler : callable
        User handler.
    target : object
        Object seen by the user as the owner of the observer.
    dispatcher : callable
        Callable for dispatching the handler.
    """
    for removed_item in event.removed:
        add_or_remove_notifiers(
            object=removed_item,
            graph=graph,
            handler=handler,
            target=target,
            dispatcher=dispatcher,
            remove=True,
        )
    for added_item in event.added:
        add_or_remove_notifiers(
            object=added_item,
            graph=graph,
            handler=handler,
            target=target,
            dispatcher=dispatcher,
            remove=False,
        )
