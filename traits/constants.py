# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from enum import IntEnum

import traits.ctraits


class TraitKind(IntEnum):
    """ These determine the getters and setters used by the cTrait instance.
    """

    #: A standard trait (validates and notifies).
    trait = 0

    #: A standard Python attribute (no validation or notification).
    #: This sets values into the object dict, so is not suitable for use with
    #: standard Python descriptors - generally you want ``generic``.
    python = 1

    #: An event trait (can't read value, only assign value).
    event = 2

    #: A delegated trait.
    delegate = 3

    #: A trait property.
    property = 4

    #: A trait that can neither be assigned or read.
    disallow = 5

    #: A trait that can be assigned once, and after that only read (no
    #: validation or notification).
    read_only = 6

    #: A trait whose value is constant (can only be read).
    constant = 7

    #: A standard Python attribute or descriptor (no validation or
    #: notification).
    generic = 8


class ValidateTrait(IntEnum):
    """ These are indices into the ctraits.c validate_handlers array. """

    #: A type check.
    type = 0

    #: An instance check.
    instance = 1

    #: A self-type check.
    self_type = 2

    #: An integer range check (unused).
    int_range = 3

    #: A floating-point range check.
    float_range = 4

    #: An enumerated item check.
    enum = 5

    #: A mapped item check.
    map = 6

    #: A complex fast validator check with multiple fast validators.
    complex = 7

    #: A slow validator (only used in complex validators).
    slow = 8

    #: A tuple type check.
    tuple = 9

    #: A prefix map item check.
    prefix_map = 10

    #: A coercable type check.
    coerce = 11

    #: A castable type check.
    cast = 12

    #: A function check.
    function = 13

    #: A Python-based validator.
    python = 14

    #: An adaptable object check.
    adapt = 19

    #: An integer check.
    int = 20

    #: A floating-point check.
    float = 21

    #: A callable check.
    callable = 22

    #: A complex number check.
    complex_number = 23


class ComparisonMode(IntEnum):
    """ Comparison mode.

    Indicates when trait change notifications should be generated based upon
    the result of comparing the old and new values of a trait assignment:

    Enumeration members:

    none
        The values are not compared and a trait change notification is
        generated on each assignment.
    identity
        A trait change notification is generated if the old and new values are
        not the same object.
    equality
        A trait change notification is generated if the old and new values are
        not the same object, and not equal using Python's standard equality
        testing. This is the default.
    """

    #: Do not compare values (always fire trait change)
    none = 0

    #: Compare values by object identity.
    identity = 1

    #: Compare values by equality.
    equality = 2


# Backward compatibility for comparison mode constants.

#: Deprecated alias for ``ComparisonMode.none``.
NO_COMPARE = ComparisonMode.none

#: Deprecated alias for ``ComparisonMode.identity``.
OBJECT_IDENTITY_COMPARE = ComparisonMode.identity

#: Deprecated alias for ``ComparisonMode.equality``.
RICH_COMPARE = ComparisonMode.equality


class DefaultValue(IntEnum):
    """ Default value types. """

    #: The default value type has not been specified
    unspecified = -1

    #: The default_value of the trait is the default value.
    constant = traits.ctraits._CONSTANT_DEFAULT_VALUE

    #: The default_value of the trait is Missing.
    missing = traits.ctraits._MISSING_DEFAULT_VALUE

    #: The object containing the trait is the default value.
    object = traits.ctraits._OBJECT_DEFAULT_VALUE

    #: A new copy of the list specified by default_value is the default value.
    list_copy = traits.ctraits._LIST_COPY_DEFAULT_VALUE

    #: A new copy of the dict specified by default_value is the default value.
    dict_copy = traits.ctraits._DICT_COPY_DEFAULT_VALUE

    #: A new instance of TraitListObject constructed using the default_value
    #: list is the default value.
    trait_list_object = traits.ctraits._TRAIT_LIST_OBJECT_DEFAULT_VALUE

    #: A new instance of TraitDictObject constructed using the default_value
    #: dict is the default value.
    trait_dict_object = traits.ctraits._TRAIT_DICT_OBJECT_DEFAULT_VALUE

    #: The default_value is a tuple of the form: (*callable*, *args*, *kw*),
    #: where *callable* is a callable, *args* is a tuple, and *kw* is either a
    #: dictionary or None. The default value is the result obtained by invoking
    #: ``callable(\*args, \*\*kw)``.
    callable_and_args = traits.ctraits._CALLABLE_AND_ARGS_DEFAULT_VALUE

    #: The default_value is a callable. The default value is the result
    #: obtained by invoking *default_value*(*object*), where *object* is the
    #: object containing the trait. If the trait has a validate() method, the
    #: validate() method is also called to validate the result.
    callable = traits.ctraits._CALLABLE_DEFAULT_VALUE

    #: A new instance of TraitSetObject constructed using the default_value set
    #: is the default value.
    trait_set_object = traits.ctraits._TRAIT_SET_OBJECT_DEFAULT_VALUE

    #: This trait doesn't permit a default value, and an attempt to retrieve
    #: the default value using the default_value_for method will fail.
    disallow = traits.ctraits._DISALLOW_DEFAULT_VALUE


#: Maximum legal value for default_value_type, for use in testing
#: and validation.
MAXIMUM_DEFAULT_VALUE_TYPE = traits.ctraits._MAXIMUM_DEFAULT_VALUE_TYPE


#: Mapping from 'ctrait' default value types to a string representation:
default_value_map = {
    DefaultValue.constant: "value",
    DefaultValue.missing: "value",
    DefaultValue.object: "self",
    DefaultValue.list_copy: "list",
    DefaultValue.dict_copy: "dict",
    DefaultValue.trait_list_object: "list",
    DefaultValue.trait_dict_object: "dict",
    DefaultValue.callable_and_args: "factory",
    DefaultValue.callable: "method",
    DefaultValue.trait_set_object: "set",
    DefaultValue.disallow: "invalid",
}
