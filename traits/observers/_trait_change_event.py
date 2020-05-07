# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Event object and factory for CTrait change event.
"""


# TraitChangeEvent is exposed in the public API.

class TraitChangeEvent:
    """ Emitted when a trait on a HasTraits object is changed.

    Attributes
    ----------
    object : HasTraits
        Object on which a trait is changed.
    name : str
        Name of the trait.
    old : any
        The old value.
    new : any
        The new value.
    """

    def __init__(self, *, object, name, old, new):
        self.object = object
        self.name = name
        self.old = old
        self.new = new

    def __repr__(self):
        return (
            "<{class_name}("
                "object={object!r}, name={name!r}, old={old!r}, new={new!r}"
            ")>".format(
                class_name=type(self).__name__,
                object=self.object,
                name=self.name,
                old=self.old,
                new=self.new,
            )
        )


def trait_event_factory(object, name, old, new):
    """ Adapt the call signature of ctraits call_notifiers to create an event.

    Parameters
    ----------
    object : HasTraits
        Object on which a trait is changed.
    name : str
        Name of the trait.
    old : any
        The old value.
    new : any
        The new value.

    Returns
    -------
    TraitChangeEvent
    """
    return TraitChangeEvent(object=object, name=name, old=old, new=new)
