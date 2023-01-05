# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
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

    The interface of this object is provisional as of version 6.1.

    Attributes
    ----------
    object : traits.trait_list_object.TraitList
        The list being mutated.
    index : int or slice
        The index used for the mutation.
    added : list
        Values added to the list.
    removed : list
        Values removed from the list.
    """

    def __init__(self, *, object, index, removed, added):
        self.object = object
        self.added = added
        self.removed = removed
        self.index = index

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"object={self.object!r}, "
            f"index={self.index!r}, "
            f"removed={self.removed!r}, "
            f"added={self.added!r})"
        )


def list_event_factory(trait_list, index, removed, added):
    """ Adapt the call signature of TraitList.notify to create an event.

    Parameters
    ----------
    trait_list : traits.trait_list_object.TraitList
        TraitList object being mutated.
    index : int or slice
        The indices being modified by the operation.
    removed : list
        The items removed from the list.
    added : list
        The items added to the list.

    Returns
    -------
    ListChangeEvent
    """
    return ListChangeEvent(
        object=trait_list, index=index, removed=removed, added=added,
    )
