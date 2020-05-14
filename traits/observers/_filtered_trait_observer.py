# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.observers._has_traits_helpers import (
    iter_objects,
    observer_change_handler,
)
from traits.observers._i_observer import IObserver
from traits.observers._observer_change_notifier import ObserverChangeNotifier
from traits.observers._trait_change_event import trait_event_factory
from traits.observers._trait_event_notifier import TraitEventNotifier
from traits.trait_base import Uninitialized


@IObserver.register
class FilteredTraitObserver:
    """ An observer for observing traits using a custom filter.

    Parameters
    ----------
    notify : boolean
        Whether to notify for changes.
    filter : callable(str, CTrait) -> boolean
        A callable that receives the name of a trait and the corresponding
        trait definition. The returned boolean indicates whether the trait is
        observed. In order to remove an existing observer with the equivalent
        filter, the filter callables must compare equally.
    """

    def __init__(self, notify, filter):
        self.notify = notify
        self.filter = filter

    def __hash__(self):
        """ Return a hash of this object."""
        return hash((type(self), self.notify, self.filter))

    def __eq__(self, other):
        """ Return true if this observer is equal to the given one."""
        return (
            type(self) is type(other)
            and self.notify == other.notify
            and self.filter == other.filter
        )

    def iter_observables(self, object):
        """ Yield the instance traits matching the filter given. If trait
        definition cannot be found on the object, raise an error.

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
        try:
            name_to_ctrait = object.traits()
        except AttributeError:
            raise ValueError(
                "Unable to obtain trait definitions from {!r}".format(object)
            )

        for name, ctrait in name_to_ctrait.items():
            if self.filter(name, ctrait):
                yield object._trait(name, 2)

    def iter_objects(self, object):
        """ Yield the values of the traits that match the given filter. The
        values will be given to the next observer(s) following this one in an
        ObserverGraph.

        If a value has not been set as an instance attribute, i.e. absent in
        ``object.__dict__``, this observer will skip it. This is to avoid
        evaluating default initializers while adding observers. When the
        default is defined, a change event will trigger the maintainer to
        add/remove notifiers for the next observers.

        Note that ``Undefined``, ``Uninitialized`` and ``None`` values are also
        skipped, as they are unavoidable filled values that contain no further
        attributes to be observed by any other observers.

        Parameters
        ----------
        object: object
            Object provided by the ``iter_objects`` methods from another
            observers or directly by the user.

        Yields
        ------
        value : object
        """
        try:
            name_to_ctrait = object.traits()
        except AttributeError:
            raise ValueError(
                "Unable to obtain trait definitions from {!r}".format(object)
            )

        for name, ctrait in name_to_ctrait.items():
            if self.filter(name, ctrait):
                yield from iter_objects(object, name)

    def get_notifier(self, handler, target, dispatcher):
        """ Return a notifier for calling the user handler with the change
        event.

        If the old value is uninitialized, then the change is caused by having
        the default value defined. Such an event is prevented from reaching the
        user's change handler.

        Returns
        -------
        notifier : TraitEventNotifier
        """
        return TraitEventNotifier(
            handler=handler,
            target=target,
            dispatcher=dispatcher,
            event_factory=trait_event_factory,
            prevent_event=lambda event: event.old is Uninitialized,
        )

    def get_maintainer(self, graph, handler, target, dispatcher):
        """ Return a notifier for maintaining downstream observers when
        a trait is changed.

        All events should be allowed through, including setting default value
        such that downstream observers can be maintained on the new value.

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
            observer_handler=observer_change_handler,
            event_factory=trait_event_factory,
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
        # This will yield a new ObserverGraph with an observer specialized in
        # observing trait_added event.
        # enthought/traits#1077
        yield from ()
