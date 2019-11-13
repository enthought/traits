# ------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   06/21/2002
#
#  Refactored into a separate module: 07/04/2003
#
# ------------------------------------------------------------------------------

"""
Defines the BaseTraitHandler class and a standard set of BaseTraitHandler
subclasses for use with the Traits package.

A trait handler mediates the assignment of values to object traits. It
verifies (via its validate() method) that a specified value is consistent
with the object trait, and generates a TraitError exception if it is not
consistent.
"""

# -------------------------------------------------------------------------------
#  Imports:
# -------------------------------------------------------------------------------

from __future__ import absolute_import

import sys
import re
import copy

import six
import six.moves as sm

from types import FunctionType, MethodType

TypeType = type

from weakref import ref

from .trait_base import (
    strx,
    SequenceTypes,
    Undefined,
    TypeTypes,
    ClassTypes,
    CoercableTypes,
    TraitsCache,
    class_of,
    Missing,
)
from .trait_errors import TraitError, repr_type

from . import _py2to3

from ._py2to3 import LONG_TYPE

# Patched by 'traits.py' once class is defined!
Trait = Event = None

# Set up a logger:
import logging

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------------
#  Constants:
# -------------------------------------------------------------------------------

# Trait 'comparison_mode' enum values:
NO_COMPARE = 0
OBJECT_IDENTITY_COMPARE = 1
RICH_COMPARE = 2

RangeTypes = (int, LONG_TYPE, float)

CallableTypes = (FunctionType, MethodType)


#: Default value types
#: The default value type has not been specified
UNSPECIFIED_DEFAULT_VALUE = -1
#: The default_value of the trait is the default value.
CONSTANT_DEFAULT_VALUE = 0
#: The default_value of the trait is Missing.
MISSING_DEFAULT_VALUE = 1
#: The object containing the trait is the default value.
OBJECT_DEFAULT_VALUE = 2
#: A new copy of the list specified by default_value is the default value.
LIST_COPY_DEFAULT_VALUE = 3
#: A new copy of the dict specified by default_value is the default value.
DICT_COPY_DEFAULT_VALUE = 4
#: A new instance of TraitListObject constructed using the default_value list
#: is the default value.
TRAIT_LIST_OBJECT_DEFAULT_VALUE = 5
#: A new instance of TraitDictObject constructed using the default_value dict
#: is the default value.
TRAIT_DICT_OBJECT_DEFAULT_VALUE = 6
#: The default_value is a tuple of the form: (*callable*, *args*, *kw*),
#: where *callable* is a callable, *args* is a tuple, and *kw* is either a
#: dictionary or None. The default value is the result obtained by invoking
#: ``callable(\*args, \*\*kw)``.
CALLABLE_AND_ARGS_DEFAULT_VALUE = 7
#: The default_value is a callable. The default value is the result obtained
#: by invoking *default_value*(*object*), where *object* is the object
#: containing the trait. If the trait has a validate() method, the validate()
#: method is also called to validate the result.
CALLABLE_DEFAULT_VALUE = 8
#: A new instance of TraitSetObject constructed using the default_value set
#: is the default value.
TRAIT_SET_OBJECT_DEFAULT_VALUE = 9


# Mapping from trait metadata 'type' to CTrait 'type':
trait_types = {"python": 1, "event": 2}

# -------------------------------------------------------------------------------
#  Forward references:
# -------------------------------------------------------------------------------

trait_from = None  # Patched by 'traits.py' when real 'trait_from' is defined

# -------------------------------------------------------------------------------
#  Returns the correct argument count for a specified function or method:
# -------------------------------------------------------------------------------


def _arg_count(func):
    """ Returns the correct argument count for a specified function or method.
    """
    if (type(func) is MethodType) and (func.__self__ is not None):
        return func.__code__.co_argcount - 1
    return func.__code__.co_argcount


# -------------------------------------------------------------------------------
#  Property error handling functions:
# -------------------------------------------------------------------------------


def _write_only(object, name):
    raise TraitError(
        "The '%s' trait of %s instance is 'write only'."
        % (name, class_of(object))
    )


def _read_only(object, name, value):
    raise TraitError(
        "The '%s' trait of %s instance is 'read only'."
        % (name, class_of(object))
    )


def _undefined_get(object, name):
    raise TraitError(
        (
            "The '%s' trait of %s instance is a property that has "
            "no 'get' or 'set' method"
        )
        % (name, class_of(object))
    )


def _undefined_set(object, name, value):
    _undefined_get(object, name)


# -------------------------------------------------------------------------------
#  'BaseTraitHandler' class (base class for all user defined traits and trait
#  handlers):
# -------------------------------------------------------------------------------


class BaseTraitHandler(object):
    """ The task of this class and its subclasses is to verify the correctness
    of values assigned to object trait attributes.

    This class is an alternative to trait validator functions. A trait handler
    has several advantages over a trait validator function, due to being an
    object:

        * Trait handlers have constructors and state. Therefore, you can use
          them to create *parametrized types*.
        * Trait handlers can have multiple methods, whereas validator functions
          can have only one callable interface. This feature allows more
          flexibility in their implementation, and allows them to handle a
          wider range of cases, such as interactions with other components.
    """

    default_value_type = UNSPECIFIED_DEFAULT_VALUE
    has_items = False
    is_mapped = False
    editor = None
    info_text = "a legal value"

    def is_valid(self, object, name, value):
        try:
            validate = self.validate
            try:
                validate(object, name, value)
                return True
            except:
                return False
        except:
            return True

    def error(self, object, name, value):
        """Raises a TraitError exception.

        Parameters
        ----------
        object : object
            The object whose attribute is being assigned.
        name : str
            The name of the attribute being assigned.
        value : object
            The proposed new value for the attribute.

        Description
        -----------
        This method is called by the validate() method when an assigned value
        is not valid. Raising a TraitError exception either notifies the user of
        the problem, or, in the case of compound traits, provides a chance for
        another trait handler to handle to validate the value.
        """
        raise TraitError(
            object, name, self.full_info(object, name, value), value
        )

    def full_info(self, object, name, value):
        """Returns a string describing the type of value accepted by the
        trait handler.

        Parameters
        ----------
        object : object
            The object whose attribute is being assigned.
        name : str
            The name of the attribute being assigned.
        value :
            The proposed new value for the attribute.

        Description
        -----------
        The string should be a phrase describing the type defined by the
        TraitHandler subclass, rather than a complete sentence. For example, use
        the phrase, "a square sprocket" instead of the sentence, "The value must
        be a square sprocket." The value returned by full_info() is combined
        with other information whenever an error occurs and therefore makes more
        sense to the user if the result is a phrase. The full_info() method is
        similar in purpose and use to the **info** attribute of a validator
        function.

        Note that the result can include information specific to the particular
        trait handler instance. For example, TraitRange instances return a
        string indicating the range of values acceptable to the handler (e.g.,
        "an integer in the range from 1 to 9"). If the full_info() method is not
        overridden, the default method returns the value of calling the info()
        method.
        """
        return self.info()

    def info(self):
        """Must return a string describing the type of value accepted by the
        trait handler.

        The string should be a phrase describing the type defined by the
        TraitHandler subclass, rather than a complete sentence. For example, use
        the phrase, "a square sprocket" instead of the sentence, "The value must
        be a square sprocket." The value returned by info() is combined with
        other information whenever an error occurs and therefore makes more
        sense to the user if the result is a phrase. The info() method is
        similar in purpose and use to the **info** attribute of a validator
        function.

        Note that the result can include information specific to the particular
        trait handler instance. For example, TraitRange instances return a
        string indicating the range of values acceptable to the handler (e.g.,
        "an integer in the range from 1 to 9"). If the info() method is not
        overridden, the default method returns the value of the 'info_text'
        attribute.
        """
        return self.info_text

    def repr(self, value):
        """ Returns a printable representation of a value along with its type.

        .. deprecated :: 3.0.3
            This functionality was only used to provide readable error
            messages. This functionality has been incorporated into
            TraitError itself.

        Parameters
        ----------
        value : object
            The value to be printed.
        """
        import warnings

        warnings.warn(
            "this functionality has been merged into TraitError; "
            "just pass the raw value",
            DeprecationWarning,
        )
        return repr_type(value)

    def get_editor(self, trait=None):
        """ Returns a trait editor that allows the user to modify the *trait*
        trait.

        Parameters
        ----------
        trait : Trait
            The trait to be edited.

        Description
        -----------
        This method only needs to be specified if traits defined using this
        trait handler require a non-default trait editor in trait user
        interfaces. The default implementation of this method returns a trait
        editor that allows the user to type an arbitrary string as the value.

        For more information on trait user interfaces, refer to the *Traits UI
        User Guide*.
        """
        if self.editor is None:
            self.editor = self.create_editor()

        return self.editor

    def create_editor(self):
        """ Returns the default traits UI editor to use for a trait.
        """
        from traitsui.api import TextEditor

        return TextEditor()

    def inner_traits(self):
        """ Returns a tuple containing the *inner traits* for this trait. Most
            trait handlers do not have any inner traits, and so will return an
            empty tuple. The exceptions are **List** and **Dict** trait types,
            which have inner traits used to validate the values assigned to the
            trait. For example, in *List( Int )*, the *inner traits* for
            **List** are ( **Int**, ).
        """
        return ()


# -------------------------------------------------------------------------------
#  'TraitType' (base class for class-based trait definitions:
# -------------------------------------------------------------------------------

# Create a singleton object for use in the TraitType constructor:
class NoDefaultSpecified(object):
    pass


NoDefaultSpecified = NoDefaultSpecified()


