# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Defines a standard set of TraitHandler subclasses.

A trait handler mediates the assignment of values to object traits. It
verifies (via its validate() method) that a specified value is consistent
with the object trait, and generates a TraitError exception if it is not
consistent.
"""

from importlib import import_module
import sys
from types import FunctionType, MethodType

from .constants import DefaultValue, ValidateTrait
from .trait_base import (
    SequenceTypes,
    TypeTypes,
    class_of,
)
from .trait_base import RangeTypes  # noqa: F401, used by TraitsUI
from .trait_errors import TraitError
from .trait_dict_object import TraitDictEvent, TraitDictObject
from .trait_converters import trait_from
from .trait_handler import TraitHandler
from .trait_list_object import TraitListEvent, TraitListObject
from .util.deprecated import deprecated

# Constants

CallableTypes = (FunctionType, MethodType)

# Mapping of coercable types.
CoercableTypes = {
    float: (ValidateTrait.coerce, float, int),
    complex: (ValidateTrait.coerce, complex, float, int),
}

_WARNING_FORMAT_STR = ("'{handler}' trait handler has been deprecated. "
                       "Use {replacement} instead.")


# Private functions

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
    ============ =================

    Parameters
    ----------
    aType : type or object
        Either a Python type or a Python value.  If this is an object, it is
        mapped to its corresponding type. For example, the string 'cat' is
        automatically mapped to ``str``.

    Attributes
    ----------
    aType : type
        A Python type to coerce values to.
   """

    def __init__(self, aType):
        if not isinstance(aType, type):
            aType = type(aType)
        self.aType = aType
        try:
            self.fast_validate = CoercableTypes[aType]
        except:
            self.fast_validate = (ValidateTrait.coerce, aType)

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

        >>> class Person(HasTraits):
        ...     weight = Float
        ...     cweight = CFloat
        ...
        >>> bill = Person()
        >>> bill.weight = 180    # OK, coerced to 180.0
        >>> bill.cweight = 180   # OK, cast to 180.0
        >>> bill.weight = '180'  # Error, invalid coercion
        >>> bill.cweight = '180' # OK, cast to float('180')

    Parameters
    ----------
    aType : type
        Either a Python type or a Python value.  If this is an object, it is
        mapped to its corresponding type. For example, the string 'cat' is
        automatically mapped to ``str``.

    Attributes
    ----------
    aType : type
        A Python type to cast values to.
    """

    def __init__(self, aType):
        if not isinstance(aType, type):
            aType = type(aType)
        self.aType = aType
        self.fast_validate = (ValidateTrait.cast, aType)

    def validate(self, object, name, value):
        # If the value is already the desired type, then return it:
        if type(value) is self.aType:
            return value

        # Else try to cast it to the specified type:
        try:
            return self.aType(value)
        except:
            self.error(object, name, value)


class TraitInstance(TraitHandler):
    """Ensures that trait attribute values belong to a specified Python type.

    Any trait that uses a TraitInstance handler ensures that its values belong
    to the specified type or class (or one of its subclasses). For example::

        class Employee(HasTraits):
            manager = Trait(None, TraitInstance(Employee, True))

    This example defines a class Employee, which has a **manager** trait
    attribute, which accepts either None or an instance of Employee
    as its value.

    TraitInstance ensures that assigned values are exactly of the type
    specified (i.e., no coercion is performed).

    Parameters
    ----------
    aClass : type, object or str
        A Python type or a string that identifies the type, or an object.
        If this is an object, it is mapped to the class it is an instance of.
        If this is a str, it is either the name  of a class in the module
        identified by the module parameter, or an identifier of the form
        "*module_name*[.*module_name*....].*class_name*".
    allow_none : bool
        Flag indicating whether None is accepted as a valid value.
    module : str
        The name of the module that the class belongs to.  This is ignored if
        the type is provided directly, or the str value is an identifier with
        '.'s in it.

    Attributes
    ----------
    aClass : type or str
        A Python type, or a string which identifies the type.  If this is a
        str, it is either the name of a class in the module identified by the
        module attribute, or an identifier of the form
        "*module_name*[.*module_name*....].*class_name*".  A string value will
        be replaced by the actual type object the first time the trait is used
        to validate an object.
    module : str
        The name of the module that the class belongs to.  This is ignored if
        the type is provided directly, or the str value is an identifier with
        '.'s in it.
    """

    def __init__(self, aClass, allow_none=True, module=""):
        self._allow_none = allow_none
        self.module = module
        if isinstance(aClass, str):
            self.aClass = aClass
        else:
            if not isinstance(aClass, type):
                aClass = aClass.__class__
            self.aClass = aClass
            self.set_fast_validate()

    def allow_none(self):
        """ Whether or not None is permitted as a valid value.

        Returns
        -------
        bool
            Whether or not None is a valid value.
        """
        self._allow_none = True
        if hasattr(self, "fast_validate"):
            self.set_fast_validate()

    def set_fast_validate(self):
        fast_validate = [ValidateTrait.instance, self.aClass]
        if self._allow_none:
            fast_validate = [ValidateTrait.instance, None, self.aClass]
        if self.aClass in TypeTypes:
            fast_validate[0] = ValidateTrait.type
        self.fast_validate = tuple(fast_validate)

    def validate(self, object, name, value):
        if value is None:
            if self._allow_none:
                return value
            else:
                self.error(object, name, value)

        if isinstance(self.aClass, str):
            self.resolve_class(object, name, value)

        if isinstance(value, self.aClass):
            return value

        self.error(object, name, value)

    def info(self):
        aClass = self.aClass
        if type(aClass) is not str:
            aClass = aClass.__name__

        result = class_of(aClass)

        if self._allow_none:
            return result + " or None"

        return result

    def resolve_class(self, object, name, value):
        aClass = self.validate_class(self.find_class(self.aClass))
        if aClass is None:
            self.error(object, name, value)
        self.aClass = aClass

        # fixme: The following is quite ugly, because it wants to try and fix
        # the trait referencing this handler to use the 'fast path' now that
        # the actual class has been resolved. The problem is finding the trait,
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

    def find_class(self, klass):
        module = self.module
        col = klass.rfind(".")
        if col >= 0:
            module = klass[:col]
            klass = klass[col + 1:]

        theClass = getattr(sys.modules.get(module), klass, None)
        if (theClass is None) and (col >= 0):
            try:
                mod = import_module(module)
                theClass = getattr(mod, klass, None)
            except Exception:
                pass

        return theClass

    def validate_class(self, aClass):
        return aClass

    def create_default_value(self, *args, **kw):
        aClass = args[0]
        if isinstance(aClass, str):
            aClass = self.validate_class(self.find_class(aClass))
            if aClass is None:
                raise TraitError("Unable to locate class: " + args[0])

        return aClass(*args[1:], **kw)

    def get_editor(self, trait):
        if self.editor is None:
            from traitsui.api import InstanceEditor

            self.editor = InstanceEditor(
                label=trait.label or "",
                view=trait.view or "",
                kind=trait.kind or "live",
            )
        return self.editor


class TraitFunction(TraitHandler):
    """Ensures that assigned trait attribute values are acceptable to a
    specified validator function.

    TraitFunction is the underlying handler for the predefined trait
    **Function**, and for the use of function references as arguments to the
    Trait() function.

    The signature of the function must be of the form *function*(*object*,
    *name*, *value*). The function must verify that *value* is a legal value
    for the *name* trait attribute of *object*.  If it is, the value returned
    by the function is the actual value assigned to the trait attribute. If it
    is not, the function must raise a TraitError exception.

    Parameters
    ----------
    aFunc : function
        A function to validate trait attribute values.

    Attributes
    ----------
    aFunc : function
        A function to validate trait attribute values.
    """

    def __init__(self, aFunc):
        if not isinstance(aFunc, CallableTypes):
            raise TraitError("Argument must be callable.")
        self.aFunc = aFunc
        self.fast_validate = (ValidateTrait.function, aFunc)

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


class TraitEnum(TraitHandler):
    """ Ensures that a value assigned to a trait attribute is a member of a
    specified list of values.

    TraitEnum is the underlying handler for the forms of the Trait() function
    that take a list of possible values

    The list of legal values can be provided as a list or tuple of values.
    That is, ``TraitEnum([1, 2, 3])``, ``TraitEnum((1, 2, 3))`` and
    ``TraitEnum(1, 2, 3)`` are equivalent. For example::

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

    Parameters
    ----------
    *values
        Either all legal values for the enumeration, or a single list or tuple
        of the legal values.

    Attributes
    ----------
    values : tuple
        Enumeration of all legal values for a trait.
    """

    def __init__(self, *values):
        if (len(values) == 1) and (type(values[0]) in SequenceTypes):
            values = values[0]
        self.values = tuple(values)
        self.fast_validate = (ValidateTrait.enum, self.values)

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


class TraitPrefixList(TraitHandler):
    r"""Ensures that a value assigned to a trait attribute is a member of a
    list of specified string values, or is a unique prefix of one of those
    values.

    TraitPrefixList is a variation on TraitEnum. The values that can be
    assigned to a trait attribute defined using a TraitPrefixList handler is
    the set of all strings supplied to the TraitPrefixList constructor, as well
    as any unique prefix of those strings. That is, if the set of strings
    supplied to the constructor is described by
    [*s*\ :sub:`1`\ , *s*\ :sub:`2`\ , ..., *s*\ :sub:`n`\ ], then the string
    *v* is a valid value for the trait if *v* == *s*\ :sub:`i[:j]` for one and
    only one pair of values (i, j). If *v* is a valid value, then the actual
    value assigned to the trait attribute is the corresponding *s*\ :sub:`i`
    value that *v* matched.

    As with TraitEnum, the list of legal values can be provided as a list
    or tuple of values.  That is, ``TraitPrefixList(['one', 'two', 'three'])``
    and ``TraitPrefixList('one', 'two', 'three')`` are equivalent.

    Example
    -------
    ::

        class Person(HasTraits):
            married = Trait('no', TraitPrefixList('yes', 'no')

    The Person class has a **married** trait that accepts any of the
    strings 'y', 'ye', 'yes', 'n', or 'no' as valid values. However, the actual
    values assigned as the value of the trait attribute are limited to either
    'yes' or 'no'. That is, if the value 'y' is assigned to the **married**
    attribute, the actual value assigned will be 'yes'.

    Note that the algorithm used by TraitPrefixList in determining whether a
    string is a valid value is fairly efficient in terms of both time and
    space, and is not based on a brute force set of comparisons.

    Parameters
    ----------
    *values
        Either all legal string values for the enumeration, or a single list
        or tuple of legal string values.

    Attributes
    ----------
    values : tuple of strings
        Enumeration of all legal values for a trait.
    """

    @deprecated(_WARNING_FORMAT_STR.format(
        handler="TraitPrefixList", replacement="PrefixList"))
    def __init__(self, *values):
        if (len(values) == 1) and (type(values[0]) in SequenceTypes):
            values = values[0]
        self.values = values[:]
        self.values_ = values_ = {}
        for key in values:
            values_[key] = key
        self.fast_validate = (ValidateTrait.prefix_map, values_, self.validate)

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


class TraitMap(TraitHandler):
    """ Checks that the value assigned to a trait attribute is a key of a
    specified dictionary, and also assigns the dictionary value corresponding
    to that key to a *shadow* attribute.

    A trait attribute that uses a TraitMap handler is called *mapped* trait
    attribute. In practice, this means that the resulting object actually
    contains two attributes: one whose value is a key of the TraitMap
    dictionary, and the other whose value is the corresponding value of the
    TraitMap dictionary. The name of the shadow attribute is simply the base
    attribute name with an underscore ('_') appended. Mapped trait attributes
    can be used to allow a variety of user-friendly input values to be mapped
    to a set of internal, program-friendly values.

    Example
    -------

    The following example defines a ``Person`` class::

        >>> class Person(HasTraits):
        ...     married = Trait('yes', TraitMap({'yes': 1, 'no': 0 })
        ...
        >>> bob = Person()
        >>> print bob.married
        yes
        >>> print bob.married_
        1

    In this example, the default value of the ``married`` attribute of the
    Person class is 'yes'. Because this attribute is defined using
    TraitPrefixList, instances of Person have another attribute,
    ``married_``, whose default value is 1, the dictionary value corresponding
    to the key 'yes'.

    Parameters
    ----------
    map : dict
        A dictionary whose keys are valid values for the trait attribute,
        and whose corresponding values are the values for the shadow
        trait attribute.

    Attributes
    ----------
    map : dict
        A dictionary whose keys are valid values for the trait attribute,
        and whose corresponding values are the values for the shadow
        trait attribute.
    """

    is_mapped = True

    def __init__(self, map):
        self.map = map
        self.fast_validate = (ValidateTrait.map, map)

    def validate(self, object, name, value):
        try:
            if value in self.map:
                return value
        except:
            pass

        self.error(object, name, value)

    def mapped_value(self, value):
        """ Get the mapped value for a value. """
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
    ::

        mapping = {'true': 1, 'yes': 1, 'false': 0, 'no': 0 }
        boolean_map = Trait('true', TraitPrefixMap(mapping))

    This example defines a Boolean trait that accepts any prefix of 'true',
    'yes', 'false', or 'no', and maps them to 1 or 0.

    Parameters
    ----------
    map : dict
        A dictionary whose keys are strings that are valid values for the
        trait attribute, and whose corresponding values are the values for
        the shadow trait attribute.

    Attributes
    ----------
    map : dict
        A dictionary whose keys are strings that are valid values for the
        trait attribute, and whose corresponding values are the values for
        the shadow trait attribute.
    """

    @deprecated(_WARNING_FORMAT_STR.format(
        handler="TraitPrefixMap", replacement="PrefixMap"))
    def __init__(self, map):
        self.map = map
        self._map = _map = {}
        for key in map.keys():
            _map[key] = key
        self.fast_validate = (ValidateTrait.prefix_map, _map, self.validate)

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
        return super().info() + " (or any unique prefix)"


class TraitCompound(TraitHandler):
    """ Provides a logical-OR combination of other trait handlers.

    This class provides a means of creating complex trait definitions by
    combining several simpler trait definitions. TraitCompound is the
    underlying handler for the general forms of the Trait() function.

    A value is a valid value for a trait attribute based on a TraitCompound
    instance if the value is valid for at least one of the TraitHandler or
    trait objects supplied to the constructor. In addition, if at least one of
    the TraitHandler or trait objects is mapped (e.g., based on a TraitMap or
    TraitPrefixMap instance), then the TraitCompound is also mapped. In this
    case, any non-mapped traits or trait handlers use identity mapping.

    Parameters
    ----------
    *handlers
        Either all TraitHandlers or trait objects to be combined, or a single
        list or tuple of TraitHandlers or trait objects.

    Attributes
    ----------
    handlers : list or tuple
        A list or tuple of TraitHandler or trait objects to be combined.
    """

    def __init__(self, *handlers):
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
                if fv[0] == ValidateTrait.complex:
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
                fast_validates.append((ValidateTrait.slow, self))
            # Create the 'complex' fast validator:
            self.fast_validate = (ValidateTrait.complex, tuple(fast_validates))
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


class TraitTuple(TraitHandler):
    r""" Ensures that values assigned to a trait attribute are tuples of a
    specified length, with elements that are of specified types.

    TraitTuple is the underlying handler for the predefined trait **Tuple**,
    and the trait factory Tuple().

    Example
    -------

    The following example defines a ``Card`` class::

        rank = Range(1, 13)
        suit = Trait('Hearts', 'Diamonds', 'Spades', 'Clubs')
        class Card(HasTraits):
            value = Trait(TraitTuple(rank, suit))

    The Card class has a **value** trait attribute,
    which must be a tuple of two elments. The first element must be an integer
    in the range from 1 to 13, and the second element must be one of the four
    strings, 'Hearts', 'Diamonds', 'Spades', or 'Clubs'.

    Parameters
    ----------
    *args
        The traits, each *trait*\ :sub:`i` specifies the type that
        the *i*\ th element of a tuple must be.  Each *trait*\ :sub:`i`
        must be either a trait, or a value that can be
        converted to a trait using the trait_from() function. The resulting
        trait handler accepts values that are tuples of the same length as
        *args*, and whose *i*\ th element is of the type specified by
        *trait*\ :sub:`i`.

    Parameters
    ----------
    types : tuple of CTrait instances
        The traits to use for each item in a validated tuple.
    """

    @deprecated(_WARNING_FORMAT_STR.format(
        handler="TraitTuple", replacement="Tuple"))
    def __init__(self, *args):
        self.types = tuple([trait_from(arg) for arg in args])
        self.fast_validate = (ValidateTrait.tuple, self.types)

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
    ::

        class Card(HasTraits):
            pass

        class Hand(HasTraits):
            cards = Trait([], TraitList(Trait(Card), maxlen=52))

    This example defines a Hand class, which has a **cards** trait attribute,
    which is a list of Card objects and can have from 0 to 52 items in the
    list.

    Parameters
    ----------
    trait : Trait
        The type of items the list can contain. If this is None or omitted,
        then no type checking is performed on any items in the list;
        otherwise, this must be either a trait, or a value that can be
        converted to a trait using the trait_from() function.
    minlen : int
        The minimum length of the list.
    maxlen : int
        The maximum length of the list.
    has_items : bool
        Flag indicating whether the list contains elements.

    Attributes
    ----------
    item_trait : CTrait or None
        The type of items the list can contain.  If None, no type checking is
        performed on the items of the list.
    minlen : int
        The minimum length of the list.
    maxlen : int
        The maximum length of the list.
    has_items : bool
        Flag indicating whether the list contains elements.
    """

    info_trait = None
    default_value_type = DefaultValue.trait_list_object
    _items_event = None

    @deprecated(_WARNING_FORMAT_STR.format(
        handler="TraitList", replacement="List"))
    def __init__(
        self, trait=None, minlen=0, maxlen=sys.maxsize, has_items=True
    ):
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
            if self.maxlen == sys.maxsize:
                size = "items"
            else:
                size = "at most %d items" % self.maxlen
        else:
            if self.maxlen == sys.maxsize:
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
        from traits.editor_factories import list_editor

        return list_editor(trait, self)

    def items_event(self):
        return items_event()


def items_event():
    from .trait_types import Event

    if TraitList._items_event is None:
        TraitList._items_event = Event(
            TraitListEvent, is_base=False
        ).as_ctrait()

    return TraitList._items_event


class TraitDict(TraitHandler):
    """ Ensures that values assigned to a trait attribute are dictionaries
    whose keys and values are of specified types.

    TraitDict also makes sure that any changes to keys or values made that are
    made after the dictionary is assigned to the trait attribute satisfy the
    type constraints. TraitDict is the underlying handler for the
    dictionary-based predefined traits, and the Dict() trait factory.

    Example
    -------
    ::

        class WorkoutClass(HasTraits):
            member_weights = Trait({}, TraitDict(str, float))


    This example defines a WorkoutClass class containing a *member_weights*
    trait attribute whose value must be a dictionary containing keys that
    are strings (i.e., the members' names) and whose associated values must
    be floats (i.e., their most recently recorded weight).

    Parameters
    ----------
    key_trait : trait
        The type for the dictionary keys.  If this is None or omitted, the
        keys in the dictionary can be of any type. Otherwise, this
        must be either a trait, or a value that can be converted to a trait
        using the trait_from() function. In this case, all dictionary keys are
        checked to ensure that they are of the type specified.
    value_trait : trait
        The type for the dictionary values.  If this is None or omitted, the
        values in the dictionary can be of any type. Otherwise, this must be
        either a trait, or a value that can be converted to a trait using the
        trait_from() function.  In this case, all dictionary values are
        checked to ensure that they are of the type specified.
    has_items : bool
        Flag indicating whether the dictionary contains entries.

    Attributes
    ----------
    key_trait : CTrait or TraitHandler or None
        The type for the dictionary keys.  If this is None then the keys are
        not validated.
    value_trait : CTrait or TraitHandler or None
        The type for the dictionary values.  If this is None then the values
        are not validated.
    value_handler : BaseTraitHandler or None
        The trait handler for the dictionary values.
    has_items : bool
        Flag indicating whether the dictionary contains entries.
    """

    info_trait = None
    default_value_type = DefaultValue.trait_list_object
    _items_event = None

    @deprecated(_WARNING_FORMAT_STR.format(
        handler="TraitDict", replacement="Dict"))
    def __init__(self, key_trait=None, value_trait=None, has_items=True):
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
        from .trait_types import Event

        if TraitDict._items_event is None:
            TraitDict._items_event = Event(
                TraitDictEvent, is_base=False
            ).as_ctrait()

        return TraitDict._items_event
