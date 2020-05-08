# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Event object for representing mutations to a list.
"""

# ListChangeEvent is exposed in the public API

class ListChangeEvent:
    """ Event object to represent mutations to a list.

    Attributes
    ----------
    trait_list : list
        The list being mutated.
    index : int or slice
        The index used for the mutation.
    added : list
        Values added to the list.
    removed : list
        Values removed from the list.
    """

    def __init__(self, *, trait_list, index, removed, added):
        self.trait_list = trait_list
        self.added = added
        self.removed = removed
        self.index = index

    def __repr__(self):
        return (
            "<ListChangeEvent("
            "trait_list={trait_list!r}, "
            "index={index!r}, "
            "removed={removed!r}, "
            "added={added!r}"    # no trailing comma here.
            ")>".format(
                trait_list=self.trait_list,
                index=self.index,
                removed=self.removed,
                added=self.added,
            )
        )


def list_event_factory(trait_list, index, removed, added):
    """ Adapt the call signature of TraitList.notify to create an event.

    Parameters
    ----------
    trait_list : TraitList
        TraitList object being mutated.
    index : int or slice
        The indices being modified by the operation.
    removed : list
        The items to be removed.
    added : list
        The items being added to the list.

    Returns
    -------
    ListChangeEvent
    """
    return ListChangeEvent(
        trait_list=trait_list,
        index=index,
        removed=removed,
        added=added,
    )