class TraitType(BaseTraitHandler):
    """ Base class for new trait types.

        This class enables you to define new traits using a class-based
        approach, instead of by calling the Trait() factory function with an
        instance of a TraitHandler derived object.

        When subclassing this class, you can implement one or more of the
        method signatures below. Note that these methods are defined only as
        comments, because the absence of method definitions in the subclass
        definition implicitly provides information about how the trait should
        operate.

        The optional methods are as follows:

        * **get ( self, object, name ):**

          This is the getter method of a trait that behaves like a property.

          :Parameters:
            **object** (*object*) -- The object that the property applies to.

            **name** (str) -- The name of the property on *object* property.

          *Description*

          If neither this method nor the set() method is defined, the value
          of the trait is handled like a normal object attribute. If this
          method is not defined, but the set() method is defined, the trait
          behaves like a write-only property. This method should return the
          value of the *name* property for the *object* object.

        * **set ( self, object, name, value )**

          This is the setter method of a trait that behaves like a property.

          :Parameters:
            **object** (*object*) -- The object that the property applies to.

            **name** (str) -- The name of the property on *object*.

            **value** -- The value being assigned as the value of the property.

          *Description*

          If neither this method nor the get() method is implemented, the
          trait behaves like a normal trait attribute. If this method is not
          defined, but the get() method is defined, the trait behaves like a
          read-only property. This method does not need to return a value,
          but it should raise a TraitError exception if the specified *value*
          is not valid and cannot be coerced or adapted to a valid value.

        * **validate ( self, object, name, value )**

          This method validates, coerces, or adapts the specified *value* as
          the value of the *name* trait of the *object* object. This method
          is called when a value is assigned to an object trait that is
          based on this subclass of *TraitType* and the class does not
          contain a definition for either the get() or set() methods. This
          method must return the original *value* or any suitably coerced or
          adapted value that is a legal value for the trait. If *value* is
          not a legal value for the trait, and cannot be coerced or adapted
          to a legal value, the method should either raise a **TraitError** or
          call the **error** method to raise the **TraitError** on its behalf.

        * **is_valid_for ( self, value )**

          As an alternative to implementing the **validate** method, you can
          instead implement the **is_valid_for** method, which receives only
          the *value* being assigned. It should return **True** if the value is
          valid, and **False** otherwise.

        * **value_for ( self, value )**

          As another alternative to implementing the **validate** method, you
          can instead implement the **value_for** method, which receives only
          the *value* being assigned. It should return the validated form of
          *value* if it is valid, or raise a **TraitError** if the value is not
          valid.

        * **post_setattr ( self, object, name, value )**

          This method allows the trait to do additional processing after
          *value* has been successfully assigned to the *name* trait of the
          *object* object. For most traits there is no additional processing
          that needs to be done, and this method need not be defined. It is
          normally used for creating "shadow" (i.e., "mapped" traits), but
          other uses may arise as well. This method does not need to return
          a value, and should normally not raise any exceptions.
    """

    default_value = Undefined
    metadata = {}

    def __init__(self, default_value=NoDefaultSpecified, **metadata):
        """ This constructor method is the only method normally called
            directly by client code. It defines the trait. The
            default implementation accepts an optional, untype-checked default
            value, and caller-supplied trait metadata. Override this method
            whenever a different method signature or a type-checked
            default value is needed.
        """
        if default_value is not NoDefaultSpecified:
            self.default_value = default_value

        if len(metadata) > 0:
            if len(self.metadata) > 0:
                self._metadata = self.metadata.copy()
                self._metadata.update(metadata)
            else:
                self._metadata = metadata
            # By default, private traits are not visible.
            if (
                self._metadata.get("private")
                and self._metadata.get("visible") is None
            ):
                self._metadata["visible"] = False
        else:
            self._metadata = self.metadata.copy()

        self.init()

    def init(self):
        """ Allows the trait to perform any additional initialization needed.
        """
        pass

    def get_default_value(self):
        r"""Returns a tuple of the form: (*default_value_type*, *default_value*)
            which describes the default value for this trait. The default
            implementation analyzes the value of the trait's **default_value**
            attribute and determines an appropriate *default_value_type* for
            *default_value*. If you need to override this method to provide a
            different result tuple, the following values are valid values for
            *default_value_type*:

                - 0, 1: The *default_value* item of the tuple is the default
                  value.
                - 2: The object containing the trait is the default value.
                - 3: A new copy of the list specified by *default_value* is
                  the default value.
                - 4: A new copy of the dictionary specified by *default_value*
                  is the default value.
                - 5: A new instance of TraitListObject constructed using the
                  *default_value* list is the default value.
                - 6: A new instance of TraitDictObject constructed using the
                  *default_value* dictionary is the default value.
                - 7: *default_value* is a tuple of the form: (*callable*, *args*,
                  *kw*), where *callable* is a callable, *args* is a tuple, and
                  *kw* is either a dictionary or None. The default value is the
                  result obtained by invoking callable(\*args, \*\*kw).
                - 8: *default_value* is a callable. The default value is the
                  result obtained by invoking *default_value*(*object*), where
                  *object* is the object containing the trait. If the trait has
                  a validate() method, the validate() method is also called to
                  validate the result.
                - 9: A new instance of TraitSetObject constructed using the
                  *default_value* set is the default value.
        """
        dv = self.default_value
        dvt = self.default_value_type
        if dvt < 0:
            dvt = CONSTANT_DEFAULT_VALUE
            if isinstance(dv, TraitListObject):
                dvt = TRAIT_LIST_OBJECT_DEFAULT_VALUE
            elif isinstance(dv, list):
                dvt = LIST_COPY_DEFAULT_VALUE
            elif isinstance(dv, TraitDictObject):
                dvt = TRAIT_DICT_OBJECT_DEFAULT_VALUE
            elif isinstance(dv, dict):
                dvt = DICT_COPY_DEFAULT_VALUE
            elif isinstance(dv, TraitSetObject):
                dvt = TRAIT_SET_OBJECT_DEFAULT_VALUE

            self.default_value_type = dvt

        return (dvt, dv)

    def clone(self, default_value=Missing, **metadata):
        """ Clones the contents of this object into a new instance of the same
            class, and then modifies the cloned copy using the specified
            *default_value* and *metadata*. Returns the cloned object as the
            result.

            Note that subclasses can change the signature of this method if
            needed, but should always call the 'super' method if possible.
        """
        if "parent" not in metadata:
            metadata["parent"] = self

        new = self.__class__.__new__(self.__class__)
        new_dict = new.__dict__
        new_dict.update(self.__dict__)

        if "editor" in new_dict:
            del new_dict["editor"]

        if "_metadata" in new_dict:
            new._metadata = new._metadata.copy()
        else:
            new._metadata = {}

        new._metadata.update(metadata)

        if default_value is not Missing:
            new.default_value = default_value
            if self.validate is not None:
                try:
                    new.default_value = self.validate(
                        None, None, default_value
                    )
                except:
                    pass

        return new

    def get_value(self, object, name, trait=None):
        """ Returns the current value of a property-based trait.
        """
        cname = TraitsCache + name
        value = object.__dict__.get(cname, Undefined)
        if value is Undefined:
            if trait is None:
                trait = object.trait(name)

            object.__dict__[cname] = value = trait.default_value_for(
                object, name
            )

        return value

    def set_value(self, object, name, value):
        """ Sets the cached value of a property-based trait and fires the
            appropriate trait change event.
        """
        cname = TraitsCache + name
        old = object.__dict__.get(cname, Undefined)
        if value != old:
            object.__dict__[cname] = value
            object.trait_property_changed(name, old, value)

    # -- Private Methods --------------------------------------------------------

    def __call__(self, *args, **kw):
        """ Allows a derivative trait to be defined from this one.
        """
        return self.clone(*args, **kw).as_ctrait()

    def _is_valid_for(self, object, name, value):
        """ Handles a simplified validator that only returns whether or not the
            original value is valid.
        """
        if self.is_valid_for(value):
            return value

        self.error(object, name, value)

    def _value_for(self, object, name, value):
        """ Handles a simplified validator that only receives the value
            argument.
        """
        try:
            return self.value_for(value)
        except TraitError:
            self.error(object, name, value)

    def as_ctrait(self):
        """ Returns a CTrait corresponding to the trait defined by this class.
        """
        from .traits import CTrait

        metadata = getattr(self, "_metadata", {})
        getter = getattr(self, "get", None)
        setter = getattr(self, "set", None)
        if (getter is not None) or (setter is not None):
            if getter is None:
                getter = _write_only
                metadata.setdefault("transient", True)
            elif setter is None:
                setter = _read_only
                metadata.setdefault("transient", True)
            trait = CTrait(4)
            n = 0
            validate = getattr(self, "validate", None)
            if validate is not None:
                n = _arg_count(validate)
            trait.property(
                getter,
                _arg_count(getter),
                setter,
                _arg_count(setter),
                validate,
                n,
            )
            metadata.setdefault("type", "property")
        else:
            type = getattr(self, "ctrait_type", None)
            if type is None:
                type = trait_types.get(metadata.get("type"), 0)
            trait = CTrait(type)

            validate = getattr(self, "fast_validate", None)
            if validate is None:
                validate = getattr(self, "validate", None)
                if validate is None:
                    validate = getattr(self, "is_valid_for", None)
                    if validate is not None:
                        validate = self._is_valid_for
                    else:
                        validate = getattr(self, "value_for", None)
                        if validate is not None:
                            validate = self._value_for

            if validate is not None:
                trait.set_validate(validate)

            post_setattr = getattr(self, "post_setattr", None)
            if post_setattr is not None:
                trait.post_setattr = post_setattr
                trait.is_mapped(self.is_mapped)

            # Note: The use of 'rich_compare' metadata is deprecated; use
            # 'comparison_mode' metadata instead:
            rich_compare = metadata.get("rich_compare")
            if rich_compare is not None:
                trait.rich_comparison(rich_compare is True)

            comparison_mode = metadata.get("comparison_mode")
            if comparison_mode is not None:
                trait.comparison_mode(comparison_mode)

            metadata.setdefault("type", "trait")

        trait.default_value(*self.get_default_value())

        trait.value_allowed(metadata.get("trait_value", False) is True)

        trait.handler = self

        trait.__dict__ = metadata.copy()

        return trait

    def __getattr__(self, name):
        if (name[:2] == "__") and (name[-2:] == "__"):
            raise AttributeError(
                "'%s' object has no attribute '%s'"
                % (self.__class__.__name__, name)
            )

        return getattr(self, "_metadata", {}).get(name, None)


# -------------------------------------------------------------------------------
#  'TraitHandler' class (base class for all trait handlers):
# -------------------------------------------------------------------------------


class TraitHandler(BaseTraitHandler):
    """ The task of this class and its subclasses is to verify the correctness
    of values assigned to object trait attributes.

    This class is an alternative to trait validator functions. A trait handler
    has several advantages over a trait validator function, due to being an
    object:

        * Trait handlers have constructors and state. Therefore, you can use
          them to create *parametrized types*.
        * Trait handlers can have multiple methods, whereas validator functions
          can have only one callable interface. This feature allows more
          flexibility in their implementation, and allows them to handle a
          wider range of cases, such as interactions with other components.

    The only method of TraitHandler that *must* be implemented by subclasses
    is validate().
    """

    def validate(self, object, name, value):
        """ Verifies whether a new value assigned to a trait attribute is valid.

        Parameters
        ----------
        object : object
            The object whose attribute is being assigned.
        name : str
            The name of the attribute being assigned.
        value :
            The proposed new value for the attribute.

        Returns
        -------
        If the new value is valid, this method must return either the original
        value passed to it, or an alternate value to be assigned in place of the
        original value. Whatever value this method returns is the actual value
        assigned to *object.name*.

        Description
        -----------
        This method *must* be implemented by subclasses of TraitHandler. It is
        called whenever a new value is assigned to a trait attribute defined
        using this trait handler.

        If the value received by validate() is not valid for the trait
        attribute, the method must called the predefined error() method to
        raise a TraitError exception

        """
        raise TraitError(
            "The '%s' trait of %s instance has an unknown type. "
            "Contact the developer to correct the problem."
            % (name, class_of(object))
        )


# -------------------------------------------------------------------------------
#  'TraitRange' class:
# -------------------------------------------------------------------------------


