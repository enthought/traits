# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Module for HasTraits and CTrait specific utility functions for observers.
"""

from traits.constants import ComparisonMode, TraitKind
from traits.ctraits import CHasTraits
from traits.observation._observe import add_or_remove_notifiers
from traits.observation.exceptions import NotifierNotFound
from traits.trait_base import Undefined, Uninitialized


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
    if all(value is not skipped for skipped in UNOBSERVABLE_VALUES):
        yield value


def observer_change_handler(event, graph, handler, target, dispatcher):
    """ Maintain downstream notifiers when the trait changes.

    Parameters
    ----------
    event : TraitChangeEvent
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
    if all(event.old is not skipped for skipped in UNOBSERVABLE_VALUES):
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
            # The old value could be a default value that does not have any
            # notifier.
            pass

    if all(event.new is not skipped for skipped in UNOBSERVABLE_VALUES):
        add_or_remove_notifiers(
            object=event.new,
            graph=graph,
            handler=handler,
            target=target,
            dispatcher=dispatcher,
            remove=False,
        )


def ctrait_prevent_event(event):
    """ Return true if the CTrait change event should be skipped.

    Parameters
    ----------
    event : TraitChangeEvent

    Returns
    -------
    skipped : bool
        Whether the event should be skipped
    """
    if event.old is Uninitialized:
        return True

    ctrait = event.object.trait(event.name)
    if (ctrait.type == TraitKind.trait.name
            and ctrait.comparison_mode == ComparisonMode.equality):
        try:
            return bool(event.old == event.new)
        except Exception:
            # Maybe do something else about the exception
            # enthought/traits#1230
            pass
    return False
