# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Module for HasTraits and CTrait specific functions for observers.
"""

from traits.ctraits import CHasTraits
from traits.trait_base import Undefined, Uninitialized
from traits.observers.events._trait_observer_event import trait_event_factory
from traits.observers._exceptions import NotifierNotFound
from traits.observers._observer_change_notifier import ObserverChangeNotifier
from traits.observers._observe import add_or_remove_notifiers
from traits.observers._trait_event_notifier import TraitEventNotifier


#: List of values not to be passed onto the next observers because they are
#: filled values for uninitialized/undefined traits, and no observables
#: can be derived from them.
UNOBSERVABLE_VALUES = [
    Undefined,
    Uninitialized,
    None,
]


def object_has_named_trait(object, name):
    """ Return true if a trait with the given name is defined on the object.

    Parameters
    ----------
    object : any
        Any object
    name : str
        Trait name to look for.

    Returns
    -------
    boolean
    """
    return (
        isinstance(object, CHasTraits) and object._trait(name, 0) is not None
    )


def iter_objects(object, name):
    """ Yield the object referenced by the named trait, unless the value is not
    defined or is one of the few unobservable filled values.

    This function should not introduce side-effect (e.g. evaluating default)
    on the given object.

    Parameters
    ----------
    object : HasTraits
        Object from which the trait value will be obtained.
    name : str
        Name of the trait.

    Yields
    ------
    value : any
        The value of the trait, if it is defined and is not one of those
        skipped values.
    """
    value = object.__dict__.get(name, Undefined)
    if value not in UNOBSERVABLE_VALUES:
        yield value


def get_notifier(handler, target, dispatcher):
    """ Return a notifier for calling the user handler with the
    TraitObserverEvent object representing a trait value change.

    If the old value is uninitialized, then the change is caused by having
    the default value defined. Such an event is prevented from reaching the
    user's change handler.

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
    notifier : TraitEventNotifier
    """
    return TraitEventNotifier(
        handler=handler,
        target=target,
        dispatcher=dispatcher,
        event_factory=trait_event_factory,
        prevent_event=lambda event: event.old is Uninitialized,
    )


def get_maintainer(graph, handler, target, dispatcher):
    """ Return a notifier for maintaining downstream observers when
    a trait is changed.

    All events should be allowed through, including setting default value such
    that downstream observers can be maintained on the new value.

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
        event_factory=trait_event_factory,
        prevent_event=lambda event: False,
        graph=graph,
        handler=handler,
        target=target,
        dispatcher=dispatcher,
    )


def _observer_change_handler(event, graph, handler, target, dispatcher):
    """ Maintain downstream notifiers when the trait changes.

    Parameters
    ----------
    event : TraitObserverEvent
        The event that triggers this function.
    graph : ObserverGraph
        Description for the *downstream* observers, i.e. excluding the observer
        that contributed this maintainer function.
    handler : callable
        User handler.
    target : object
        Object seen by the user as the owner of the observer.
    dispatcher : callable
        Callable for dispatching the handler.
    """
    if event.old not in UNOBSERVABLE_VALUES:
        try:
            add_or_remove_notifiers(
                object=event.old,
                graph=graph,
                handler=handler,
                target=target,
                dispatcher=dispatcher,
                remove=True,
            )
        except NotifierNotFound:
            # The old value could be filled value
            # (e.g. an empty TraitListObject)
            # that does not have any notifier.
            pass

    if event.new not in UNOBSERVABLE_VALUES:
        add_or_remove_notifiers(
            object=event.new,
            graph=graph,
            handler=handler,
            target=target,
            dispatcher=dispatcher,
            remove=False,
        )