class TraitRange(TraitHandler):
    """Ensures that a trait attribute lies within a specified numeric range.

    TraitRange is the underlying handler for the predefined Range() trait
    factory.

    Any value assigned to a trait containing a TraitRange handler must be of the
    correct type and in the numeric range defined by the TraitRange instance.
    No automatic coercion takes place. For example::

        class Person(HasTraits):
            age = Trait(0, TraitRange(0, 150))
            weight = Trait(0.0, TraitRange(0.0, None))

    This example defines a Person class, which has an **age** trait
    attribute, which must be an integer/long in the range from 0 to 150, and a
    **weight** trait attribute, which must be a non-negative float value.
    """

    def __init__(
        self, low=None, high=None, exclude_low=False, exclude_high=False
    ):
        """ Creates a TraitRange handler.

        Parameters
        ----------
        low : number
            The minimum value that the trait can accept.
        high : number
            The maximum value that the trait can accept.
        exclude_low : bool
            Should the *low* value be exclusive (or inclusive).
        exclude_high : bool
            Should the *high* value be exclusive (or inclusive).

        Description
        -----------
        The *low* and *high* values must be of the same Python numeric type,
        either ``int``, ``long`` or ``float``. Alternatively, one of the values
        may be None, to indicate that that portion of the range is
        unbounded. The *exclude_low* and *exclude_high* values can be used to
        specify whether the *low* and *high* values should be exclusive (or
        inclusive).
        """
        vtype = type(high)
        if (low is not None) and (vtype is not float):
            vtype = type(low)
        if vtype not in RangeTypes:
            raise TraitError(
                "TraitRange can only be use for int, long or "
                "float values, but a value of type %s was "
                "specified." % vtype
            )
        if vtype is float:
            self.validate = self.float_validate
            kind = 4
            self._type_desc = "a floating point number"
            if low is not None:
                low = float(low)
            if high is not None:
                high = float(high)
        elif vtype is LONG_TYPE:
            self.validate = self.long_validate
            self._type_desc = "a long integer"
            if low is not None:
                low = LONG_TYPE(low)
            if high is not None:
                high = LONG_TYPE(high)
        else:
            self.validate = self.int_validate
            kind = 3
            self._type_desc = "an integer"
            if low is not None:
                low = int(low)
            if high is not None:
                high = int(high)
        exclude_mask = 0
        if exclude_low:
            exclude_mask |= 1
        if exclude_high:
            exclude_mask |= 2
        if vtype is not LONG_TYPE:
            self.fast_validate = (kind, low, high, exclude_mask)

        # Assign type-corrected arguments to handler attributes
        self._low = low
        self._high = high
        self._exclude_low = exclude_low
        self._exclude_high = exclude_high

    def float_validate(self, object, name, value):
        try:
            if (
                isinstance(value, RangeTypes)
                and (
                    (self._low is None)
                    or (self._exclude_low and (self._low < value))
                    or ((not self._exclude_low) and (self._low <= value))
                )
                and (
                    (self._high is None)
                    or (self._exclude_high and (self._high > value))
                    or ((not self._exclude_high) and (self._high >= value))
                )
            ):
                return float(value)
        except:
            pass
        self.error(object, name, value)

    def int_validate(self, object, name, value):
        try:
            if (
                isinstance(value, int)
                and (
                    (self._low is None)
                    or (self._exclude_low and (self._low < value))
                    or ((not self._exclude_low) and (self._low <= value))
                )
                and (
                    (self._high is None)
                    or (self._exclude_high and (self._high > value))
                    or ((not self._exclude_high) and (self._high >= value))
                )
            ):
                return value
        except:
            pass
        self.error(object, name, value)

    def long_validate(self, object, name, value):
        try:
            if (
                isinstance(value, six.integer_types)
                and (
                    (self._low is None)
                    or (self._exclude_low and (self._low < value))
                    or ((not self._exclude_low) and (self._low <= value))
                )
                and (
                    (self._high is None)
                    or (self._exclude_high and (self._high > value))
                    or ((not self._exclude_high) and (self._high >= value))
                )
            ):
                return value
        except:
            pass
        self.error(object, name, value)

    def info(self):
        if self._low is None:
            if self._high is None:
                return self._type_desc
            return "%s <%s %s" % (
                self._type_desc,
                "="[self._exclude_high :],
                self._high,
            )
        elif self._high is None:
            return "%s >%s %s" % (
                self._type_desc,
                "="[self._exclude_low :],
                self._low,
            )
        return "%s <%s %s <%s %s" % (
            self._low,
            "="[self._exclude_low :],
            self._type_desc,
            "="[self._exclude_high :],
            self._high,
        )

    def get_editor(self, trait):
        from traitsui.api import RangeEditor

        auto_set = trait.auto_set
        if auto_set is None:
            auto_set = True

        return RangeEditor(
            self,
            mode=trait.mode or "auto",
            cols=trait.cols or 3,
            auto_set=auto_set,
            enter_set=trait.enter_set or False,
            low_label=trait.low or "",
            high_label=trait.high or "",
        )


# -------------------------------------------------------------------------------
#  'TraitString' class:
# -------------------------------------------------------------------------------


class TraitString(TraitHandler):
    """ Ensures that a trait attribute value is a string that satisfied some
    additional, optional constraints.

    The optional constraints include minimum and maximum lengths, and a regular
    expression that the string must match.

    If the value assigned to the trait attribute is a Python numeric type, the
    TraitString handler first coerces the value to a string. Values of other
    non-string types result in a TraitError being raised. The handler then
    makes sure that the resulting string is within the specified length range
    and that it matches the regular expression.

    Example
    -------

    class Person(HasTraits):
        name = Trait('', TraitString(maxlen=50, regex=r'^[A-Za-z]*$'))


    This example defines a **Person** class with a **name** attribute, which
    must be a string of between 0 and 50 characters that consist of only
    upper and lower case letters.
    """

    def __init__(self, minlen=0, maxlen=six.MAXSIZE, regex=""):
        """ Creates a TraitString handler.

        Parameters
        ----------
        minlen : int
            The minimum length allowed for the string.
        maxlen : int
            The maximum length allowed for the string.
        regex : str
            A Python regular expression that the string must match.

        """
        self.minlen = max(0, minlen)
        self.maxlen = max(self.minlen, maxlen)
        self.regex = regex
        self._init()

    def _init(self):
        if self.regex != "":
            self.match = re.compile(self.regex).match
            if (self.minlen == 0) and (self.maxlen == six.MAXSIZE):
                self.validate = self.validate_regex
        elif (self.minlen == 0) and (self.maxlen == six.MAXSIZE):
            self.validate = self.validate_str
        else:
            self.validate = self.validate_len

    def validate(self, object, name, value):
        try:
            value = strx(value)
            if (self.minlen <= len(value) <= self.maxlen) and (
                self.match(value) is not None
            ):
                return value
        except:
            pass
        self.error(object, name, value)

    def validate_str(self, object, name, value):
        try:
            return strx(value)
        except:
            pass
        self.error(object, name, value)

    def validate_len(self, object, name, value):
        try:
            value = strx(value)
            if self.minlen <= len(value) <= self.maxlen:
                return value
        except:
            pass
        self.error(object, name, value)

    def validate_regex(self, object, name, value):
        try:
            value = strx(value)
            if self.match(value) is not None:
                return value
        except:
            pass
        self.error(object, name, value)

    def info(self):
        msg = ""
        if (self.minlen != 0) and (self.maxlen != six.MAXSIZE):
            msg = " between %d and %d characters long" % (
                self.minlen,
                self.maxlen,
            )
        elif self.maxlen != six.MAXSIZE:
            msg = " <= %d characters long" % self.maxlen
        elif self.minlen != 0:
            msg = " >= %d characters long" % self.minlen
        if self.regex != "":
            if msg != "":
                msg += " and"
            msg += " matching the pattern '%s'" % self.regex
        return "a string" + msg

    def __getstate__(self):
        result = self.__dict__.copy()
        for name in ["validate", "match"]:
            if name in result:
                del result[name]
        return result

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._init()


# -------------------------------------------------------------------------------
#  'TraitCoerceType' class:
# -------------------------------------------------------------------------------


class TraitCoerceType(TraitHandler):
    """Ensures that a value assigned to a trait attribute is of a specified
    Python type, or can be coerced to the specified type.

    TraitCoerceType is the underlying handler for the predefined traits and
    factories for Python simple types. The TraitCoerceType class is also an
    example of a parametrized type, because the single TraitCoerceType class
    allows creating instances that check for totally different sets of values.
    For example::

        class Person(HasTraits):
            name = Trait('', TraitCoerceType(''))
            weight = Trait(0.0, TraitCoerceType(float))

    In this example, the **name** attribute must be of type ``str`` (string),
    while the **weight** attribute must be of type ``float``, although both are
    based on instances of the TraitCoerceType class. Note that this example is
    essentially the same as writing::

        class Person(HasTraits):
            name = Trait('')
            weight = Trait(0.0)

    This simpler form is automatically changed by the Trait() function into
    the first form, based on TraitCoerceType instances, when the trait
    attributes are defined.

    For attributes based on TraitCoerceType instances, if a value that is
    assigned is not of the type defined for the trait, a TraitError exception
    is raised. However, in certain cases, if the value can be coerced to the
    required type, then the coerced value is assigned to the attribute. Only
    *widening* coercions are allowed, to avoid any possible loss of precision.
    The following table lists the allowed coercions.

    ============ =================
     Trait Type   Coercible Types
    ============ =================
    complex      float, int
    float        int
    long         int
    unicode      str
    ============ =================
    """

    def __init__(self, aType):
        """ Creates a TraitCoerceType handler.

        Parameters
        ----------
        aType : type
            Either a Python type (e.g., ``str`` or types.StringType) or a
            Python value (e.g., 'cat').

        Description
        -----------
        If *aType* is a value, it is mapped to its corresponding type. For
        example, the string 'cat' is automatically mapped to ``str`` (i.e.,
        types.StringType).
        """
        if not isinstance(aType, TypeType):
            aType = type(aType)
        self.aType = aType
        try:
            self.fast_validate = CoercableTypes[aType]
        except:
            self.fast_validate = (11, aType)

    def validate(self, object, name, value):
        fv = self.fast_validate
        tv = type(value)

        # If the value is already the desired type, then return it:
        if tv is fv[1]:
            return value

        # Else see if it is one of the coercable types:
        for typei in fv[2:]:
            if tv is typei:
                # Return the coerced value:
                return fv[1](value)

        # Otherwise, raise an exception:
        self.error(object, name, value)

    def info(self):
        return "a value of %s" % str(self.aType)[1:-1]

    def get_editor(self, trait):

        # Make the special case of a 'bool' type use the boolean editor:
        if self.aType is bool:
            if self.editor is None:
                from traitsui.api import BooleanEditor

                self.editor = BooleanEditor()

            return self.editor

        # Otherwise, map all other types to a text editor:
        auto_set = trait.auto_set
        if auto_set is None:
            auto_set = True

        from traitsui.api import TextEditor

        return TextEditor(
            auto_set=auto_set,
            enter_set=trait.enter_set or False,
            evaluate=self.fast_validate[1],
        )


# -------------------------------------------------------------------------------
#  'TraitCastType' class:
# -------------------------------------------------------------------------------


class TraitCastType(TraitCoerceType):
    """Ensures that a value assigned to a trait attribute is of a specified
    Python type, or can be cast to the specified type.

    This class is similar to TraitCoerceType, but uses casting rather than
    coercion. Values are cast by calling the type with the value to be assigned
    as an argument. When casting is performed, the result of the cast is the
    value assigned to the trait attribute.

    Any trait that uses a TraitCastType instance in its definition ensures that
    its value is of the type associated with the TraitCastType instance. For
    example::

        class Person(HasTraits):
            name = Trait('', TraitCastType(''))
            weight = Trait(0.0, TraitCastType(float))

    In this example, the **name** trait must be of type ``str`` (string), while
    the **weight** trait must be of type ``float``. Note that this example is
    essentially the same as writing::

        class Person(HasTraits):
            name = CStr
            weight = CFloat

    To understand the difference between TraitCoerceType and TraitCastType (and
    also between Float and CFloat), consider the following example::

        >>>class Person(HasTraits):
        ...    weight = Float
        ...    cweight = CFloat
        >>>
        >>>bill = Person()
        >>>bill.weight = 180    # OK, coerced to 180.0
        >>>bill.cweight = 180   # OK, cast to 180.0
        >>>bill.weight = '180'  # Error, invalid coercion
        >>>bill.cweight = '180' # OK, cast to float('180')
    """

    def __init__(self, aType):
        """ Creates a TraitCastType handler.

        Parameters
        ----------
        aType : type
            Either a Python type (e.g., ``str`` or types.StringType) or a
            Python value (e.g., ``'cat``).

        Description
        -----------
        If *aType* is a Python value, it is automatically mapped to its
        corresponding Python type. For example, the string 'cat' is
        automatically mapped to ``str`` (i.e., types.StringType).

        """
        if not isinstance(aType, TypeType):
            aType = type(aType)
        self.aType = aType
        self.fast_validate = (12, aType)

    def validate(self, object, name, value):

        # If the value is already the desired type, then return it:
        if type(value) is self.aType:
            return value

        # Else try to cast it to the specified type:
        try:
            return self.aType(value)
        except:
            self.error(object, name, value)


