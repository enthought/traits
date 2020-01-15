#  Copyright (c) 2005-20, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
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

from .ctrait import CTrait


def trait_cast(obj):
    """ Convert to a CTrait if the object knows how, else return None.
    """
    # special-case TraitType classes
    if isinstance(obj, type) and hasattr(obj, 'instantiate_and_get_ctrait'):
        return obj.instantiate_and_get_ctrait()

    if hasattr(obj, 'as_ctrait'):
        return obj.as_ctrait()

    return None


def check_trait(trait):
    """ Returns either the original value or a valid CTrait if the value can be
        converted to a CTrait.
    """
    # special-case TraitType classes
    if isinstance(trait, type) and hasattr(trait, 'instantiate_and_get_ctrait'):
        return trait.instantiate_and_get_ctrait()

    if hasattr(trait, 'as_ctrait'):
        return trait.as_ctrait()

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

    # special-case TraitType classes
    if isinstance(obj, type) and hasattr(obj, 'instantiate_and_get_ctrait'):
        return obj.instantiate_and_get_ctrait()

    if hasattr(obj, 'as_ctrait'):
        return obj.as_ctrait()

    return Trait(obj)


def trait_for(trait):
    """ Returns the trait corresponding to a specified value.
    """
    # XXX this is the same as trait_from except that None is treated
    # differently and returns Trait(None) (which is the same as
    # Instance(NoneType))

    from .traits import Trait

    trait = check_trait(trait)
    if isinstance(trait, CTrait):
        return trait

    return Trait(trait)


def mapped_trait_for(trait):
    """ Returns the 'mapped trait' definition for a mapped trait.
    """
    from .trait_types import Any

    default_value = trait.default_value()[1]
    try:
        default_value = trait.handler.mapped_value(default_value)
    except Exception:
        pass

    return Any(
        default_value, is_base=False, transient=True, editable=False
    ).as_ctrait()
