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

    Attributes
    ----------
    trait_set : traits.trait_set_object.TraitSet
        The set being mutated.
    removed : set
        Values removed from the set.
    added : set
        Values added to the set.
    """

    def __init__(self, *, trait_set, removed, added):
        self.trait_set = trait_set
        self.removed = removed
        self.added = added

    def __repr__(self):
        return (
            "{event.__class__.__name__}("
            "trait_set={event.trait_set!r}, "
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
        trait_set=trait_set, added=added, removed=removed,
    )