# -------------------------------------------------------------------------------
#  'ThisClass' class:
# -------------------------------------------------------------------------------


class ThisClass(TraitHandler):
    """Ensures that the trait attribute values belong to the same class (or
       a subclass) as the object containing the trait attribute.

       ThisClass is the underlying handler for the predefined traits **This**
       and **self**, and the elements of ListThis.
    """

    def __init__(self, allow_none=False):
        """Creates a ThisClass handler.

        Parameters
        ----------
        allow_none : bool
            Flag indicating whether None is accepted as a valid value
            (True or non-zero) or not (False or 0).
        """
        if allow_none:
            self.validate = self.validate_none
            self.info = self.info_none
            self.fast_validate = (2, None)
        else:
            self.fast_validate = (2,)

    def validate(self, object, name, value):
        if isinstance(value, object.__class__):
            return value

        self.validate_failed(object, name, value)

    def validate_none(self, object, name, value):
        if isinstance(value, object.__class__) or (value is None):
            return value

        self.validate_failed(object, name, value)

    def info(self):
        return "an instance of the same type as the receiver"

    def info_none(self):
        return "an instance of the same type as the receiver or None"

    def validate_failed(self, object, name, value):
        self.error(object, name, value)

    def get_editor(self, trait):
        if self.editor is None:
            from traitsui.api import InstanceEditor

            self.editor = InstanceEditor(
                label=trait.label or "",
                view=trait.view or "",
                kind=trait.kind or "live",
            )
        return self.editor


# -------------------------------------------------------------------------------
#  'TraitInstance' class:
# -------------------------------------------------------------------------------

# Mapping from 'adapt' parameter values to 'fast validate' values
AdaptMap = {"no": -1, "yes": 0, "default": 1}


class TraitInstance(ThisClass):
    """Ensures that trait attribute values belong to a specified Python class
    or type.

    TraitInstance is the underlying handler for the predefined trait
    **Instance** and the elements of List( Instance ).

    Any trait that uses a TraitInstance handler ensures that its values belong
    to the specified type or class (or one of its subclasses). For example::

        class Employee(HasTraits):
            manager = Trait(None, TraitInstance(Employee, True))

    This example defines a class Employee, which has a **manager** trait
    attribute, which accepts either None or an instance of Employee
    as its value.

    TraitInstance ensures that assigned values are exactly of the type specified
    (i.e., no coercion is performed).
    """

    def __init__(self, aClass, allow_none=True, adapt="no", module=""):
        """Creates a TraitInstance handler.

        Parameters
        ----------
        aClass : class or type
            A Python class, an instance of a Python class, or a Python type.
        allow_none : bool
            Flag indicating whether None is accepted as a valid value.
            (True or non-zero) or not (False or 0)
        adapt : str
            Value indicating how adaptation should be handled:

            - 'no' (-1): Adaptation is not allowed.
            - 'yes' (0): Adaptation is allowed and should raise an exception if
              adaptation fails.
            - 'default' (1): Adaption is allowed and should return the default
              value if adaptation fails.
        module : module
            The module that the class belongs to.

        Description
        -----------
        If *aClass* is an instance, it is mapped to the class it is an instance
        of.
        """
        self._allow_none = allow_none
        self.adapt = AdaptMap[adapt]
        self.module = module
        if isinstance(aClass, six.string_types):
            self.aClass = aClass
        else:
            if not isinstance(aClass, ClassTypes):
                aClass = aClass.__class__
            self.aClass = aClass
            self.set_fast_validate()

    def allow_none(self):
        self._allow_none = True
        if hasattr(self, "fast_validate"):
            self.set_fast_validate()

    def set_fast_validate(self):
        if self.adapt < 0:
            fast_validate = [1, self.aClass]
            if self._allow_none:
                fast_validate = [1, None, self.aClass]
            if self.aClass in TypeTypes:
                fast_validate[0] = 0
            self.fast_validate = tuple(fast_validate)
        else:
            self.fast_validate = (
                19,
                self.aClass,
                self.adapt,
                self._allow_none,
            )

    def validate(self, object, name, value):

        from traits.adaptation.api import adapt

        if value is None:
            if self._allow_none:
                return value
            else:
                self.validate_failed(object, name, value)

        if isinstance(self.aClass, six.string_types):
            self.resolve_class(object, name, value)

        if self.adapt < 0:
            if isinstance(value, self.aClass):
                return value
        elif self.adapt == 0:
            try:
                return adapt(value, self.aClass)
            except:
                pass
        else:
            # fixme: The 'None' value is not really correct. It should return
            # the default value for the trait, but the handler does not have
            # any way to know this currently. Since the 'fast validate' code
            # does the correct thing, this should not normally be a problem.
            return adapt(value, self.aClass, None)

        self.validate_failed(object, name, value)

    def info(self):
        aClass = self.aClass
        if type(aClass) is not str:
            aClass = aClass.__name__

        if self.adapt < 0:
            result = class_of(aClass)
        else:
            result = (
                "an implementor of, or can be adapted to implement, %s"
                % aClass
            )

        if self._allow_none:
            return result + " or None"

        return result

    def resolve_class(self, object, name, value):
        aClass = self.validate_class(self.find_class(self.aClass))
        if aClass is None:
            self.validate_failed(object, name, value)
        self.aClass = aClass

        # fixme: The following is quite ugly, because it wants to try and fix
        # the trait referencing this handler to use the 'fast path' now that the
        # actual class has been resolved. The problem is finding the trait,
        # especially in the case of List(Instance('foo')), where the
        # object.base_trait(...) value is the List trait, not the Instance
        # trait, so we need to check for this and pull out the List
        # 'item_trait'. Obviously this does not extend well to other traits
        # containing nested trait references (Dict?)...
        self.set_fast_validate()
        trait = object.base_trait(name)
        handler = trait.handler
        if (handler is not self) and hasattr(handler, "item_trait"):
            trait = handler.item_trait
        trait.set_validate(self.fast_validate)

    def find_class(self, aClass):
        module = self.module
        col = aClass.rfind(".")
        if col >= 0:
            module = aClass[:col]
            aClass = aClass[col + 1 :]

        theClass = getattr(sys.modules.get(module), aClass, None)
        if (theClass is None) and (col >= 0):
            try:
                mod = __import__(module, globals=globals(), level=1)
                for component in module.split(".")[1:]:
                    mod = getattr(mod, component)
                theClass = getattr(mod, aClass, None)
            except:
                pass

        return theClass

    def validate_class(self, aClass):
        return aClass

    def create_default_value(self, *args, **kw):
        aClass = args[0]
        if isinstance(aClass, six.string_types):
            aClass = self.validate_class(self.find_class(aClass))
            if aClass is None:
                raise TraitError("Unable to locate class: " + args[0])

        return aClass(*args[1:], **kw)


# -------------------------------------------------------------------------------
#  'TraitWeakRef' class:
# -------------------------------------------------------------------------------


class TraitWeakRef(TraitInstance):
    def _get(self, object, name):
        value = getattr(object, name + "_", None)
        if value is not None:
            return value.value()
        return None

    def _set(self, object, name, value):
        if value is not None:
            value = HandleWeakRef(object, name, value)
        object.__dict__[name + "_"] = value

    def resolve_class(self, object, name, value):
        # fixme: We have to override this method to prevent the 'fast validate'
        # from being set up, since the trait using this is a 'property' style
        # trait which is not currently compatible with the 'fast_validate'
        # style (causes internal Python SystemError messages).
        aClass = self.find_class(self.aClass)
        if aClass is None:
            self.validate_failed(object, name, value)
        self.aClass = aClass


# -- Private Class --------------------------------------------------------------


def _make_value_freed_callback(object_ref, name):
    def _value_freed(value_ref):
        object = object_ref()
        if object is not None:
            object.trait_property_changed(name, Undefined, None)

    return _value_freed


class HandleWeakRef(object):
    def __init__(self, object, name, value):
        object_ref = ref(object)
        _value_freed = _make_value_freed_callback(object_ref, name)
        self.object = object_ref
        self.name = name
        self.value = ref(value, _value_freed)


# -------------------------------------------------------------------------------
#  'TraitClass' class:
# -------------------------------------------------------------------------------


class TraitClass(TraitHandler):
    """Ensures that trait attribute values are subclasses of a specified class
    (or the class itself).

    A value is valid if it is a subclass of the specified class (including the
    class itself), or it is a string that is equivalent to the name of a valid
    class.
    """

    def __init__(self, aClass):
        """Creates a TraitClass handler.

        Parameters
        ----------
        aClass : class
            A Python class.

        Description
        -----------
        If *aClass* is an instance, it is mapped to the class it is an instance
        of.
        """
        if _py2to3.is_old_style_instance(aClass):
            aClass = aClass.__class__
        self.aClass = aClass

    def validate(self, object, name, value):
        try:
            if isinstance(value, six.string_types):
                value = value.strip()
                col = value.rfind(".")
                if col >= 0:
                    module_name = value[:col]
                    class_name = value[col + 1 :]
                    module = sys.modules.get(module_name)
                    if module is None:
                        exec("import " + module_name)
                        module = sys.modules[module_name]
                    value = getattr(module, class_name)
                else:
                    value = globals().get(value)

            if issubclass(value, self.aClass):
                return value
        except:
            pass

        self.error(object, name, value)

    def info(self):
        return "a subclass of " + self.aClass.__name__


# -------------------------------------------------------------------------------
#  'TraitFunction' class:
# -------------------------------------------------------------------------------


class TraitFunction(TraitHandler):
    """Ensures that assigned trait attribute values are acceptable to a
    specified validator function.

    TraitFunction is the underlying handler for the predefined trait
    **Function**, and for the use of function references as arguments to the
    Trait() function.
    """

    def __init__(self, aFunc):
        """ Creates a TraitFunction handler.

        Parameters
        ----------
        aFunc : function
            A function to validate trait attribute values.

        Description
        -----------
        The signature of the function passed as an argument must be of the
        form *function* ( *object*, *name*, *value* ). The function must
        verify that *value* is a legal value for the *name* trait attribute
        of *object*. If it is, the value returned by the function is the
        actual value assigned to the trait attribute. If it is not, the
        function must raise a TraitError exception.
        """
        if not isinstance(aFunc, CallableTypes):
            raise TraitError("Argument must be callable.")
        self.aFunc = aFunc
        self.fast_validate = (13, aFunc)

    def validate(self, object, name, value):
        try:
            return self.aFunc(object, name, value)
        except TraitError:
            self.error(object, name, value)

    def info(self):
        try:
            return self.aFunc.info
        except:
            if self.aFunc.__doc__:
                return self.aFunc.__doc__
            return "a legal value"


