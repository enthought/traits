# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.observation._i_observer import IObserver
from traits.observation._observe import add_or_remove_notifiers
from traits.observation._observer_change_notifier import ObserverChangeNotifier
from traits.observation._set_change_event import set_event_factory
from traits.observation._trait_event_notifier import TraitEventNotifier
from traits.trait_set_object import TraitSet


@IObserver.register
class SetItemObserver:
    """ Observer for observing mutations on a set.

    Parameters
    ----------
    notify : boolean
        Whether to notify for changes.
    optional : boolean
        If False, this observer will complain if the incoming object is not
        an observable set. If True and the incoming object is not a set, this
        observer will do nothing. Useful for the 'items' keyword in the text
        parser, where the source container type is ambiguous.
    """

    def __init__(self, *, notify, optional):
        self.notify = notify
        self.optional = optional

    def __hash__(self):
        """ Return a hash of this object."""
        return hash((type(self).__name__, self.notify, self.optional))

    def __eq__(self, other):
        """ Return true if this observer is equal to the given one."""
        return (
            type(self) is type(other)
            and self.notify == other.notify
            and self.optional == other.optional
        )

    def iter_observables(self, object):
        """ If the given object is an observable set, yield that set.
        Otherwise, raise an error, unless this observer is optional

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
            If the given object is not an observable set and optional is false.
        """
        if not isinstance(object, TraitSet):
            if self.optional:
                return
            raise ValueError(
                "Expected a TraitSet to be observed, "
                "got {!r} (type: {!r})".format(object, type(object))
            )

        yield object

    def iter_objects(self, object):
        """ Yield the content of the set if the given object is an observable
        set. Otherwise, raise an error, unless the observer is optional.

        The content of the set will be passed onto the children observer(s)
        following this one in an ObserverGraph.

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
            If the given object is not an observable set and optional is false.
        """
        if not isinstance(object, TraitSet):
            if self.optional:
                return
            raise ValueError(
                "Expected a TraitSet to be observed, "
                "got {!r} (type: {!r})".format(object, type(object))
            )

        yield from object

    def get_notifier(self, handler, target, dispatcher):
        """ Return a notifier for calling the user handler with the change
        event.

        Returns
        -------
        notifier : TraitEventNotifier
        """
        return TraitEventNotifier(
            handler=handler,
            target=target,
            dispatcher=dispatcher,
            event_factory=set_event_factory,
            prevent_event=lambda event: False,
        )

    def get_maintainer(self, graph, handler, target, dispatcher):
        """ Return a notifier for maintaining downstream observers when
        a set is mutated.

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
            event_factory=set_event_factory,
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

    Parameters
    ----------
    event : SetChangeEvent
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
