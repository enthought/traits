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
    trait_set : set
        The set being mutated.
    added : set
        Values added to the set.
    removed : set
        Values removed from the set.
    """

    def __init__(self, *, trait_set, added, removed):
        self.trait_set = trait_set
        self.added = added
        self.removed = removed

    def __repr__(self):
        return (
            "<{class_name}("
            "trait_set={trait_set!r}, "
            "added={added!r}, "
            "removed={removed!r}"
            ")>".format(
                class_name=type(self).__name__,
                trait_set=self.trait_set,
                added=self.added,
                removed=self.removed,
            )
        )


def set_event_factory(trait_set, removed, added):
    """ Adapt the call signature of TraitSet.notify to create an event.

    Parameters
    ----------
    trait_set : set
        The set being mutated.
    removed : set
        The items that have been removed.
    added : set
        The new items that have been added to the set.

    Returns
    -------
    SetChangeEvent
    """
    return SetChangeEvent(
        trait_set=trait_set,
        added=added,
        removed=removed,
    )