# -------------------------------------------------------------------------------
#  'TraitEnum' class:
# -------------------------------------------------------------------------------


class TraitEnum(TraitHandler):
    """ Ensures that a value assigned to a trait attribute is a member of a
    specified list of values.

    TraitEnum is the underlying handler for the forms of the Trait() function
    that take a list of possible values
    """

    def __init__(self, *values):
        """ Creates a TraitEnum handler.

        Parameters
        ----------
        values : list or tuple
            Enumeration of all legal values for a trait.

        Description
        -----------
        The list of legal values can be provided as a list of values. That is,
        ``TraitEnum([1, 2, 3])`` and ``TraitEnum(1, 2, 3)`` are equivalent. For
        example::

            class Flower(HasTraits):
                color = Trait('white', TraitEnum(['white', 'yellow', 'red']))
                kind  = Trait('annual', TraitEnum('annual', 'perennial'))

        This example defines a Flower class, which has a **color** trait
        attribute, which can have as its value, one of the three strings,
        'white', 'yellow', or 'red', and a **kind** trait attribute, which can
        have as its value, either of the strings 'annual' or 'perennial'. This
        is equivalent to the following class definition::

            class Flower(HasTraits):
                color = Trait(['white', 'yellow', 'red'])
                kind  = Trait('annual', 'perennial')

        The Trait() function automatically maps traits of the form shown in
        this example to the form shown in the preceding example whenever it
        encounters them in a trait definition.
        """
        if (len(values) == 1) and (type(values[0]) in SequenceTypes):
            values = values[0]
        self.values = tuple(values)
        self.fast_validate = (5, self.values)

    def validate(self, object, name, value):
        if value in self.values:
            return value
        self.error(object, name, value)

    def info(self):
        return " or ".join([repr(x) for x in self.values])

    def get_editor(self, trait):
        from traitsui.api import EnumEditor

        return EnumEditor(
            values=self,
            cols=trait.cols or 3,
            evaluate=trait.evaluate,
            mode=trait.mode or "radio",
        )


# -------------------------------------------------------------------------------
#  'TraitPrefixList' class:
# -------------------------------------------------------------------------------


class TraitPrefixList(TraitHandler):
    r"""Ensures that a value assigned to a trait attribute is a member of a list
    of specified string values, or is a unique prefix of one of those values.

    TraitPrefixList is a variation on TraitEnum. The values that can be
    assigned to a trait attribute defined using a TraitPrefixList handler is the
    set of all strings supplied to the TraitPrefixList constructor, as well as
    any unique prefix of those strings. That is, if the set of strings supplied
    to the constructor is described by [*s*\ :sub:`1`\ , *s*\ :sub:`2`\ , ...,
    *s*\ :sub:`n`\ ], then the string *v* is a valid value for the trait if
    *v* == *s*\ :sub:`i[:j]` for one and only one pair of values (i, j). If *v*
    is a valid value, then the actual value assigned to the trait attribute is
    the corresponding *s*\ :sub:`i` value that *v* matched.

    Example
    -------

    class Person(HasTraits):
        married = Trait('no', TraitPrefixList('yes', 'no')

    The Person class has a **married** trait that accepts any of the
    strings 'y', 'ye', 'yes', 'n', or 'no' as valid values. However, the actual
    values assigned as the value of the trait attribute are limited to either
    'yes' or 'no'. That is, if the value 'y' is assigned to the **married**
    attribute, the actual value assigned will be 'yes'.

    Note that the algorithm used by TraitPrefixList in determining whether a
    string is a valid value is fairly efficient in terms of both time and space,
    and is not based on a brute force set of comparisons.

    """

    def __init__(self, *values):
        """ Creates a TraitPrefixList handler.

        Parameters
        ----------
        values : list or tuple of strings
            Enumeration of all legal values for a trait.

        Description
        -----------
        As with TraitEnum, the list of legal values can be provided as a list
        of values.  That is, ``TraitPrefixList(['one', 'two', 'three'])`` and
        ``TraitPrefixList('one', 'two', 'three')`` are equivalent.
        """
        if (len(values) == 1) and (type(values[0]) in SequenceTypes):
            values = values[0]
        self.values = values[:]
        self.values_ = values_ = {}
        for key in values:
            values_[key] = key
        self.fast_validate = (10, values_, self.validate)

    def validate(self, object, name, value):
        try:
            if value not in self.values_:
                match = None
                n = len(value)
                for key in self.values:
                    if value == key[:n]:
                        if match is not None:
                            match = None
                            break
                        match = key
                if match is None:
                    self.error(object, name, value)
                self.values_[value] = match
            return self.values_[value]
        except:
            self.error(object, name, value)

    def info(self):
        return (
            " or ".join([repr(x) for x in self.values])
            + " (or any unique prefix)"
        )

    def get_editor(self, trait):
        from traitsui.api import EnumEditor

        return EnumEditor(values=self, cols=trait.cols or 3)

    def __getstate__(self):
        result = self.__dict__.copy()
        if "fast_validate" in result:
            del result["fast_validate"]

        return result


# -------------------------------------------------------------------------------
#  'TraitMap' class:
# -------------------------------------------------------------------------------


class TraitMap(TraitHandler):
    """Checks that the value assigned to a trait attribute is a key of a
    specified dictionary, and also assigns the dictionary value corresponding
    to that key to a *shadow* attribute.

    A trait attribute that uses a TraitMap handler is called *mapped* trait
    attribute. In practice, this means that the resulting object actually
    contains two attributes: one whose value is a key of the TraitMap
    dictionary, and the other whose value is the corresponding value of the
    TraitMap dictionary. The name of the shadow attribute is simply the base
    attribute name with an underscore ('_') appended. Mapped trait attributes
    can be used to allow a variety of user-friendly input values to be mapped to
    a set of internal, program-friendly values.

    Example
    -------

        >>>class Person(HasTraits):
        ...    married = Trait('yes', TraitMap({'yes': 1, 'no': 0 })
        >>>
        >>>bob = Person()
        >>>print bob.married
        yes
        >>>print bob.married_
        1

    In this example, the default value of the **married** attribute of the
    Person class is 'yes'. Because this attribute is defined using
    TraitPrefixList, instances of Person have another attribute,
    **married_**, whose default value is 1, the dictionary value corresponding
    to the key 'yes'.
    """

    is_mapped = True

    def __init__(self, map):
        """ Creates a TraitMap handler.

        Parameters
        ----------
        map : dict
            A dictionary whose keys are valid values for the trait attribute,
            and whose corresponding values are the values for the shadow
            trait attribute.
        """
        self.map = map
        self.fast_validate = (6, map)

    def validate(self, object, name, value):
        try:
            if value in self.map:
                return value
        except:
            pass

        self.error(object, name, value)

    def mapped_value(self, value):
        return self.map[value]

    def post_setattr(self, object, name, value):
        try:
            setattr(object, name + "_", self.mapped_value(value))
        except:
            # We don't need a fancy error message, because this exception
            # should always be caught by a TraitCompound handler:
            raise TraitError("Unmappable")

    def info(self):
        keys = sorted(repr(x) for x in self.map.keys())
        return " or ".join(keys)

    def get_editor(self, trait):
        from traitsui.api import EnumEditor

        return EnumEditor(values=self, cols=trait.cols or 3)


# -------------------------------------------------------------------------------
#  'TraitPrefixMap' class:
# -------------------------------------------------------------------------------


class TraitPrefixMap(TraitMap):
    """A cross between the TraitPrefixList and TraitMap classes.

    Like TraitMap, TraitPrefixMap is created using a dictionary, but in this
    case, the keys of the dictionary must be strings. Like TraitPrefixList,
    a string *v* is a valid value for the trait attribute if it is a prefix of
    one and only one key *k* in the dictionary. The actual values assigned to
    the trait attribute is *k*, and its corresponding mapped attribute is
    *map*[*k*].

    Example
    -------

        mapping = {'true': 1, 'yes': 1, 'false': 0, 'no': 0 }
        boolean_map = Trait('true', TraitPrefixMap(mapping))

    This example defines a Boolean trait that accepts any prefix of 'true',
    'yes', 'false', or 'no', and maps them to 1 or 0.
    """

    def __init__(self, map):
        """Creates a TraitPrefixMap handler.

        Parameters
        ----------
        map : dict
            A dictionary whose keys are strings that are valid values for the
            trait attribute, and whose corresponding values are the values for
            the shadow trait attribute.
        """
        self.map = map
        self._map = _map = {}
        for key in map.keys():
            _map[key] = key
        self.fast_validate = (10, _map, self.validate)

    def validate(self, object, name, value):
        try:
            if value not in self._map:
                match = None
                n = len(value)
                for key in self.map.keys():
                    if value == key[:n]:
                        if match is not None:
                            match = None
                            break
                        match = key
                if match is None:
                    self.error(object, name, value)
                self._map[value] = match
            return self._map[value]
        except:
            self.error(object, name, value)

    def info(self):
        return super(TraitPrefixMap, self).info() + " (or any unique prefix)"


# -------------------------------------------------------------------------------
#  'TraitExpression' class:
# -------------------------------------------------------------------------------


class TraitExpression(TraitHandler):
    """ Ensures that a value assigned to a trait attribute is a valid Python
        expression. The compiled form of a valid expression is stored as the
        mapped value of the trait.
    """

    is_mapped = True

    def validate(self, object, name, value):
        try:
            compile(value, "<string>", "eval")
            return value
        except:
            self.error(object, name, value)

    def post_setattr(self, object, name, value):
        object.__dict__[name + "_"] = self.mapped_value(value)

    def info(self):
        return "a valid Python expression"

    def mapped_value(self, value):
        return compile(value, "<string>", "eval")


# -------------------------------------------------------------------------------
#  'TraitCompound' class:
# -------------------------------------------------------------------------------


