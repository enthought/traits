# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!


# SetChangeEvent is in the public API.


class SetChangeEvent:
    """ Event object to represent mutations on a set.

    The interface of this object is provisional as of version 6.1.

    Attributes
    ----------
    object : traits.trait_set_object.TraitSet
        The set being mutated.
    removed : set
        Values removed from the set.
    added : set
        Values added to the set.
    """

    def __init__(self, *, object, removed, added):
        self.object = object
        self.removed = removed
        self.added = added

    def __repr__(self):
        return (
            "{event.__class__.__name__}("
            "object={event.object!r}, "
            "removed={event.removed!r}, "
            "added={event.added!r}"
            ")".format(event=self)
        )


def set_event_factory(trait_set, removed, added):
    """ Adapt the call signature of TraitSet.notify to create an event.

    Parameters
    ----------
    trait_set : traits.trait_set_object.TraitSet
        The set being mutated.
    removed : set
        Values removed from the set.
    added : set
        Values added to the set.

    Returns
    -------
    SetChangeEvent
    """
    return SetChangeEvent(
        object=trait_set, added=added, removed=removed,
    )
