# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Utility routines that convert objects to CTrait instances

Most of these functions depend on objects having an informal ``as_ctrait``
interface if they know how to turn themselves into a CTrait instance.

We need to special-case ``TraitType`` subclasses so that we can use them
in trait definitions without needing to call them, eg.::

    x = Float

rather than::

    x = Float()

To handle this, there is another informal interface with the deliberately
unwieldy classmethod name ``instantiate_and_get_ctrait``.
"""


def trait_cast(obj):
    """ Convert to a CTrait if the object knows how, else return None.
    """
    try:
        return as_ctrait(obj)
    except TypeError:
        return None


def as_ctrait(obj):
    """ Convert to CTrait if the object knows how, else raise TraitError.

    Parameters
    ----------
    obj
        An object that supports conversion to `CTrait`. Refer
        documentation for when the object supports this conversion.

    Returns
    -------
    ctrait.CTrait
        A CTrait object.

    Raises
    ------
    TypeError
        If the object does not support conversion to CTrait.
    """
    if isinstance(obj, type) and hasattr(obj, 'instantiate_and_get_ctrait'):
        return obj.instantiate_and_get_ctrait()
    elif not isinstance(obj, type) and hasattr(obj, 'as_ctrait'):
        return obj.as_ctrait()
    else:
        raise TypeError(
            "Object {!r} does not support conversion to CTrait".format(obj))


def check_trait(trait):
    """ Returns either the original value or a valid CTrait if the value can be
        converted to a CTrait.
    """
    try:
        return as_ctrait(trait)
    except TypeError:
        return trait


#: alias for check_trait
try_trait_cast = check_trait


def trait_from(obj):
    """ Returns a trait derived from its input.
    """
    from .trait_types import Any
    from .traits import Trait

    # special-case None
    if obj is None:
        return Any().as_ctrait()

    try:
        return as_ctrait(obj)
    except TypeError:
        return Trait(obj)


def trait_for(trait):
    """ Returns the trait corresponding to a specified value.
    """
    # XXX this is the same as trait_from except that None is treated
    # differently and returns Trait(None) (which is the same as
    # Instance(NoneType))

    from .traits import Trait

    try:
        return as_ctrait(trait)
    except TypeError:
        return Trait(trait)


def mapped_trait_for(trait, name):
    """ Returns the 'mapped trait' definition for a mapped trait, the default
        value of which is a callable that maps the value of the original trait.

        Parameters
        ----------
        trait : ctrait.CTrait
            A trait for which the 'mapped trait' definition is being created.
        name : str
            The name of the trait for which the 'mapped trait' definition is
            being created.

        Returns
        -------
        trait_types.Any
            A definition of the 'mapped trait'
    """
    from .trait_types import Any
    from .constants import DefaultValue
    from .trait_base import Undefined

    mapped_trait = Any(
        is_base=False, transient=True, editable=False
    ).as_ctrait()

    def default(instance):
        value = getattr(instance, name, Undefined)
        if value is Undefined:
            return Undefined
        return trait.handler.mapped_value(value)

    mapped_trait.set_default_value(DefaultValue.callable, default)

    return mapped_trait