class TraitCompound(TraitHandler):
    """ Provides a logical-OR combination of other trait handlers.

    This class provides a means of creating complex trait definitions by
    combining several simpler trait definitions. TraitCompound is the underlying
    handler for the general forms of the Trait() function.

    A value is a valid value for a trait attribute based on a TraitCompound
    instance if the value is valid for at least one of the TraitHandler or
    trait objects supplied to the constructor. In addition, if at least one of
    the TraitHandler or trait objects is mapped (e.g., based on a TraitMap or
    TraitPrefixMap instance), then the TraitCompound is also mapped. In this
    case, any non-mapped traits or trait handlers use identity mapping.

    """

    def __init__(self, *handlers):
        """ Creates a TraitCompound handler.

        Parameters
        ----------
        *handlers :
            list or tuple of TraitHandler or trait objects to be combined.

        """
        if (len(handlers) == 1) and (type(handlers[0]) in SequenceTypes):
            handlers = handlers[0]
        self.handlers = handlers
        self.set_validate()

    def set_validate(self):
        self.is_mapped = False
        self.has_items = False
        self.reversable = True
        post_setattrs = []
        mapped_handlers = []
        validates = []
        fast_validates = []
        slow_validates = []

        for handler in self.handlers:
            fv = getattr(handler, "fast_validate", None)
            if fv is not None:
                validates.append(handler.validate)
                if fv[0] == 7:
                    # If this is a nested complex fast validator, expand its
                    # contents and adds its list to our list:
                    fast_validates.extend(fv[1])
                else:
                    # Else just add the entire validator to the list:
                    fast_validates.append(fv)
            else:
                slow_validates.append(handler.validate)

            post_setattr = getattr(handler, "post_setattr", None)
            if post_setattr is not None:
                post_setattrs.append(post_setattr)

            if handler.is_mapped:
                self.is_mapped = True
                mapped_handlers.append(handler)
            else:
                self.reversable = False

            if handler.has_items:
                self.has_items = True

        self.validates = validates
        self.slow_validates = slow_validates

        if self.is_mapped:
            self.mapped_handlers = mapped_handlers
        elif hasattr(self, "mapped_handlers"):
            del self.mapped_handlers

        # If there are any fast validators, then we create a 'complex' fast
        # validator that composites them:
        if len(fast_validates) > 0:
            # If there are any 'slow' validators, add a special handler at
            # the end of the fast validator list to handle them:
            if len(slow_validates) > 0:
                fast_validates.append((8, self))
            # Create the 'complex' fast validator:
            self.fast_validate = (7, tuple(fast_validates))
        elif hasattr(self, "fast_validate"):
            del self.fast_validate

        if len(post_setattrs) > 0:
            self.post_setattrs = post_setattrs
            self.post_setattr = self._post_setattr
        elif hasattr(self, "post_setattr"):
            del self.post_setattr

    def validate(self, object, name, value):
        for validate in self.validates:
            try:
                return validate(object, name, value)
            except TraitError:
                pass
        return self.slow_validate(object, name, value)

    def slow_validate(self, object, name, value):
        for validate in self.slow_validates:
            try:
                return validate(object, name, value)
            except TraitError:
                pass
        self.error(object, name, value)

    def full_info(self, object, name, value):
        return " or ".join(
            [x.full_info(object, name, value) for x in self.handlers]
        )

    def info(self):
        return " or ".join([x.info() for x in self.handlers])

    def mapped_value(self, value):
        for handler in self.mapped_handlers:
            try:
                return handler.mapped_value(value)
            except:
                pass
        return value

    def _post_setattr(self, object, name, value):
        for post_setattr in self.post_setattrs:
            try:
                post_setattr(object, name, value)
                return
            except TraitError:
                pass
        setattr(object, name + "_", value)

    def get_editor(self, trait):
        from traitsui.api import TextEditor, CompoundEditor

        the_editors = [x.get_editor(trait) for x in self.handlers]
        text_editor = TextEditor()
        count = 0
        editors = []
        for editor in the_editors:
            if isinstance(text_editor, editor.__class__):
                count += 1
                if count > 1:
                    continue
            editors.append(editor)

        return CompoundEditor(editors=editors)

    def items_event(self):
        return items_event()


# -------------------------------------------------------------------------------
#  'TraitTuple' class:
# -------------------------------------------------------------------------------


class TraitTuple(TraitHandler):
    """ Ensures that values assigned to a trait attribute are tuples of a
    specified length, with elements that are of specified types.

    TraitTuple is the underlying handler for the predefined trait **Tuple**,
    and the trait factory Tuple().

    Example
    -------

        rank = Range(1, 13)
        suit = Trait('Hearts', 'Diamonds', 'Spades', 'Clubs')
        class Card(HasTraits):
            value = Trait(TraitTuple(rank, suit))

    This example defines a Card class, which has a **value** trait attribute,
    which must be a tuple of two elments. The first element must be an integer
    in the range from 1 to 13, and the second element must be one of the four
    strings, 'Hearts', 'Diamonds', 'Spades', or 'Clubs'.
    """

    def __init__(self, *args):
        r""" Creates a TraitTuple handler.

        Parameters
        ----------
        *args :
            A list of traits, each *trait*\ :sub:`i` specifies the type that
            the *i*\ th element of a tuple must be.

        Description
        -----------
        Each *trait*\ :sub:`i` must be either a trait, or a value that can be
        converted to a trait using the Trait() function. The resulting
        trait handler accepts values that are tuples of the same length as
        *args*, and whose *i*\ th element is of the type specified by
        *trait*\ :sub:`i`.
        """
        self.types = tuple([trait_from(arg) for arg in args])
        self.fast_validate = (9, self.types)

    def validate(self, object, name, value):
        try:
            if isinstance(value, tuple):
                types = self.types
                if len(value) == len(types):
                    values = []
                    for i, type in enumerate(types):
                        values.append(
                            type.handler.validate(object, name, value[i])
                        )
                    return tuple(values)
        except:
            pass

        self.error(object, name, value)

    def full_info(self, object, name, value):
        return "a tuple of the form: (%s)" % (
            ", ".join(
                [
                    self._trait_info(type, object, name, value)
                    for type in self.types
                ]
            )
        )

    def _trait_info(self, type, object, name, value):
        handler = type.handler
        if handler is None:
            return "any value"

        return handler.full_info(object, name, value)

    def get_editor(self, trait):
        from traitsui.api import TupleEditor

        return TupleEditor(
            types=self.types, labels=trait.labels or [], cols=trait.cols or 1
        )


# -------------------------------------------------------------------------------
#  'TraitCallable' class:
# -------------------------------------------------------------------------------


class TraitCallable(TraitHandler):
    """Ensures that the value of a trait attribute is a callable Python object
    (usually a function or method).
    """

    def validate(self, object, name, value):
        if (value is None) or callable(value):
            return value
        self.error(object, name, value)

    def info(self):
        return "a callable value"


# -------------------------------------------------------------------------------
#  'TraitListEvent' class:
# -------------------------------------------------------------------------------


class TraitListEvent(object):

    # ---------------------------------------------------------------------------
    #  Initialize the object:
    # ---------------------------------------------------------------------------

    def __init__(self, index=0, removed=None, added=None):
        self.index = index

        if removed is None:
            removed = []
        self.removed = removed

        if added is None:
            added = []
        self.added = added


# -------------------------------------------------------------------------------
#  'TraitList' class:
# -------------------------------------------------------------------------------


class TraitList(TraitHandler):
    """ Ensures that a value assigned to a trait attribute is a list containing
    elements of a specified type, and that the length of the list is also
    within a specified range.

    TraitList also makes sure that any changes made to the list after it is
    assigned to the trait attribute do not violate the list's type and length
    constraints. TraitList is the underlying handler for the predefined
    list-based traits.

    Example
    -------

    class Card(HasTraits):
        pass
    class Hand(HasTraits):
        cards = Trait([], TraitList(Trait(Card), maxlen=52))


    This example defines a Hand class, which has a **cards** trait attribute,
    which is a list of Card objects and can have from 0 to 52 items in the
    list.
    """

    info_trait = None
    default_value_type = TRAIT_LIST_OBJECT_DEFAULT_VALUE
    _items_event = None

    def __init__(
        self, trait=None, minlen=0, maxlen=six.MAXSIZE, has_items=True
    ):
        """ Creates a TraitList handler.

        Parameters
        ----------
        trait : Trait
            The type of items the list can contain.
        minlen : int
            The minimum length of the list.
        maxlen : int
            The maximum length of the list.
        has_items : bool
            Flag indicating whether the list contains elements.

        Description
        -----------
        If *trait* is None or omitted, then no type checking is performed
        on any items in the list; otherwise, *trait* must be either a trait, or
        a value that can be converted to a trait using the Trait() function.

        """
        self.item_trait = trait_from(trait)
        self.minlen = max(0, minlen)
        self.maxlen = max(minlen, maxlen)
        self.has_items = has_items

    def clone(self):
        return TraitList(
            self.item_trait, self.minlen, self.maxlen, self.has_items
        )

    def validate(self, object, name, value):
        if isinstance(value, list) and (
            self.minlen <= len(value) <= self.maxlen
        ):
            return TraitListObject(self, object, name, value)

        self.error(object, name, value)

    def full_info(self, object, name, value):
        if self.minlen == 0:
            if self.maxlen == six.MAXSIZE:
                size = "items"
            else:
                size = "at most %d items" % self.maxlen
        else:
            if self.maxlen == six.MAXSIZE:
                size = "at least %d items" % self.minlen
            else:
                size = "from %s to %s items" % (self.minlen, self.maxlen)
        handler = self.item_trait.handler
        if handler is None:
            info = ""
        else:
            info = " which are %s" % handler.full_info(object, name, value)

        return "a list of %s%s" % (size, info)

    def get_editor(self, trait):
        from traits.traits import list_editor

        return list_editor(trait, self)

    def items_event(self):
        return items_event()


def items_event():
    if TraitList._items_event is None:
        TraitList._items_event = Event(
            TraitListEvent, is_base=False
        ).as_ctrait()

    return TraitList._items_event


# -------------------------------------------------------------------------------
#  'TraitListObject' class:
# -------------------------------------------------------------------------------


