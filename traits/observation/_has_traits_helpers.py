# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
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

import warnings

from traits.constants import ComparisonMode
from traits.ctraits import CHasTraits
from traits.observation._exceptions import NotifierNotFound
from traits.observation._observe import add_or_remove_notifiers
from traits.trait_base import Undefined, Uninitialized
from traits.trait_types import Dict, List, Set


#: List of values not to be passed onto the next observers because they are
#: filled values for uninitialized/undefined traits, and no observables
#: can be derived from them.
UNOBSERVABLE_VALUES = [
    Undefined,
    Uninitialized,
    None,
]


def _has_container_trait(ctrait):
    """ Return true if the CTrait trait type contains container trait
    at the top-level.

    Parameters
    ----------
    ctrait : CTrait
    """
    container_types = (Dict, List, Set)
    is_container = ctrait.is_trait_type(container_types)
    if is_container:
        return True
    # Try inner traits, e.g. to support Union
    return any(
        trait.is_trait_type(container_types)
        for trait in ctrait.inner_traits
    )


def warn_comparison_mode(object, name):
    """ Check if the trait is a Dict/List/Set with comparison_mode set to
    equality (or higher). If so, warn about the fact that observers will be
    lost in the event of reassignment.

    Parameters
    ----------
    object : HasTraits
        Object where a trait is defined
    name : str
        Name of a trait to check if warning needs to be issued for it.
    """
    ctrait = object.traits()[name]

    if (not ctrait.is_property
            and _has_container_trait(ctrait)
            and ctrait.comparison_mode == ComparisonMode.equality):
        warnings.warn(
            "Trait {name!r} (trait type: {trait_type}) on class {class_name} "
            "is defined with comparison_mode={current_mode!r}. "
            "Mutations and extended traits cannot be observed if a new "
            "container compared equally to the old one is set. Redefine the "
            "trait with {trait_type}(..., comparison_mode={new_mode!r}) "
            "to avoid this.".format(
                name=name,
                class_name=object.__class__.__name__,
                current_mode=ctrait.comparison_mode,
                trait_type=ctrait.trait_type.__class__.__name__,
                new_mode=ComparisonMode.identity,
            ),
            RuntimeWarning,
        )


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
    warn_comparison_mode(object, name)
    value = object.__dict__.get(name, Undefined)
    if value not in UNOBSERVABLE_VALUES:
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
            # The old value could be a default value that does not have any
            # notifier.
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
