# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.observation._trait_change_event import trait_event_factory
from traits.observation._has_traits_helpers import (
    ctrait_prevent_event,
    iter_objects,
    object_has_named_trait,
    observer_change_handler,
)
from traits.observation._i_observer import IObserver
from traits.observation._observer_change_notifier import ObserverChangeNotifier
from traits.observation._observer_graph import ObserverGraph
from traits.observation._trait_added_observer import TraitAddedObserver
from traits.observation._trait_event_notifier import TraitEventNotifier


@IObserver.register
class NamedTraitObserver:
    """ Observer for observing changes on a named trait
    on an instance of HasTraits.
    """

    __slots__ = ("name", "notify", "optional")

    def __init__(self, *, name, notify, optional):
        """ Initializer.
        Once this observer is defined, it should not be mutated.

        Parameters
        ----------
        name : str
            Name of the trait to be observed.
        notify : boolean
            Whether to notify for changes.
        optional : boolean
            If true and if the incoming object is not an instance of HasTraits
            or does not have a trait with the given name, this observer will
            quietly skip it. Otherwise, this observer will raise an error if
            the named trait cannot be found. Useful if the named trait is
            added after a handler is registered, or when the context is
            ambiguous (e.g. "items" in the domain specific language).
        """
        self.name = name
        self.notify = notify
        self.optional = optional

    def __hash__(self):
        return hash(
            (type(self).__name__, self.name, self.notify, self.optional)
        )

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and self.name == other.name
            and self.notify == other.notify
            and self.optional == other.optional
        )

    def __repr__(self):
        formatted_args = [
            f"name={self.name!r}",
            f"notify={self.notify!r}",
            f"optional={self.optional!r}",
        ]
        return f"{self.__class__.__name__}({', '.join(formatted_args)})"

    def iter_observables(self, object):
        """ Yield the named instance trait from the given object. If the named
        trait cannot be found and optional is false, raise an error.

        Parameters
        ----------
        object: object
            Object provided by another observers or by the user.

        Yields
        ------
        CTrait

        Raises
        ------
        ValueError
            If the trait is not found and optional flag is set to false.
        """
        if not object_has_named_trait(object, self.name):
            if self.optional:
                return
            raise ValueError(
                "Trait named {!r} not found on {!r}.".format(self.name, object)
            )
        yield object._trait(self.name, 2)

    def iter_objects(self, object):
        """ Yield the value of the named trait from the given object, if the
        value is defined. The value will then be given to the next observer(s)
        following this one in an ObserverGraph.

        If the value has not been set as an instance attribute, i.e. absent in
        ``object.__dict__``, this observer will yield nothing. This is to avoid
        evaluating default initializers while adding observers. When the
        default is defined, a change event will trigger the maintainer to
        add/remove notifiers for the next observers.

        Note that ``Undefined``, ``Uninitialized`` and ``None`` values are also
        skipped, as they are inevitable filled values that contain no further
        attributes to be observed by any other observers.

        Parameters
        ----------
        object: HasTraits
            Expected to be an instance of HasTraits

        Yields
        ------
        value : any

        Raises
        ------
        ValueError
            If the trait is not found and optional flag is set to false.
        """
        if not object_has_named_trait(object, self.name):
            if self.optional:
                return
            raise ValueError(
                "Trait named {!r} not found on {!r}.".format(self.name, object)
            )
        yield from iter_objects(object, self.name)

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
            prevent_event=ctrait_prevent_event,
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
        """ Yield additional ObserverGraph for adding/removing notifiers when
        this observer is encountered in a given ObserverGraph.

        Parameters
        ----------
        graph : ObserverGraph
            The graph where this observer is the root node.

        Yields
        ------
        graph : ObserverGraph
        """
        yield ObserverGraph(
            node=TraitAddedObserver(
                match_func=lambda name, trait: name == self.name,
                optional=self.optional,
            ),
            children=[graph],
        )