class TraitListObject(list):
    def __init__(self, trait, object, name, value):
        self.trait = trait
        self.object = ref(object)
        self.name = name
        self.name_items = None
        if trait.has_items:
            self.name_items = name + "_items"

        # Do the validated 'setslice' assignment without raising an
        # 'items_changed' event:
        if trait.minlen <= len(value) <= trait.maxlen:
            try:
                validate = trait.item_trait.handler.validate
                if validate is not None:
                    value = [validate(object, name, val) for val in value]

                list.__setitem__(self, slice(0, 0), value)

                return

            except TraitError as excp:
                excp.set_prefix("Each element of the")
                raise excp

        self.len_error(len(value))

    def _send_trait_items_event(self, name, event, items_event=None):
        """ Send a TraitListEvent to the owning object if there is one.
        """
        object = self.object()
        if object is not None:
            if items_event is None and hasattr(self, "trait"):
                items_event = self.trait.items_event()
            object.trait_items_event(name, event, items_event)

    def __deepcopy__(self, memo):
        id_self = id(self)
        if id_self in memo:
            return memo[id_self]

        memo[id_self] = result = TraitListObject(
            self.trait,
            lambda: None,
            self.name,
            [copy.deepcopy(x, memo) for x in self],
        )

        return result

    def __setitem__(self, key, value):
        self_trait = getattr(self, "trait", None)
        if self_trait is None:
            return list.__setitem__(self, key, value)
        try:
            removed = self[key]
        except:
            removed = []
        try:
            object = self.object()
            validate = self.trait.item_trait.handler.validate
            name = self.name

            if isinstance(key, slice):
                values = value
                slice_len = len(removed)

                delta = len(values) - slice_len
                step = 1 if key.step is None else key.step
                if step != 1 and delta != 0:
                    raise ValueError(
                        "attempt to assign sequence of size %d to extended slice of size %d"
                        % (len(values), slice_len)
                    )
                newlen = len(self) + delta
                if not (self_trait.minlen <= newlen <= self_trait.maxlen):
                    self.len_error(newlen)
                    return

                if validate is not None:
                    values = [
                        validate(object, name, value) for value in values
                    ]
                value = values
                if step == 1:
                    # FIXME: Bug-for-bug compatibility with old __setslice__ code.
                    # In this case, we return a TraitListEvent with an
                    # index=key.start and the removed and added lists as they
                    # are.
                    index = 0 if key.start is None else key.start
                else:
                    # Otherwise, we have an extended slice which was handled,
                    # badly, by __setitem__ before. In this case, we return the
                    # removed and added lists wrapped in another list.
                    index = key
                    values = [values]
                    removed = [removed]
            else:
                if validate is not None:
                    value = validate(object, name, value)

                values = [value]
                removed = [removed]
                delta = 0

                index = len(self) + key if key < 0 else key

            list.__setitem__(self, key, value)
            if self.name_items is not None:
                if delta == 0:
                    try:
                        if removed == values:
                            return
                    except:
                        # Treat incomparable values as equal:
                        pass
                self._send_trait_items_event(
                    self.name_items, TraitListEvent(index, removed, values)
                )

        except TraitError as excp:
            excp.set_prefix("Each element of the")
            raise excp

    if six.PY2:

        def __setslice__(self, i, j, values):
            self.__setitem__(slice(i, j), values)

    def __delitem__(self, key):
        trait = getattr(self, "trait", None)
        if trait is None:
            return list.__delitem__(self, key)

        try:
            removed = self[key]
        except:
            removed = []

        if isinstance(key, slice):
            slice_len = len(removed)
            delta = slice_len
            step = 1 if key.step is None else key.step
            if step == 1:
                # FIXME: See corresponding comment in __setitem__() for
                # explanation.
                index = 0 if key.start is None else key.start
            else:
                index = key
                removed = [removed]
        else:
            delta = 1
            index = len(self) + key + 1 if key < 0 else key
            removed = [removed]

        if not (trait.minlen <= (len(self) - delta)):
            self.len_error(len(self) - delta)
            return

        list.__delitem__(self, key)

        if self.name_items is not None:
            self._send_trait_items_event(
                self.name_items, TraitListEvent(index, removed)
            )

    if six.PY2:

        def __delslice__(self, i, j):
            self.__delitem__(slice(i, j))

    def __iadd__(self, other):
        self.extend(other)
        return self

    def __imul__(self, count):
        trait = getattr(self, "trait", None)
        if trait is None:
            return list.__imul__(self, count)

        original_len = len(self)

        if trait.minlen <= original_len * count <= trait.maxlen:
            if self.name_items is not None:
                removed = None if count else self[:]

            result = list.__imul__(self, count)

            if self.name_items is not None:
                added = self[original_len:] if count else None
                index = original_len if count else 0
                self._send_trait_items_event(
                    self.name_items, TraitListEvent(index, removed, added)
                )

            return result
        else:
            self.len_error(original_len * count)

    def append(self, value):
        trait = getattr(self, "trait", None)
        if trait is None:
            list.append(self, value)
            return

        if trait.minlen <= (len(self) + 1) <= trait.maxlen:
            try:
                validate = trait.item_trait.handler.validate
                object = self.object()
                if validate is not None:
                    value = validate(object, self.name, value)
                list.append(self, value)
                if self.name_items is not None:
                    self._send_trait_items_event(
                        self.name_items,
                        TraitListEvent(len(self) - 1, None, [value]),
                        trait.items_event(),
                    )
                return

            except TraitError as excp:
                excp.set_prefix("Each element of the")
                raise excp

        self.len_error(len(self) + 1)

    def insert(self, index, value):
        trait = getattr(self, "trait", None)
        if trait is None:
            return list.insert(self, index, value)
        if trait.minlen <= (len(self) + 1) <= trait.maxlen:
            try:
                validate = trait.item_trait.handler.validate
                object = self.object()
                if validate is not None:
                    value = validate(object, self.name, value)

                list.insert(self, index, value)

                if self.name_items is not None:
                    # Length before the insertion.
                    original_len = len(self) - 1

                    # Indices outside [-original_len, original_len] are clipped.
                    # This matches the behaviour of insert on the
                    # underlying list.
                    if index < 0:
                        index += original_len
                        if index < 0:
                            index = 0
                    elif index > original_len:
                        index = original_len

                    self._send_trait_items_event(
                        self.name_items,
                        TraitListEvent(index, None, [value]),
                        trait.items_event(),
                    )

                return

            except TraitError as excp:
                excp.set_prefix("Each element of the")
                raise excp

        self.len_error(len(self) + 1)

    def extend(self, xlist):
        trait = getattr(self, "trait", None)
        if trait is None:
            list.extend(self, xlist)

            return

        try:
            len_xlist = len(xlist)
        except:
            raise TypeError("list.extend() argument must be iterable")

        if trait.minlen <= (len(self) + len_xlist) <= trait.maxlen:
            object = self.object()
            name = self.name
            validate = trait.item_trait.handler.validate
            try:
                if validate is not None:
                    xlist = [validate(object, name, value) for value in xlist]

                list.extend(self, xlist)

                if (self.name_items is not None) and (len(xlist) != 0):
                    self._send_trait_items_event(
                        self.name_items,
                        TraitListEvent(len(self) - len(xlist), None, xlist),
                        trait.items_event(),
                    )

                return

            except TraitError as excp:
                excp.set_prefix("The elements of the")
                raise excp

        self.len_error(len(self) + len(xlist))

    def remove(self, value):
        trait = getattr(self, "trait", None)
        if trait is None:
            list.remove(self, value)
            return
        if trait.minlen < len(self):
            try:
                index = self.index(value)
                removed = [self[index]]
            except:
                pass

            list.remove(self, value)

            if self.name_items is not None:
                self._send_trait_items_event(
                    self.name_items, TraitListEvent(index, removed)
                )
        elif len(self) == 0:
            # Let whatever system error (ValueError) should be raised be raised.
            list.remove(self, value)
        else:
            self.len_error(len(self) - 1)

    if six.PY2:

        def sort(self, cmp=None, key=None, reverse=False):
            removed = self[:]
            list.sort(self, cmp=cmp, key=key, reverse=reverse)
            self._sort_common(removed)

    else:

        def sort(self, key=None, reverse=False):
            removed = self[:]
            list.sort(self, key=key, reverse=reverse)
            self._sort_common(removed)

    def _sort_common(self, removed):
        if (
            getattr(self, "name_items", None) is not None
            and getattr(self, "trait", None) is not None
        ):
            self._send_trait_items_event(
                self.name_items, TraitListEvent(0, removed, self[:])
            )

    def reverse(self):
        removed = self[:]
        if len(self) > 1:
            list.reverse(self)
            if self.name_items is not None:
                self._send_trait_items_event(
                    self.name_items, TraitListEvent(0, removed, self[:])
                )

    def pop(self, *args):
        if not hasattr(self, "trait"):
            return list.pop(self, *args)
        if self.trait.minlen < len(self):
            if len(args) > 0:
                index = args[0]
            else:
                index = -1

            try:
                removed = [self[index]]
            except:
                pass

            result = list.pop(self, *args)

            if self.name_items is not None:
                if index < 0:
                    index = len(self) + index + 1

                self._send_trait_items_event(
                    self.name_items, TraitListEvent(index, removed)
                )

            return result

        else:
            self.len_error(len(self) - 1)

    def rename(self, name):
        trait = self.object()._trait(name, 0)
        if trait is not None:
            self.name = name
            self.trait = trait.handler

    def len_error(self, len):
        raise TraitError(
            "The '%s' trait of %s instance must be %s, "
            "but you attempted to change its length to %d element%s."
            % (
                self.name,
                class_of(self.object()),
                self.trait.full_info(self.object(), self.name, Undefined),
                len,
                "s"[len == 1 :],
            )
        )

    def __getstate__(self):
        result = self.__dict__.copy()
        result.pop("object", None)
        result.pop("trait", None)

        return result

    def __setstate__(self, state):
        name = state.setdefault("name", "")
        object = state.pop("object", None)
        if object is not None:
            self.object = ref(object)
            self.rename(name)
        else:
            self.object = lambda: None

        self.__dict__.update(state)


# -------------------------------------------------------------------------------
#  'TraitSetEvent' class:
# -------------------------------------------------------------------------------


class TraitSetEvent(object):

    # ---------------------------------------------------------------------------
    #  Initialize the object:
    # ---------------------------------------------------------------------------

    def __init__(self, removed=None, added=None):
        if removed is None:
            removed = set()
        self.removed = removed

        if added is None:
            added = set()
        self.added = added


# -------------------------------------------------------------------------------
#  'TraitSetObject' class:
# -------------------------------------------------------------------------------


class TraitSetObject(set):
    def __init__(self, trait, object, name, value):
        self.trait = trait
        self.object = ref(object)
        self.name = name
        self.name_items = None
        if trait.has_items:
            self.name_items = name + "_items"

        # Validate and assign the initial set value:
        try:
            validate = trait.item_trait.handler.validate
            if validate is not None:
                value = [validate(object, name, val) for val in value]

            super(TraitSetObject, self).__init__(value)

            return

        except TraitError as excp:
            excp.set_prefix("Each element of the")
            raise excp

    def _send_trait_items_event(self, name, event, items_event=None):
        """ Send a TraitDictEvent to the owning object if there is one.
        """
        object = self.object()
        if object is not None:
            if items_event is None and hasattr(self, "trait"):
                items_event = self.trait.items_event()
            object.trait_items_event(name, event, items_event)

    def __deepcopy__(self, memo):
        id_self = id(self)
        if id_self in memo:
            return memo[id_self]

        memo[id_self] = result = TraitSetObject(
            self.trait,
            lambda: None,
            self.name,
            [copy.deepcopy(x, memo) for x in self],
        )

        return result

    def update(self, value):
        if not hasattr(self, "trait"):
            return set.update(self, value)
        try:
            if not isinstance(value, set):
                value = set(value)
            added = value.difference(self)
            if len(added) > 0:
                object = self.object()
                validate = self.trait.item_trait.handler.validate
                if validate is not None:
                    name = self.name
                    added = set(
                        [validate(object, name, item) for item in added]
                    )

                set.update(self, added)

                if self.name_items is not None:
                    self._send_trait_items_event(
                        self.name_items, TraitSetEvent(None, added)
                    )
        except TraitError as excp:
            excp.set_prefix("Each element of the")
            raise excp

    def intersection_update(self, value):
        removed = self.difference(value)
        if len(removed) > 0:
            set.difference_update(self, removed)

            if self.name_items is not None:
                self._send_trait_items_event(
                    self.name_items, TraitSetEvent(removed)
                )

    def difference_update(self, value):
        removed = self.intersection(value)
        if len(removed) > 0:
            set.difference_update(self, removed)

            if self.name_items is not None:
                self._send_trait_items_event(
                    self.name_items, TraitSetEvent(removed)
                )

    def symmetric_difference_update(self, value):
        if not hasattr(self, "trait"):
            return set.symmetric_difference_update(self, value)
        if not isinstance(value, set):
            value = set(value)
        removed = self.intersection(value)
        added = value.difference(self)
        if (len(removed) > 0) or (len(added) > 0):
            object = self.object()
            set.difference_update(self, removed)

            if len(added) > 0:
                validate = self.trait.item_trait.handler.validate
                if validate is not None:
                    name = self.name
                    added = set(
                        [validate(object, name, item) for item in added]
                    )

                set.update(self, added)

            if self.name_items is not None:
                self._send_trait_items_event(
                    self.name_items, TraitSetEvent(removed, added)
                )

    def add(self, value):
        if not hasattr(self, "trait"):
            return set.add(self, value)
        if value not in self:
            try:
                object = self.object()
                validate = self.trait.item_trait.handler.validate
                if validate is not None:
                    value = validate(object, self.name, value)

                set.add(self, value)

                if self.name_items is not None:
                    self._send_trait_items_event(
                        self.name_items, TraitSetEvent(None, set([value]))
                    )
            except TraitError as excp:
                excp.set_prefix("Each element of the")
                raise excp

    def remove(self, value):
        set.remove(self, value)

        if self.name_items is not None:
            self._send_trait_items_event(
                self.name_items, TraitSetEvent(set([value]))
            )

    def discard(self, value):
        if value in self:
            self.remove(value)

    def pop(self):
        value = set.pop(self)

        if self.name_items is not None:
            self._send_trait_items_event(
                self.name_items, TraitSetEvent(set([value]))
            )

        return value

    def clear(self):
        removed = set(self)
        set.clear(self)

        if self.name_items is not None:
            self._send_trait_items_event(
                self.name_items, TraitSetEvent(removed)
            )

    def copy(self):
        """ Return a true ``set`` object with a copy of the data.
        """
        return set(self)

    def __reduce_ex__(self, protocol=None):
        """ Overridden to make sure we call our custom __getstate__.
        """
        return (
            sm.copyreg._reconstructor,
            (type(self), set, list(self)),
            self.__getstate__(),
        )

    def __getstate__(self):
        result = self.__dict__.copy()
        result.pop("object", None)
        result.pop("trait", None)
        return result

    def __setstate__(self, state):
        name = state.setdefault("name", "")
        object = state.pop("object", None)
        if object is not None:
            self.object = ref(object)
            self.rename(name)
        else:
            self.object = lambda: None

        self.__dict__.update(state)

    def __ior__(self, value):
        self.update(value)
        return self

    def __iand__(self, value):
        self.intersection_update(value)
        return self

    def __ixor__(self, value):
        self.symmetric_difference_update(value)
        return self

    def __isub__(self, value):
        self.difference_update(value)
        return self


