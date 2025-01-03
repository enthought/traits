# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Event object for representing mutations to a dict.
"""

# DictChangeEvent is exposed in the public API


class DictChangeEvent:
    """ Event object to represent mutations on a dict.

    Note that the API is different from the ``TraitDictEvent`` emitted via the
    "*name* _items" trait. In particular, the attribute ``changed`` is not
    defined here.

    The interface of this object is provisional as of version 6.1.

    Attributes
    ----------
    object : traits.trait_dict_object.TraitDict
        The dict being mutated.
    removed : dict
        Keys and values for removed or updated items.
        If keys are found in ``added`` as well, they refer to updated items
        and the values are old.
    added : dict
        Keys and values for added or updated items.
        If keys are found in ``removed`` as well, they refer to updated items
        and the values are new.
    """

    def __init__(self, *, object, removed, added):
        self.object = object
        self.removed = removed
        self.added = added

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"object={self.object!r}, "
            f"removed={self.removed!r}, "
            f"added={self.added!r})"
        )


def dict_event_factory(trait_dict, removed, added, changed):
    """ Adapt the call signature of TraitDict.notify to create an event.

    Parameters
    ----------
    trait_dict : traits.trait_dict_object.TraitDict
        The dict being mutated.
    removed : dict
        Items removed from the dict
    added : dict
        Items added to the dict
    changed : dict
        Old values for items updated on the dict.

    Returns
    -------
    DictChangeEvent
    """
    # See enthought/traits#1031 for changing the signature of TraitDict.notify
    # instead.
    removed = removed.copy()
    removed.update(changed)
    for key in changed:
        added[key] = trait_dict[key]
    return DictChangeEvent(
        object=trait_dict, added=added, removed=removed,
    )
