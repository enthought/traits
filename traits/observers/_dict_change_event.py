# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
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


class DictChangeEvent:
    """ Event object to represent mutations on a dict.

    Attributes
    ----------
    trait_dict : dict
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

    def __init__(self, *, trait_dict, removed, added):
        self.trait_dict = trait_dict
        self.removed = removed
        self.added = added

    def __repr__(self):
        return (
            "<{class_name}("
            "trait_dict={trait_dict!r}, "
            "removed={removed!r}"
            "added={added!r}, "
            ")>".format(
                class_name=type(self).__name__,
                trait_dict=self.trait_dict,
                added=self.added,
                removed=self.removed,
            )
        )


def dict_event_factory(trait_dict, removed, added, changed):
    """ Adapt the call signature of TraitDict.notify to create an event.

    Parameters
    ----------
    trait_dict : TraitDict
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
        trait_dict=trait_dict, added=added, removed=removed,
    )