# -------------------------------------------------------------------------------
#  'TraitDictEvent' class:
# -------------------------------------------------------------------------------


class TraitDictEvent(object):
    def __init__(self, added=None, changed=None, removed=None):
        """
        Parameters
        ----------
        added : dict
            New keys and values.
        changed : dict
            Updated keys and their previous values.
        removed : dict
            Old keys and values that were just removed.
        """
        # Construct new empty dicts every time instead of using a default value
        # in the method argument, just in case someone gets the bright idea of
        # modifying the dict they get in-place.
        if added is None:
            added = {}
        self.added = added

        if changed is None:
            changed = {}
        self.changed = changed

        if removed is None:
            removed = {}
        self.removed = removed


# -------------------------------------------------------------------------------
#  'TraitDict' class:
# -------------------------------------------------------------------------------


class TraitDict(TraitHandler):
    """ Ensures that values assigned to a trait attribute are dictionaries whose
    keys and values are of specified types.

    TraitDict also makes sure that any changes to keys or values made that are
    made after the dictionary is assigned to the trait attribute satisfy the
    type constraints. TraitDict is the underlying handler for the
    dictionary-based predefined traits, and the Dict() trait factory.

    Example
    -------

    class WorkoutClass(HasTraits):
        member_weights = Trait({}, TraitDict(str, float))


    This example defines a WorkoutClass class containing a *member_weights*
    trait attribute whose value must be a dictionary containing keys that
    are strings (i.e., the members' names) and whose associated values must
    be floats (i.e., their most recently recorded weight).
    """

    info_trait = None
    default_value_type = TRAIT_DICT_OBJECT_DEFAULT_VALUE
    _items_event = None

    def __init__(self, key_trait=None, value_trait=None, has_items=True):
        """ Creates a TraitDict handler.

        Parameters
        ----------
        key_trait : trait
            The type for the dictionary keys.
        value_trait : trait
            The type for the dictionary values.
        has_items : bool
            Flag indicating whether the dictionary contains entries.

        Description
        -----------
        If *key_trait* is None or omitted, the keys in the dictionary can
        be of any type. Otherwise, *key_trait* must be either a trait, or a
        value that can be converted to a trait using the Trait() function. In
        this case, all dictionary keys are checked to ensure that they are of
        the type specified by *key_trait*.

        If *value_trait* is None or omitted, the values in the dictionary
        can be of any type. Otherwise, *value_trait* must be either a trait, or
        a value that can be converted to a trait using the Trait() function.
        In this case, all dictionary values are checked to ensure that they are
        of the type specified by *value_trait*.

        """
        self.key_trait = trait_from(key_trait)
        self.value_trait = trait_from(value_trait)
        self.has_items = has_items
        handler = self.value_trait.handler
        if handler.has_items:
            handler = handler.clone()
            handler.has_items = False
        self.value_handler = handler

    def clone(self):
        return TraitDict(self.key_trait, self.value_trait, self.has_items)

    def validate(self, object, name, value):
        if isinstance(value, dict):
            return TraitDictObject(self, object, name, value)
        self.error(object, name, value)

    def full_info(self, object, name, value):
        extra = ""
        handler = self.key_trait.handler
        if handler is not None:
            extra = " with keys which are %s" % handler.full_info(
                object, name, value
            )
        handler = self.value_handler
        if handler is not None:
            if extra == "":
                extra = " with"
            else:
                extra += " and"
            extra += " values which are %s" % handler.full_info(
                object, name, value
            )
        return "a dictionary%s" % extra

    def get_editor(self, trait):
        if self.editor is None:
            from traitsui.api import TextEditor

            self.editor = TextEditor(evaluate=eval)

        return self.editor

    def items_event(self):
        if TraitDict._items_event is None:
            TraitDict._items_event = Event(
                TraitDictEvent, is_base=False
            ).as_ctrait()

        return TraitDict._items_event


# -------------------------------------------------------------------------------
#  'TraitDictObject' class:
# -------------------------------------------------------------------------------


class TraitDictObject(dict):
    def __init__(self, trait, object, name, value):
        self.trait = trait
        self.object = ref(object)
        self.name = name
        self.name_items = None
        if trait.has_items:
            self.name_items = name + "_items"

        if len(value) > 0:
            dict.update(self, self._validate_dic(value))

    def _send_trait_items_event(self, name, event, items_event=None):
        """ Send a TraitDictEvent to the owning object if there is one.
        """
        object = self.object()
        if object is not None:
            if items_event is None and hasattr(self, "trait"):
                items_event = self.trait.items_event()
            object.trait_items_event(name, event, items_event)

    def __deepcopy__(self, memo):
        id_self = id(self)
        if id_self in memo:
            return memo[id_self]

        memo[id_self] = result = TraitDictObject(
            self.trait,
            lambda: None,
            self.name,
            dict([copy.deepcopy(x, memo) for x in six.iteritems(self)]),
        )

        return result

    def __setitem__(self, key, value):
        trait = getattr(self, "trait", None)
        if trait is None:
            dict.__setitem__(self, key, value)
            return

        object = self.object()
        try:
            validate = trait.key_trait.handler.validate
            if validate is not None:
                key = validate(object, self.name, key)

        except TraitError as excp:
            excp.set_prefix("Each key of the")
            raise excp

        try:
            validate = trait.value_handler.validate
            if validate is not None:
                value = validate(object, self.name, value)

            if self.name_items is not None:
                if key in self:
                    added = None
                    old = self[key]
                    changed = {key: old}
                else:
                    added = {key: value}
                    changed = None

            dict.__setitem__(self, key, value)

            if self.name_items is not None:
                if added is None:
                    try:
                        if old == value:
                            return
                    except:
                        # Treat incomparable objects as unequal:
                        pass
                self._send_trait_items_event(
                    self.name_items,
                    TraitDictEvent(added, changed),
                    trait.items_event(),
                )

        except TraitError as excp:
            excp.set_prefix("Each value of the")
            raise excp

    def __delitem__(self, key):
        if self.name_items is not None:
            removed = {key: self[key]}

        dict.__delitem__(self, key)

        if self.name_items is not None:
            self._send_trait_items_event(
                self.name_items, TraitDictEvent(removed=removed)
            )

    def clear(self):
        if len(self) > 0:
            if self.name_items is not None:
                removed = self.copy()

            dict.clear(self)

            if self.name_items is not None:
                self._send_trait_items_event(
                    self.name_items, TraitDictEvent(removed=removed)
                )

    def update(self, dic):
        trait = getattr(self, "trait", None)
        if trait is None:
            dict.update(self, dic)
            return

        if len(dic) > 0:
            new_dic = self._validate_dic(dic)

            if self.name_items is not None:
                added = {}
                changed = {}
                for key, value in six.iteritems(new_dic):
                    if key in self:
                        changed[key] = self[key]
                    else:
                        added[key] = value

                dict.update(self, new_dic)

                self._send_trait_items_event(
                    self.name_items,
                    TraitDictEvent(added=added, changed=changed),
                )
            else:
                dict.update(self, new_dic)

    def setdefault(self, key, value=None):
        if key in self:
            return self[key]

        self[key] = value
        result = self[key]

        if self.name_items is not None:
            self._send_trait_items_event(
                self.name_items, TraitDictEvent(added={key: result})
            )

        return result

    def pop(self, key, value=Undefined):
        if (value is Undefined) or key in self:
            result = dict.pop(self, key)

            if self.name_items is not None:
                self._send_trait_items_event(
                    self.name_items, TraitDictEvent(removed={key: result})
                )

            return result

        return value

    def popitem(self):
        result = dict.popitem(self)

        if self.name_items is not None:
            self._send_trait_items_event(
                self.name_items, TraitDictEvent(removed={result[0]: result[1]})
            )

        return result

    def rename(self, name):
        trait = self.object()._trait(name, 0)
        if trait is not None:
            self.name = name
            self.trait = trait.handler
        else:
            logger.debug(
                "rename: No 'trait' in %s for '%s'" % (self.object(), name)
            )

    def __getstate__(self):
        result = self.__dict__.copy()
        result.pop("object", None)
        result.pop("trait", None)
        return result

    def __setstate__(self, state):
        name = state.setdefault("name", "")
        object = state.pop("object", None)
        if object is not None:
            self.object = ref(object)
            self.rename(name)
        else:
            self.object = lambda: None

        self.__dict__.update(state)

    # -- Private Methods ------------------------------------------------------------

    def _validate_dic(self, dic):
        name = self.name
        new_dic = {}

        key_validate = self.trait.key_trait.handler.validate
        if key_validate is None:
            key_validate = lambda object, name, key: key

        value_validate = self.trait.value_trait.handler.validate
        if value_validate is None:
            value_validate = lambda object, name, value: value

        object = self.object()
        for key, value in six.iteritems(dic):
            try:
                key = key_validate(object, name, key)
            except TraitError as excp:
                excp.set_prefix("Each key of the")
                raise excp

            try:
                value = value_validate(object, name, value)
            except TraitError as excp:
                excp.set_prefix("Each value of the")
                raise excp

            new_dic[key] = value

        return new_dic


# -------------------------------------------------------------------------------
#  Tell the C-based traits module about 'TraitListObject', 'TraitSetObject and
#  'TraitDictObject', and the PyProtocols 'adapt' function:
# -------------------------------------------------------------------------------

from . import ctraits

ctraits._list_classes(TraitListObject, TraitSetObject, TraitDictObject)


def _adapt_wrapper(*args, **kw):
    # We need this wrapper to defer the import of 'adapt' and avoid a circular
    # import. The ctraits 'adapt' callback needs to be set as soon as possible,
    # but the adaptation mechanism relies on traits.

    # This wrapper is called once, after which we set the ctraits callback
    # to point directly to 'adapt'.

    from traits.adaptation.api import adapt

    ctraits._adapt(adapt)
    return adapt(*args, **kw)


ctraits._adapt(_adapt_wrapper)
