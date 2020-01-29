# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Core Trait definitions.
"""

import datetime
import enum
from importlib import import_module
import operator
import re
import sys
try:
    from os import fspath
except ImportError:
    fspath = None
from os.path import isfile, isdir
from types import FunctionType, MethodType, ModuleType
import uuid

from .constants import DefaultValue, TraitKind, ValidateTrait
from .trait_base import (
    strx,
    get_module_name,
    HandleWeakRef,
    class_of,
    enum_default,
    EnumTypes,
    RangeTypes,
    safe_contains,
    SequenceTypes,
    TypeTypes,
    Undefined,
    TraitsCache,
    xgetattr,
)
from .trait_converters import trait_from
from .trait_dict_object import TraitDictEvent, TraitDictObject
from .trait_errors import TraitError
from .trait_list_object import TraitListEvent, TraitListObject
from .trait_set_object import TraitSetEvent, TraitSetObject
from .trait_type import TraitType
from .traits import (
    Trait,
    _TraitMaker,
    _InstanceArgs,
)
from .util.import_symbol import import_symbol

# TraitsUI integration imports
from .editor_factories import (
    code_editor,
    html_editor,
    password_editor,
    shell_editor,
    date_editor,
    datetime_editor,
    time_editor,
    list_editor,
)


# -------------------------------------------------------------------------------
#  Constants:
# -------------------------------------------------------------------------------

MutableTypes = (list, dict)
SetTypes = SequenceTypes + (set,)

# -------------------------------------------------------------------------------
#  Numeric type fast validator definitions:
# -------------------------------------------------------------------------------

# A few words about the next block of code:

# The coerce validator is a generic validator for possibly coercible types
# (see validate_trait_coerce_type in ctraits.c).
#
# The tuples below are of the form
# (ValidateTrait.coerce, type1, [type2, type3, ...], [None, ctype1, [ctype2, ...]])
#
# 'type1' corresponds to the main type for the trait
# 'None' acts as the separator between 'types' and 'ctypes' (coercible types)
#
# The validation passes if:
# 1) The trait value type is (a subtype of) one of 'type1', 'type2',  ...
#    in which case the value is returned as-is
# or
# 2) The trait value type is (a subtype of) one of 'ctype1', 'ctype2', ...
#    in which case the value is returned coerced to trait type using
#    'return type1(value')

try:
    # The numpy enhanced definitions:
    from numpy import integer, floating, complexfloating, bool_

    int_fast_validate = (ValidateTrait.coerce, int, integer)
    float_fast_validate = (ValidateTrait.coerce, float, floating, None, int, integer)
    complex_fast_validate = (
        ValidateTrait.coerce,
        complex,
        complexfloating,
        None,
        float,
        floating,
        int,
        integer,
    )
    bool_fast_validate = (ValidateTrait.coerce, bool, None, bool_)
    # Tuple or single type suitable for an isinstance check.
    _BOOL_TYPES = (bool, bool_)
except ImportError:
    # The standard python definitions (without numpy):
    int_fast_validate = (ValidateTrait.coerce, int)
    float_fast_validate = (ValidateTrait.coerce, float, None, int)
    complex_fast_validate = (ValidateTrait.coerce, complex, None, float, int)
    bool_fast_validate = (ValidateTrait.coerce, bool)
    # Tuple or single type suitable for an isinstance check.
    _BOOL_TYPES = bool


def default_text_editor(trait, type=None):
    """ Returns a default text editor for a trait.

    Parameters
    ----------
    trait : TraitType
        The trait we are constructing the editor for.
    type : callable, optional
        A callable (usually a Python type) to use to evaluate the text content
        of the editor and return the correct type of value for the trait.

    Returns
    -------
    TextEditor
        A TraitsUI TextEditor instance for the trait.
    """
    auto_set = trait.auto_set
    if auto_set is None:
        auto_set = True

    enter_set = trait.enter_set or False

    from traitsui.api import TextEditor

    if type is None:
        return TextEditor(auto_set=auto_set, enter_set=enter_set)

    return TextEditor(auto_set=auto_set, enter_set=enter_set, evaluate=type)


# -------------------------------------------------------------------------------
# Generic validators
# -------------------------------------------------------------------------------

def _validate_int(value):
    """ Convert an integer-like Python object to an int, or raise TypeError.
    """
    if type(value) is int:
        return value
    else:
        return int(operator.index(value))


def _validate_float(value):
    """ Convert an arbitrary Python object to a float, or raise TypeError.
    """
    if type(value) is float:  # fast path for common case
        return value
    try:
        nb_float = type(value).__float__
    except AttributeError:
        raise TypeError(
            "Object of type {!r} not convertible to float".format(type(value))
        )
    return nb_float(value)


# -------------------------------------------------------------------------------
# Trait Types
# -------------------------------------------------------------------------------

class Any(TraitType):
    """ A trait type whose value can be anything.
    """

    #: The default value for the trait:
    default_value = None

    #: A description of the type of value this trait accepts:
    info_text = "any value"


class BaseInt(TraitType):
    """ A trait type whose value must be an int.

    Values which support the Python index protocol will validate and will be
    converted to the corresponding int value.
    """

    #: The function to use for evaluating strings to this type:
    evaluate = int

    #: The default value for the trait:
    default_value = 0

    #: A description of the type of value this trait accepts:
    info_text = "an integer"

    def validate(self, object, name, value):
        """ Validates that a specified value is valid for this trait.
        """
        try:
            return _validate_int(value)
        except TypeError:
            self.error(object, name, value)

    def create_editor(self):
        """ Returns the default traits UI editor for this type of trait.
        """
        return default_text_editor(self, int)


class Int(BaseInt):
    """ A fast-validating trait type whose value must be an integer.

    Values which support the Python index protocol will validate and will be
    converted to the corresponding int value.
    """

    #: The C-level fast validator to use:
    fast_validate = (ValidateTrait.int,)


class BaseFloat(TraitType):
    """ A trait type whose value must be a float.

    Values which support automatic conversion to floats via the Python
    __float__ method will validate and will be converted to the corresponding
    float value.
    """

    #: The function to use for evaluating strings to this type:
    evaluate = float

    #: The default value for the trait:
    default_value = 0.0

    #: A description of the type of value this trait accepts:
    info_text = "a float"

    def validate(self, object, name, value):
        """ Validates that a specified value is valid for this trait.

        Note: The 'fast validator' version performs this check in C.
        """
        try:
            return _validate_float(value)
        except TypeError:
            self.error(object, name, value)

    def create_editor(self):
        """ Returns the default traits UI editor for this type of trait.
        """
        return default_text_editor(self, float)


class Float(BaseFloat):
    """ A fast-validating trait type whose value must be a float.

    Values which support automatic conversion to floats via the Python
    __float__ method will validate and will be converted to the corresponding
    float value.
    """

    #: The C-level fast validator to use:
    fast_validate = (ValidateTrait.float,)


class BaseComplex(TraitType):
    """ A trait type whose value must be a complex number.

    Integers and floating point numbers will be converted to the
    corresponding complex value.
    """

    #: The function to use for evaluating strings to this type:
    evaluate = complex

    #: The default value for the trait:
    default_value = 0.0 + 0.0j

    #: A description of the type of value this trait accepts:
    info_text = "a complex number"

    def validate(self, object, name, value):
        """ Validates that a specified value is valid for this trait.

        Note: The 'fast validator' version performs this check in C.
        """
        if isinstance(value, complex):
            return value

        if isinstance(value, (float, int)):
            return complex(value)

        self.error(object, name, value)

    def create_editor(self):
        """ Returns the default traits UI editor for this type of trait.
        """
        return default_text_editor(self, complex)


class Complex(BaseComplex):
    """ A fast-validating trait type whose value must be a complex number.

    Integers and floating point numbers will be converted to the
    corresponding complex value.
    """

    #: The C-level fast validator to use:
    fast_validate = complex_fast_validate


class BaseStr(TraitType):
    """ A trait type whose value must be a string.
    """

    #: The default value for the trait:
    default_value = ""

    #: A description of the type of value this trait accepts:
    info_text = "a string"

    def validate(self, object, name, value):
        """ Validates that a specified value is valid for this trait.

        Note: The 'fast validator' version performs this check in C.
        """
        if isinstance(value, str):
            return value

        self.error(object, name, value)

    def create_editor(self):
        """ Returns the default traits UI editor for this type of trait.
        """
        from .editor_factories import multi_line_text_editor

        auto_set = self.auto_set
        if auto_set is None:
            auto_set = True
        enter_set = self.enter_set or False

        return multi_line_text_editor(auto_set, enter_set)


class Str(BaseStr):
    """ A fast-validating trait type whose value must be a complex number..
    """

    #: The C-level fast validator to use:
    fast_validate = (ValidateTrait.coerce, str)


class Title(Str):
    """ A Str trait which by default uses a TraitsUI TitleEditor.
    """

    def create_editor(self):
        """ Returns the default traits UI editor to use for a trait.
        """
        from traitsui.api import TitleEditor

        if hasattr(self, "allow_selection"):
            return TitleEditor(allow_selection=self.allow_selection)
        else:
            return TitleEditor()


class BaseBytes(TraitType):
    """ A trait type whose value must be a bytestring.
    """

    #: The default value for the trait:
    default_value = b""

    #: A description of the type of value this trait accepts:
    info_text = "a bytes string"

    #: An encoding to use with TraitsUI editors
    encoding = None

    def validate(self, object, name, value):
        """ Validates that a specified value is valid for this trait.

        Note: The 'fast validator' version performs this check in C.
        """
        if isinstance(value, bytes):
            return value

        self.error(object, name, value)

    def create_editor(self):
        """ Returns the default traits UI editor for this type of trait.
        """
        from .traits import bytes_editor

        auto_set = self.auto_set
        if auto_set is None:
            auto_set = True
        enter_set = self.enter_set or False

        return bytes_editor(auto_set, enter_set, self.encoding)


class Bytes(BaseBytes):
    """ A fast-validating trait type whose value must be a bytestring.
    """

    #: The C-level fast validator to use:
    fast_validate = (ValidateTrait.coerce, bytes)


class BaseBool(TraitType):
    """ A trait type whose value must be a bool.
    """

    #: The function to use for evaluating strings to this type:
    evaluate = bool

    #: The default value for the trait:
    default_value = False

    #: A description of the type of value this trait accepts:
    info_text = "a boolean"

    def validate(self, object, name, value):
        """ Validates that a specified value is valid for this trait.

        Note: The 'fast validator' version performs this check in C.
        """
        if isinstance(value, _BOOL_TYPES):
            return bool(value)

        self.error(object, name, value)

    def create_editor(self):
        """ Returns the default traits UI editor for this type of trait.
        """
        from traitsui.api import BooleanEditor

        return BooleanEditor()


class Bool(BaseBool):
    """ A fast-validating trait type whose value must be a bool.
    """

    #: The C-level fast validator to use:
    fast_validate = bool_fast_validate


class BaseCInt(BaseInt):
    """ A coercing trait type whose value is an integer.
    """

    #: The function to use for evaluating strings to this type:
    evaluate = int

    def validate(self, object, name, value):
        """ Validates that a specified value is valid for this trait.

        Note: The 'fast validator' version performs this check in C.
        """
        try:
            return int(value)
        except (ValueError, TypeError):
            self.error(object, name, value)


class CInt(BaseCInt):
    """ A fast-validating, coercing trait type whose value is an int.
    """

    #: The C-level fast validator to use:
    fast_validate = (ValidateTrait.cast, int)


class BaseCFloat(BaseFloat):
    """ A coercing trait type whose value is a float.
    """

    #: The function to use for evaluating strings to this type:
    evaluate = float

    def validate(self, object, name, value):
        """ Validates that a specified value is valid for this trait.

        Note: The 'fast validator' version performs this check in C.
        """
        try:
            return float(value)
        except (ValueError, TypeError):
            self.error(object, name, value)


class CFloat(BaseCFloat):
    """ A fast-validating, coercing trait type whose value is a float.
    """

    #: The C-level fast validator to use:
    fast_validate = (ValidateTrait.cast, float)


class BaseCComplex(BaseComplex):
    """ A coercing trait type whose value is a complex number.
    """

    #: The function to use for evaluating strings to this type:
    evaluate = complex

    def validate(self, object, name, value):
        """ Validates that a specified value is valid for this trait.

        Note: The 'fast validator' version performs this check in C.
        """
        try:
            return complex(value)
        except (ValueError, TypeError):
            self.error(object, name, value)


class CComplex(BaseCComplex):
    """ A fast-validating, coercing trait type whose value is a complex number.
    """

    #: The C-level fast validator to use:
    fast_validate = (ValidateTrait.cast, complex)


class BaseCStr(BaseStr):
    """ A coercing trait type whose value is a string.
    """

    def validate(self, object, name, value):
        """ Validates that a specified value is valid for this trait.

        Note: The 'fast validator' version performs this check in C.
        """
        try:
            return str(value)
        except:
            self.error(object, name, value)


class CStr(BaseCStr):
    """ A fast-validating, coercing trait type whose value is a string.
    """

    #: The C-level fast validator to use:
    fast_validate = (ValidateTrait.cast, str)


class BaseCBytes(BaseBytes):
    """ A coercing trait type whose value is a bytestring.
    """

    def validate(self, object, name, value):
        """ Validates that a specified value is valid for this trait.

        Note: The 'fast validator' version performs this check in C.
        """
        try:
            return bytes(value)
        except:
            self.error(object, name, value)


class CBytes(BaseCBytes):
    """ A fast-validating, coercing trait type whose value is a bytestring.
    """

    #: The C-level fast validator to use:
    fast_validate = (ValidateTrait.cast, bytes)


class BaseCBool(BaseBool):
    """ A coercing trait type whose value is a bool.
    """

    #: The function to use for evaluating strings to this type:
    evaluate = bool

    def validate(self, object, name, value):
        """ Validates that a specified value is valid for this trait.

        Note: The 'fast validator' version performs this check in C.
        """
        try:
            return bool(value)
        except:
            self.error(object, name, value)


class CBool(BaseCBool):
    """ A fast-validating, coercing trait type whose value is a bool.
    """

    #: The C-level fast validator to use:
    fast_validate = (ValidateTrait.cast, bool)


class String(TraitType):
    """ A trait type whose value must be a string with optional constraints.

    The value is a string whose length is in a specified range, and which
    optionally matches a specified regular expression.

    Parameters
    ----------
    value : str
        The default value for the string.
    minlen : integer
        The minimum length allowed for the string.
    maxlen : integer
        The maximum length allowed for the string.
    regex : str
        A Python regular expression that the string must match.
    **metadata
        The trait metadata for the trait.

    Attributes
    ----------
    minlen : integer
        The minimum length allowed for the string.
    maxlen : integer
        The maximum length allowed for the string.
    regex : str
        A Python regular expression that the string must match.
    """

    def __init__(
        self, value="", minlen=0, maxlen=sys.maxsize, regex="", **metadata
    ):
        super(String, self).__init__(value, **metadata)
        self.minlen = max(0, minlen)
        self.maxlen = max(self.minlen, maxlen)
        self.regex = regex
        self._init()

    def _init(self):
        """ Completes initialization of the trait at construction or unpickling
        time.
        """
        self._validate = "validate_all"
        if self.regex != "":
            self.match = re.compile(self.regex).match
            if (self.minlen == 0) and (self.maxlen == sys.maxsize):
                self._validate = "validate_regex"
        elif (self.minlen == 0) and (self.maxlen == sys.maxsize):
            self._validate = "validate_str"
        else:
            self._validate = "validate_len"

    def validate(self, object, name, value):
        """ Validates that the value is a valid string.
        """
        return getattr(self, self._validate)(object, name, value)

    def validate_all(self, object, name, value):
        """ Validates that the value is a valid string in the specified length
            range which matches the specified regular expression.
        """
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
        """ Validates that the value is a valid string.
        """
        try:
            return strx(value)
        except:
            pass

        self.error(object, name, value)

    def validate_len(self, object, name, value):
        """ Validates that the value is a valid string in the specified length
        range.
        """
        try:
            value = strx(value)
            if self.minlen <= len(value) <= self.maxlen:
                return value
        except:
            pass

        self.error(object, name, value)

    def validate_regex(self, object, name, value):
        """ Validates that the value is a valid string which matches the
        specified regular expression.
        """
        try:
            value = strx(value)
            if self.match(value) is not None:
                return value
        except:
            pass

        self.error(object, name, value)

    def info(self):
        """ Returns a description of the trait.
        """
        msg = ""
        if (self.minlen != 0) and (self.maxlen != sys.maxsize):
            msg = " between %d and %d characters long" % (
                self.minlen,
                self.maxlen,
            )
        elif self.maxlen != sys.maxsize:
            msg = " <= %d characters long" % self.maxlen
        elif self.minlen != 0:
            msg = " >= %d characters long" % self.minlen
        if self.regex != "":
            if msg != "":
                msg += " and"
            msg += " matching the pattern '%s'" % self.regex
        return "a string" + msg

    def create_editor(self):
        """ Returns the default traits UI editor for this type of trait.
        """
        return default_text_editor(self)

    def __getstate__(self):
        """ Returns the current state of the trait.
        """
        result = self.__dict__.copy()
        for name in ["validate", "match"]:
            if name in result:
                del result[name]

        return result

    def __setstate__(self, state):
        """ Sets the current state of the trait.
        """
        self.__dict__.update(state)
        self._init()


class Regex(String):
    """ A trait type whose value must match a regular expression.

    Parameters
    ----------
    value : str
        The default value of the trait.
    regex : str
        The regular expression that the trait value must match.
    **metadata
        Trait metadata.
    """

    def __init__(self, value="", regex=".*", **metadata):
        super(Regex, self).__init__(value=value, regex=regex, **metadata)


class Code(String):
    """ A trait type whose value holds a string of source code.

    Validation does not perform any sort of syntax checking. The default
    TraitsUI editor is a CodeEditor.
    """

    #: The standard metadata for the trait:
    metadata = {"editor": code_editor}


class HTML(String):
    """ A trait type whose value holds an HTML string.

    The validation of the value does not enforce HTML syntax.  The default
    TraitsUI editor is an HTMLEditor.
    """

    #: The standard metadata for the trait:
    metadata = {"editor": html_editor}


class Password(String):
    """ A trait type whose value holds a password string.

    The default TraitsUI editor is an PasswordEditor, which obscures text
    entered by the user.
    """

    #: The standard metadata for the trait:
    metadata = {"editor": password_editor}


class BaseCallable(TraitType):
    """ A trait type whose value must be a Python callable.
    """

    #: The standard metadata for the trait:
    metadata = {"copy": "ref"}

    #: The default value for the trait:
    default_value = None

    #: A description of the type of value this trait accepts:
    info_text = "a callable value"

    def validate(self, object, name, value):
        """ Validates that the value is a Python callable.
        """
        if (value is None) or callable(value):
            return value

        self.error(object, name, value)


class Callable(BaseCallable):
    """ A fast-validating trait type whose value must be a Python callable.
    """

    #: The C-level fast validator to use
    fast_validate = (ValidateTrait.callable,)


class BaseType(TraitType):
    """ A trait type whose value must be an instance of a Python type.

    This is an abstract class and should not be directly instantiated.
    """

    def validate(self, object, name, value):
        """ Validates that the value is a Python callable.
        """
        if isinstance(value, self.fast_validate[1:]):
            return value

        self.error(object, name, value)


class This(BaseType):
    """ A trait type whose value must be an instance of the defining class.
    """

    #: The C-level fast validator to use:
    fast_validate = (ValidateTrait.self_type,)

    #: A description of the type of value this trait accepts:
    info_text = "an instance of the same type as the receiver"

    def __init__(self, value=None, allow_none=True, **metadata):
        super(This, self).__init__(value, **metadata)

        if allow_none:
            self.fast_validate = (ValidateTrait.self_type, None)
            self.validate = self.validate_none
            self.info = self.info_none

    def validate(self, object, name, value):
        if isinstance(value, object.__class__):
            return value

        self.error(object, name, value)

    def validate_none(self, object, name, value):
        if isinstance(value, object.__class__) or (value is None):
            return value

        self.error(object, name, value)

    def info(self):
        return "an instance of the same type as the receiver"

    def info_none(self):
        return "an instance of the same type as the receiver or None"


class self(This):
    """ A trait type whose default value is the object containing the trait.

    The trait can be assigned to, but any new value must be an instance of
    the defining class.
    """

    #: The default value type to use (i.e. 'self'):
    default_value_type = DefaultValue.object


class Function(TraitType):
    """ A trait type whose value must be a function.
    """

    #: The C-level fast validator to use:
    fast_validate = (ValidateTrait.coerce, FunctionType)

    #: A description of the type of value this trait accepts:
    info_text = "a function"


class Method(TraitType):
    """ A trait type whose value must be a method.
    """

    #: The C-level fast validator to use:
    fast_validate = (ValidateTrait.coerce, MethodType)

    #: A description of the type of value this trait accepts:
    info_text = "a method"


class Module(TraitType):
    """ A trait type whose value must be a module.
    """

    #: The C-level fast validator to use:
    fast_validate = (ValidateTrait.coerce, ModuleType)

    #: A description of the type of value this trait accepts:
    info_text = "a module"


class Python(TraitType):
    """ A trait type that behaves as to a standard Python attribute.

    This trait type allows any value to be assigned, and raises an
    ValueError if an attempt is made to get the value before one has been
    assigned. It has no default value. This trait is most often used in
    conjunction with wildcard naming. See the *Traits User Manual* for
    details on wildcards.
    """

    #: The standard metadata for the trait:
    metadata = {"type": "python"}

    #: The default value for the trait:
    default_value = Undefined


class ReadOnly(TraitType):
    """ A trait type that is write-once, and then read-only.

    The initial value of the attribute is the special, singleton object
    Undefined. The trait allows any value to be assigned to the attribute
    if the current value is the Undefined object. Once any other value is
    assigned, no further assignment is allowed. Normally, the initial
    assignment to the attribute is performed in the class constructor,
    based on information passed to the constructor. If the read-only value
    is known in advance of run time, use Constant instead of ReadOnly to
    define the trait.
    """

    # Defines the CTrait type to use for this trait:
    ctrait_type = TraitKind.read_only

    #: The default value for the trait:
    default_value = Undefined


# Create a singleton instance as the trait:
ReadOnly = ReadOnly()


class Disallow(TraitType):
    """ A trait that prevents any value from being assigned or read.

    Any attempt to get or set the value of the trait attribute raises an
    exception. This trait is most often used in conjunction with wildcard
    naming, for example, to catch spelling mistakes in attribute names.

    See the *Traits User Manual* for details on wildcards.
    """

    #: Defines the CTrait type to use for this trait:
    ctrait_type = TraitKind.disallow


# Create a singleton instance as the trait:
Disallow = Disallow()


class Constant(TraitType):
    """ A trait type whose value is a constant.

    Traits of this type are very space efficient (and fast) because
    *value* is not stored in each instance using the trait, but only in
    the trait object itself. The *value* cannot be a list or dictionary,
    because those types have mutable values.

    Parameters
    ----------
    value : any type other than list or dict
        The constant value for the trait.
    **metadata
        Trait metadata for the trait.
    """

    #: Defines the CTrait type to use for this trait:
    ctrait_type = TraitKind.constant

    #: The standard metadata for the trait:
    metadata = {"type": "constant", "transient": True}

    def __init__(self, value, **metadata):
        if type(value) in MutableTypes:
            raise TraitError(
                "Cannot define a constant using a mutable list or dictionary"
            )

        super(Constant, self).__init__(value, **metadata)


class Delegate(TraitType):
    """ A trait type whose value is delegated to a trait on another object.

    This is a base class that shouldn't be used directly, rather use one of
    the subclasses DelegatesTo or PrototypesFrom, depending on desired
    behaviour.

    An object containing a delegator trait attribute must contain a
    second attribute that references the object containing the delegate
    trait attribute. The name of this second attribute is passed as the
    *delegate* argument.

    The following rules govern the application of the prefix parameter:

    * If *prefix* is empty or omitted, the delegation is to an attribute
      of the delegate object with the same name as the delegator
      attribute.
    * If *prefix* is a valid Python attribute name, then the delegation
      is to an attribute whose name is the value of *prefix*.
    * If *prefix* ends with an asterisk ('*') and is longer than one
      character, then the delegation is to an attribute whose name is
      the value of *prefix*, minus the trailing asterisk, prepended to
      the delegator attribute name.
    * If *prefix* is equal to a single asterisk, the delegation is to an
      attribute whose name is the value of the delegator object's
      __prefix__ attribute prepended to delegator attribute name.

    Parameters
    ----------
    delegate : str
        The name of the trait that holds the HasTraits instance that the
        value is delegated to.
    prefix : str
        The name of the trait on the delegate that holds the delegated
        value.  If empty, then the name of this trait will be used.
    modify : bool
        Whether modifications of this trait are applied to the delegated
        object.  This differentiates the behaviour of DelegatesTo and
        PrototypedFrom.
    listenable : bool
        Whether changes to the delegated trait will fire listeners to
        this trait.

    Attributes
    ----------
    delegate : str
        The name of the trait that holds the HasTraits instance that the
        value is delegated to.
    prefix : str
        The name of the trait on the delegate that holds the delegated
        value.  If empty, then the name of this trait will be used.
    prefix_type : int
        An integer giving the type of prefix being used.
    modify : bool
        Whether modifications of this trait are applied to the delegated
        object.  This differentiates the behaviour of DelegatesTo and
        PrototypedFrom.
    """

    #: Defines the CTrait type to use for this trait:
    ctrait_type = TraitKind.delegate

    #: The standard metadata for the trait:
    metadata = {"type": "delegate", "transient": False}

    def __init__(
        self, delegate, prefix="", modify=False, listenable=True, **metadata
    ):
        """ Creates a Delegate trait.
        """
        if prefix == "":
            prefix_type = 0
        elif prefix[-1:] != "*":
            prefix_type = 1
        else:
            prefix = prefix[:-1]
            if prefix != "":
                prefix_type = 2
            else:
                prefix_type = 3

        metadata["_delegate"] = delegate
        metadata["_prefix"] = prefix
        metadata["_listenable"] = listenable

        super(Delegate, self).__init__(**metadata)

        self.delegate = delegate
        self.prefix = prefix
        self.prefix_type = prefix_type
        self.modify = modify

    def as_ctrait(self):
        """ Returns a CTrait corresponding to the trait defined by this class.
        """
        trait = super(Delegate, self).as_ctrait()
        trait.delegate(
            self.delegate, self.prefix, self.prefix_type, self.modify
        )

        return trait


class DelegatesTo(Delegate):
    """ A trait type that matches the 'delegate' design pattern.

    This defines a trait whose value and definition is "delegated" to
    another trait on a different object.

    An object containing a delegator trait attribute must contain a
    second attribute that references the object containing the delegate
    trait attribute. The name of this second attribute is passed as the
    *delegate* argument to the DelegatesTo() function.

    The following rules govern the application of the prefix parameter:

    * If *prefix* is empty or omitted, the delegation is to an attribute
      of the delegate object with the same name as the delegator
      attribute.
    * If *prefix* is a valid Python attribute name, then the delegation
      is to an attribute whose name is the value of *prefix*.
    * If *prefix* ends with an asterisk ('*') and is longer than one
      character, then the delegation is to an attribute whose name is
      the value of *prefix*, minus the trailing asterisk, prepended to
      the delegator attribute name.
    * If *prefix* is equal to a single asterisk, the delegation is to an
      attribute whose name is the value of the delegator object's
      __prefix__ attribute prepended to delegator attribute name.

    Note that any changes to the delegator attribute are actually
    applied to the corresponding attribute on the delegate object. The
    original object containing the delegator trait is not modified.

    Parameters
    ----------
    delegate : str
        Name of the attribute on the current object which references
        the object that is the trait's delegate.
    prefix : str
        A prefix or substitution applied to the original attribute when
        looking up the delegated attribute.
    listenable : bool
        Indicates whether a listener can be attached to this attribute
        such that changes to the delegated attribute will trigger it.
    **metadata
        Trait metadata for the trait.
    """

    def __init__(self, delegate, prefix="", listenable=True, **metadata):
        super(DelegatesTo, self).__init__(
            delegate,
            prefix=prefix,
            modify=True,
            listenable=listenable,
            **metadata
        )


class PrototypedFrom(Delegate):
    """ A trait type that matches the 'prototype' design pattern.

    This defines a trait whose default value and definition is "prototyped"
    from another trait on a different object.

    An object containing a prototyped trait attribute must contain a
    second attribute that references the object containing the prototype
    trait attribute. The name of this second attribute is passed as the
    *prototype* argument to the PrototypedFrom() function.

    The following rules govern the application of the prefix parameter:

    * If *prefix* is empty or omitted, the prototype delegation is to an
      attribute of the prototype object with the same name as the
      prototyped attribute.
    * If *prefix* is a valid Python attribute name, then the prototype
      delegation is to an attribute whose name is the value of *prefix*.
    * If *prefix* ends with an asterisk ('*') and is longer than one
      character, then the prototype delegation is to an attribute whose
      name is the value of *prefix*, minus the trailing asterisk,
      prepended to the prototyped attribute name.
    * If *prefix* is equal to a single asterisk, the prototype
      delegation is to an attribute whose name is the value of the
      prototype object's __prefix__ attribute prepended to the
      prototyped attribute name.

    Note that any changes to the prototyped attribute are made to the
    original object, not the prototype object. The prototype object is
    only used to define to trait type and default value.

    Parameters
    ----------
    prototype : str
        Name of the attribute on the current object which references the
        object that is the trait's prototype.
    prefix : str
        A prefix or substitution applied to the original attribute when
        looking up the prototyped attribute.
    listenable : bool
        Indicates whether a listener can be attached to this attribute
        such that changes to the corresponding attribute on the
        prototype object will trigger it.
    **metadata
        Trait metadata for the trait.
    """

    def __init__(self, prototype, prefix="", listenable=True, **metadata):
        super(PrototypedFrom, self).__init__(
            prototype,
            prefix=prefix,
            modify=False,
            listenable=listenable,
            **metadata
        )


class Expression(TraitType):
    """ A trait type whose value must be a valid Python expression.

    The compiled form of a valid expression is stored as the mapped value of
    the trait.
    """

    #: The default value for the trait:
    default_value = "0"

    #: A description of the type of value this trait accepts:
    info_text = "a valid Python expression"

    #: Indicate that this is a mapped trait:
    is_mapped = True

    def validate(self, object, name, value):
        """ Validates that a specified value is valid for this trait.
        """
        try:
            return compile(value, "<string>", "eval")
        except:
            self.error(object, name, value)

    def post_setattr(self, object, name, value):
        """ Performs additional post-assignment processing.
        """
        object.__dict__[name + "_"] = value

    def mapped_value(self, value):
        """ Returns the 'mapped' value for the specified **value**.
        """
        return compile(value, "<string>", "eval")

    def as_ctrait(self):
        """ Returns a CTrait corresponding to the trait defined by this class.
        """
        # Tell the C code that 'setattr' should store the original, unadapted
        # value passed to it:
        ctrait = super(Expression, self).as_ctrait()
        ctrait.setattr_original_value = True
        return ctrait


class PythonValue(Any):
    """ A trait type whose value can be of any type.

    The default editor is a ShellEditor.
    """

    #: The standard metadata for the trait:
    metadata = {"editor": shell_editor}


class BaseFile(BaseStr):
    """ A trait type whose value must be a file path string.

    For Python 3.6 and later this will accept os.pathlib Path objects,
    converting them to the corresponding string value.

    Parameters
    ----------
    value : str
        The default value for the trait.
    filter : str
        A wildcard string to filter filenames in the file dialog box used by
        the attribute trait editor.
    auto_set : bool
        Indicates whether the file editor updates the trait value after
        every key stroke.
    entries : int
        A hint to the TraitsUI editor about how many values to display in
        the editor.
    exists : bool
        Indicates whether the trait value must be an existing file or
        not.

    Attributes
    ----------
    filter : str
        A wildcard string to filter filenames in the file dialog box used by
        the attribute trait editor.
    auto_set : bool
        Indicates whether the file editor updates the trait value after
        every key stroke.
    entries : int
        A hint to the TraitsUI editor about how many values to display in
        the editor.
    exists : bool
        Indicates whether the trait value must be an existing file or
        not.
    """

    #: A description of the type of value this trait accepts:
    info_text = "a filename or object implementing the os.PathLike interface"

    def __init__(
        self,
        value="",
        filter=None,
        auto_set=False,
        entries=0,
        exists=False,
        **metadata
    ):
        self.filter = filter
        self.auto_set = auto_set
        self.entries = entries
        self.exists = exists

        super(BaseFile, self).__init__(value, **metadata)

    def validate(self, object, name, value):
        """ Validates that a specified value is valid for this trait.

            Note: The 'fast validator' version performs this check in C.
        """
        if fspath is not None:
            # Python 3.5 does not implement __fspath__
            try:
                # If value is of type os.PathLike, get the path representation
                # The path representation could be either a str or bytes type
                # If fspath returns bytes, further validation will fail.
                value = fspath(value)
            except TypeError:
                pass

        validated_value = super(BaseFile, self).validate(object, name, value)
        if not self.exists:
            return validated_value
        elif isfile(value):
            return validated_value

        self.error(object, name, value)

    def create_editor(self):
        from traitsui.editors.file_editor import FileEditor

        editor = FileEditor(
            filter=self.filter or [],
            auto_set=self.auto_set,
            entries=self.entries,
            dialog_style="open" if self.exists else "save",
        )
        return editor


class File(BaseFile):
    """ A fast-validating trait type whose value must be a file path string.

    For Python 3.6 and later this will accept os.pathlib Path objects,
    converting them to the corresponding string value.

    Parameters
    ----------
    value : str
        The default value for the trait.
    filter : str
        A wildcard string to filter filenames in the file dialog box used by
        the attribute trait editor.
    auto_set : bool
        Indicates whether the file editor updates the trait value after
        every key stroke.
    entries : int
        A hint to the TraitsUI editor about how many values to display in
        the editor.
    exists : bool
        Indicates whether the trait value must be an existing file or
        not.

    Attributes
    ----------
    filter : str
        A wildcard string to filter filenames in the file dialog box used by
        the attribute trait editor.
    auto_set : bool
        Indicates whether the file editor updates the trait value after
        every key stroke.
    entries : int
        A hint to the TraitsUI editor about how many values to display in
        the editor.
    exists : bool
        Indicates whether the trait value must be an existing file or
        not.
    """

    def __init__(
        self,
        value="",
        filter=None,
        auto_set=False,
        entries=0,
        exists=False,
        **metadata
    ):
        super(File, self).__init__(
            value, filter, auto_set, entries, exists, **metadata
        )


class BaseDirectory(BaseStr):
    """ A trait type whose value is a directory path string.

    Parameters
    ----------
    value : str
        The default value for the trait.
    auto_set : bool
        Indicates whether the directory editor updates the trait value
        after every key stroke.
    entries : int
        A hint to the TraitsUI editor about how many values to display in
        the editor.
    exists : bool
        Indicates whether the trait value must be an existing directory or
        not.

    Attributes
    ----------
    auto_set : bool
        Indicates whether the directory editor updates the trait value
        after every key stroke.
    entries : int
        A hint to the TraitsUI editor about how many values to display in
        the editor.
    exists : bool
        Indicates whether the trait value must be an existing directory or
        not.
    """

    #: A description of the type of value this trait accepts:
    info_text = "a directory name"

    def __init__(
        self, value="", auto_set=False, entries=0, exists=False, **metadata
    ):
        self.entries = entries
        self.auto_set = auto_set
        self.exists = exists

        super(BaseDirectory, self).__init__(value, **metadata)

    def validate(self, object, name, value):
        """ Validates that a specified value is valid for this trait.

        Note: The 'fast validator' version performs this check in C.
        """
        validated_value = super(BaseDirectory, self).validate(
            object, name, value
        )
        if not self.exists:
            return validated_value
        elif isdir(value):
            return validated_value

        self.error(object, name, value)

    def create_editor(self):
        from traitsui.editors.directory_editor import DirectoryEditor

        editor = DirectoryEditor(auto_set=self.auto_set, entries=self.entries)
        return editor


class Directory(BaseDirectory):
    """ A fast-validating trait type whose value is a directory path string.

    Parameters
    ----------
    value : str
        The default value for the trait.
    auto_set : bool
        Indicates whether the directory editor updates the trait value
        after every key stroke.
    entries : int
        A hint to the TraitsUI editor about how many values to display in
        the editor.
    exists : bool
        Indicates whether the trait value must be an existing directory or
        not.

    Attributes
    ----------
    auto_set : bool
        Indicates whether the directory editor updates the trait value
        after every key stroke.
    entries : int
        A hint to the TraitsUI editor about how many values to display in
        the editor.
    exists : bool
        Indicates whether the trait value must be an existing directory or
        not.
    """

    def __init__(
        self, value="", auto_set=False, entries=0, exists=False, **metadata
    ):
        # Define the C-level fast validator to use if the directory existence
        #: test is not required:
        if not exists:
            self.fast_validate = (ValidateTrait.coerce, str)
        super(Directory, self).__init__(
            value, auto_set, entries, exists, **metadata
        )


class BaseRange(TraitType):
    """ A trait type whose numeric value lies inside a range.

    The value held will be either an integer or a float, which type is
    determined by whether the *low*, *high* and *value* arguments are
    integers or floats.

    The *low*, *high*, and *value* arguments must be of the same type
    (integer or float), except in the case where either *low* or *high* is
    a string (i.e. extended trait name).

    If *value* is None or omitted, the default value is *low*, unless *low*
    is None or omitted, in which case the default value is *high*.

    Parameters
    ----------
    low : integer, float or string (i.e. extended trait name)
        The low end of the range.
    high : integer, float or string (i.e. extended trait name)
        The high end of the range.
    value : integer, float or string (i.e. extended trait name)
        The default value of the trait.
    exclude_low : bool
        Indicates whether the low end of the range is exclusive.
    exclude_high : bool
        Indicates whether the high end of the range is exclusive.
    """

    def __init__(
        self,
        low=None,
        high=None,
        value=None,
        exclude_low=False,
        exclude_high=False,
        **metadata
    ):
        if value is None:
            if low is not None:
                value = low
            else:
                value = high

        super(BaseRange, self).__init__(value, **metadata)

        vtype = type(high)
        if (low is not None) and (
            not issubclass(vtype, (float, str))
        ):
            vtype = type(low)

        is_static = not issubclass(vtype, str)
        if is_static and (vtype not in RangeTypes):
            raise TraitError(
                "Range can only be use for int or float "
                "values, but a value of type %s was specified." % vtype
            )

        self._low_name = self._high_name = ""
        self._vtype = Undefined

        kind = None

        if vtype is float:
            self._validate = "float_validate"
            kind = ValidateTrait.float_range
            self._type_desc = "a floating point number"
            if low is not None:
                low = float(low)

            if high is not None:
                high = float(high)

        elif vtype is int:
            self._validate = "int_validate"
            self._type_desc = "an integer"
            if low is not None:
                low = int(low)

            if high is not None:
                high = int(high)
        else:
            self.get, self.set, self.validate = self._get, self._set, None
            self._vtype = None
            self._type_desc = "a number"

            if isinstance(high, str):
                self._high_name = high = "object." + high
            else:
                self._vtype = type(high)
            high = compile(str(high), "<string>", "eval")

            if isinstance(low, str):
                self._low_name = low = "object." + low
            else:
                self._vtype = type(low)
            low = compile(str(low), "<string>", "eval")

            if isinstance(value, str):
                value = "object." + value
            self._value = compile(str(value), "<string>", "eval")

            self.default_value_type = DefaultValue.callable
            self.default_value = self._get_default_value

        exclude_mask = 0
        if exclude_low:
            exclude_mask |= 1

        if exclude_high:
            exclude_mask |= 2

        if is_static and kind is not None:
            self.init_fast_validate(kind, low, high, exclude_mask)

        #: Assign type-corrected arguments to handler attributes:
        self._low = low
        self._high = high
        self._exclude_low = exclude_low
        self._exclude_high = exclude_high

    def init_fast_validate(self, *args):
        """ Does nothing for the BaseRange class. Used in the Range class to
        set up the fast validator.
        """
        pass

    def validate(self, object, name, value):
        """ Validate that the value is in the specified range.
        """
        return getattr(self, self._validate)(object, name, value)

    def float_validate(self, object, name, value):
        """ Validate that the value is a float value in the specified range.
        """
        # Convert to exact type float, re-raising a TypeError as a TraitError
        # and letting other errors propagate. Keep original value for
        # error-reporting purposes.
        original_value = value
        try:
            value = _validate_float(value)
        except TypeError:
            self.error(object, name, original_value)

        if (
            (
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

        self.error(object, name, original_value)

    def int_validate(self, object, name, value):
        """ Validate that the value is an int value in the specified range.
        """
        # Convert to exact type float, re-raising a TypeError as a TraitError
        # and letting other errors propagate. Keep original value for
        # error-reporting purposes.
        original_value = value
        try:
            value = _validate_int(value)
        except TypeError:
            self.error(object, name, original_value)

        if (
            (
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

        self.error(object, name, original_value)

    def _get_default_value(self, object):
        """ Returns the default value of the range.
        """
        return eval(self._value)

    def _get(self, object, name, trait):
        """ Returns the current value of a dynamic range trait.
        """
        cname = "_traits_cache_" + name
        value = object.__dict__.get(cname, Undefined)
        if value is Undefined:
            object.__dict__[cname] = value = eval(self._value)

        low = eval(self._low)
        high = eval(self._high)
        if (low is not None) and (value < low):
            value = low
        elif (high is not None) and (value > high):
            value = high

        return self._typed_value(value, low, high)

    def _set(self, object, name, value):
        """ Sets the current value of a dynamic range trait.
        """
        if not isinstance(value, str):
            try:
                low = eval(self._low)
                high = eval(self._high)
                if (low is None) and (high is None):
                    if isinstance(value, RangeTypes):
                        self._set_value(object, name, value)
                        return
                else:
                    new_value = self._typed_value(value, low, high)
                    if (
                        (low is None)
                        or (self._exclude_low and (low < new_value))
                        or ((not self._exclude_low) and (low <= new_value))
                    ) and (
                        (high is None)
                        or (self._exclude_high and (high > new_value))
                        or ((not self._exclude_high) and (high >= new_value))
                    ):
                        self._set_value(object, name, new_value)
                        return
            except:
                pass

        self.error(object, name, value)

    def _typed_value(self, value, low, high):
        """ Returns the specified value with the correct type for the current
            dynamic range.
        """
        vtype = self._vtype
        if vtype is None:
            if low is not None:
                vtype = type(low)
            elif high is not None:
                vtype = type(high)
            else:
                vtype = lambda x: x

        return vtype(value)

    def _set_value(self, object, name, value):
        """ Sets the specified value as the value of the dynamic range.
        """
        cname = "_traits_cache_" + name
        old = object.__dict__.get(cname, Undefined)
        if old is Undefined:
            old = eval(self._value)
        object.__dict__[cname] = value
        if value != old:
            object.trait_property_changed(name, old, value)

    def full_info(self, object, name, value):
        """ Returns a description of the trait.
        """
        if self._vtype is not Undefined:
            low = eval(self._low)
            high = eval(self._high)
            low, high = (
                self._typed_value(low, low, high),
                self._typed_value(high, low, high),
            )
        else:
            low = self._low
            high = self._high

        if low is None:
            if high is None:
                return self._type_desc

            return "%s <%s %s" % (
                self._type_desc,
                "="[self._exclude_high:],
                high,
            )

        elif high is None:
            return "%s >%s %s" % (
                self._type_desc,
                "="[self._exclude_low:],
                low,
            )

        return "%s <%s %s <%s %s" % (
            low,
            "="[self._exclude_low:],
            self._type_desc,
            "="[self._exclude_high:],
            high,
        )

    def create_editor(self):
        """ Returns the default UI editor for the trait.
        """
        # fixme: Needs to support a dynamic range editor.

        auto_set = self.auto_set
        if auto_set is None:
            auto_set = True

        from traitsui.api import RangeEditor

        return RangeEditor(
            self,
            mode=self.mode or "auto",
            cols=self.cols or 3,
            auto_set=auto_set,
            enter_set=self.enter_set or False,
            low_label=self.low or "",
            high_label=self.high or "",
            low_name=self._low_name,
            high_name=self._high_name,
        )


class Range(BaseRange):
    """ A fast-validating trait type whose numeric value lies inside a range.
    """

    def init_fast_validate(self, *args):
        """ Set up the C-level fast validator.
        """
        self.fast_validate = args


class BaseEnum(TraitType):
    """ A trait type whose value is one of a set of values.

    The default value is the first positional argument, or the first item of
    the list, tuple or enum.Enum if that is the only argument or if the valid
    values are provided dynamically.

    Parameters
    ----------
    *args
        The enumeration of all legal values for the trait.  The expected
        signatures are either:

        - a single list, enum.Enum or tuple.  The default value is the first
          item in the collection.
        - a single default value, combined with the values keyword
          argument.
        - a default value, followed by a single list enum.Enum or tuple.
        - arbitrary positional arguments each giving a valid value.
    values : str
        The name of a trait holding the legal values.  A default value may
        be provided via a positional argument, otherwise it is the first
        item stored in the .
    **metadata
        Trait metadata for the trait.

    Attributes
    ----------
    values : tuple
        A tuple holding the legal values.

    name : str
        The name of a trait holding the legal values, or the empty string if
        unused.
    """

    def __init__(self, *args, **metadata):
        values = metadata.pop("values", None)
        if isinstance(values, str):
            self.name = values
            self.get, self.set, self.validate = self._get, self._set, None
            n = len(args)
            if n == 0:
                super(BaseEnum, self).__init__(**metadata)
            elif n == 1:
                default_value = args[0]
                super(BaseEnum, self).__init__(default_value, **metadata)
            else:
                raise TraitError(
                    "Incorrect number of arguments specified "
                    "when using the 'values' keyword"
                )
        else:
            default_value = args[0]
            if (len(args) == 1) and isinstance(default_value, EnumTypes):
                args = default_value
                default_value = enum_default(args)
            elif (len(args) == 2) and isinstance(args[1], EnumTypes):
                args = args[1]

            if isinstance(args, enum.EnumMeta):
                metadata.setdefault('format_func', operator.attrgetter('name'))
                metadata.setdefault('evaluate', args)

            self.name = ""
            self.values = tuple(args)
            self.init_fast_validate(ValidateTrait.enum, self.values)

            super(BaseEnum, self).__init__(default_value, **metadata)

    def init_fast_validate(self, *args):
        """ Does nothing for the BaseEnum class. Used in the Enum class to set
            up the fast validator.
        """
        pass

    def validate(self, object, name, value):
        """ Validates that the value is one of the enumerated set of valid
        values.
        """
        if safe_contains(value, self.values):
            return value

        self.error(object, name, value)

    def full_info(self, object, name, value):
        """ Returns a description of the trait.
        """
        if self.name == "":
            values = self.values
        else:
            values = xgetattr(object, self.name)

        return " or ".join([repr(x) for x in values])

    def create_editor(self):
        """ Returns the default UI editor for the trait.
        """
        from traitsui.api import EnumEditor

        values = self
        if self.name != "":
            values = None

        return EnumEditor(
            values=values,
            name=self.name,
            cols=self.cols or 3,
            evaluate=self.evaluate,
            format_func=self.format_func,
            mode=self.mode if self.mode else "radio",
        )

    def _get(self, object, name, trait):
        """ Returns the current value of a dynamic enum trait.
        """
        value = self.get_value(object, name, trait)
        values = xgetattr(object, self.name)
        if not safe_contains(value, values):
            value = enum_default(values)
        return value

    def _set(self, object, name, value):
        """ Sets the current value of a dynamic range trait.
        """
        if safe_contains(value, xgetattr(object, self.name)):
            self.set_value(object, name, value)
        else:
            self.error(object, name, value)


class Enum(BaseEnum):
    """ A fast-validating trait type whose value is one of a set of values.

    The default value is the first positional argument, or the first item of
    the list, tuple or enum.Enum if that is the only argument or if the valid
    values are provided dynamically.

    Parameters
    ----------
    *args
        The enumeration of all legal values for the trait.  The expected
        signatures are either:

        - a single list, enum.Enum or tuple.  The default value is the first
          item in the collection.
        - a single default value, combined with the values keyword
          argument.
        - a default value, followed by a single list enum.Enum or tuple.
        - arbitrary positional arguments each giving a valid value.

    values : str
        The name of a trait holding the legal values.  A default value may
        be provided via a positional argument, otherwise it is the first
        item stored in the .
    **metadata
        Trait metadata for the trait.

    Attributes
    ----------
    values : tuple
        A tuple holding the legal values.

    name : str
        The name of a trait holding the legal values, or the empty string if
        unused.
    """

    def init_fast_validate(self, *args):
        """ Set up C-level fast validation. """
        self.fast_validate = args


class BaseTuple(TraitType):
    """ A trait type holding a tuple with typed elements.

    The default value is determined as follows:

    1.  If no arguments are specified, the default value is ().
    2.  If a tuple is specified as the first argument, it is the default
        value.
    3.  If a tuple is not specified as the first argument, the default
        value is a tuple whose length is the length of the argument list,
        and whose values are the default values for the corresponding trait
        types.

    Example for case #2::

        mytuple = Tuple(('Fred', 'Betty', 5))

    The trait's value must be a 3-element tuple whose first and second
    elements are strings, and whose third element is an integer. The
    default value is ``('Fred', 'Betty', 5)``.

    Example for case #3::

        mytuple = Tuple('Fred', 'Betty', 5)

    The trait's value must be a 3-element tuple whose first and second
    elements are strings, and whose third element is an integer. The
    default value is ``('','',0)``.

    Parameters
    ----------
    *types
        Definition of the default and allowed tuples. If the first item of
        *types* is a tuple, it is used as the default value.
        The remaining argument list is used to form a tuple that constrains
        the  values assigned to the returned trait. The trait's value must
        be a tuple of the same length as the remaining argument list, whose
        elements must match the types specified by the corresponding items
        of the remaining argument list.
    **metadata
        Trait metadata for the trait.

    Attributes
    ----------
    types : tuple
        The tuple of traits specifying the type of each element in order.
    no_type_check : bool
        Flag to indicate whether validation should check the type of each
        element.
    """

    def __init__(self, *types, **metadata):
        if len(types) == 0:
            self.init_fast_validate(ValidateTrait.coerce, tuple, None, list)

            super(BaseTuple, self).__init__((), **metadata)

            return

        default_value = None

        if isinstance(types[0], tuple):
            default_value, types = types[0], types[1:]
            if len(types) == 0:
                types = [Trait(element) for element in default_value]

        self.types = tuple([trait_from(type) for type in types])
        self.init_fast_validate(ValidateTrait.tuple, self.types)

        if default_value is None:
            default_value = tuple(
                [type.default_value()[1] for type in self.types]
            )

        super(BaseTuple, self).__init__(default_value, **metadata)

    def init_fast_validate(self, *args):
        """ Saves the validation parameters.
        """
        self.no_type_check = args[0] == ValidateTrait.coerce

    def validate(self, object, name, value):
        """ Validates that the value is a valid tuple.
        """
        if self.no_type_check:
            if isinstance(value, tuple):
                return value

            if isinstance(value, list):
                return tuple(value)

            self.error(object, name, value)

        try:
            if isinstance(value, list):
                value = tuple(value)

            if isinstance(value, tuple):
                types = self.types
                if len(value) == len(types):
                    values = []
                    for i, type in enumerate(types):
                        values.append(type.validate(object, name, value[i]))

                    return tuple(values)
        except:
            pass

        self.error(object, name, value)

    def full_info(self, object, name, value):
        """ Returns a description of the trait.
        """
        if self.no_type_check:
            return "a tuple"

        return "a tuple of the form: (%s)" % (
            ", ".join(
                [type.full_info(object, name, value) for type in self.types]
            )
        )

    def create_editor(self):
        """ Returns the default UI editor for the trait.
        """
        from traitsui.api import TupleEditor

        auto_set = self.auto_set
        if auto_set is None:
            auto_set = True
        enter_set = self.enter_set or False

        return TupleEditor(
            types=self.types,
            labels=self.labels or [],
            cols=self.cols or 1,
            auto_set=auto_set,
            enter_set=enter_set,
        )


class Tuple(BaseTuple):
    """ A fast-validating trait type holding a tuple with typed elements.
    """

    def init_fast_validate(self, *args):
        """ Set up the C-level fast validator.
        """
        super(Tuple, self).init_fast_validate(*args)

        self.fast_validate = args


class ValidatedTuple(BaseTuple):
    """ A trait type holding a tuple with customized validation.

    Parameters
    ----------
    *types
        Definition of the default and allowed tuples. (see
        :class:`~.BaseTuple` for more details)
    fvalidate : callable, optional
        A callable to provide the additional custom validation for the
        tuple. The callable will be passed the tuple value and should
        return True or False.
    fvalidate_info : string, optional
        A string describing the custom validation to use for the error
        messages.
    **metadata
        Trait metadata for the trait.

    Example
    -------
    The definition::

        value_range = ValidatedTuple(Int(0), Int(1), fvalidate=lambda x: x[0] < x[1])

    will accept only tuples ``(a, b)`` containing two integers that
    satisfy ``a < b``.
    """

    def __init__(self, *types, **metadata):
        metadata.setdefault("fvalidate", None)
        metadata.setdefault("fvalidate_info", "")
        super(ValidatedTuple, self).__init__(*types, **metadata)

    def validate(self, object, name, value):
        """ Validates that the value is a valid tuple.
        """
        values = super(ValidatedTuple, self).validate(object, name, value)
        # Exceptions in the fvalidate function will not result in a TraitError
        # but will be allowed to propagate up the frame stacks.
        if self.fvalidate is None or self.fvalidate(values):
            return values
        else:
            self.error(object, name, value)

    def full_info(self, object, name, value):
        """ Returns a description of the trait.
        """
        message = "a tuple of the form: ({0}) that passes custom validation{1}"
        types_info = ", ".join(
            [type_.full_info(object, name, value) for type_ in self.types]
        )
        if self.fvalidate_info is not None:
            fvalidate_info = ": {0}".format(self.fvalidate_info)
        else:
            fvalidate_info = ""
        return message.format(types_info, fvalidate_info)


class List(TraitType):
    """ A trait type for a list of values of the specified type.

    The length of the list assigned to the trait must be such that::

        minlen <= len(list) <= maxlen

    Parameters
    ----------
    trait : a trait or value that can be converted using trait_from()
        The type of item that the list contains. If not specified, the list
        can contain items of any type.
    value : list
        Default value for the list.
    minlen : integer
        The minimum length of a list that can be assigned to the trait.
    maxlen : integer
        The maximum length of a list that can be assigned to the trait.
    items : bool
        Whether there is a corresponding `<name>_items` trait.
    **metadata
        Trait metadata for the trait.

    Attributes
    ----------
    item_trait : trait
        The type of item that the list contains.
    minlen : integer
        The minimum length of a list that can be assigned to the trait.
    maxlen : integer
        The maximum length of a list that can be assigned to the trait.
    has_items : bool
        Whether there is a corresponding `<name>_items` trait.
    """

    info_trait = None
    default_value_type = DefaultValue.trait_list_object
    _items_event = None

    def __init__(
        self,
        trait=None,
        value=None,
        minlen=0,
        maxlen=sys.maxsize,
        items=True,
        **metadata
    ):
        metadata.setdefault("copy", "deep")

        if isinstance(trait, SequenceTypes):
            trait, value = value, list(trait)

        if value is None:
            value = []

        self.item_trait = trait_from(trait)
        self.minlen = max(0, minlen)
        self.maxlen = max(minlen, maxlen)
        self.has_items = items

        if self.item_trait.instance_handler == "_instance_changed_handler":
            metadata.setdefault("instance_handler", "_list_changed_handler")

        super(List, self).__init__(value, **metadata)

    def validate(self, object, name, value):
        """ Validates that the values is a valid list.

        .. note::

            `object` can be None when validating a default value (see e.g.
            :meth:`~traits.trait_handlers.TraitType.clone`)

        """
        if isinstance(value, list) and (
            self.minlen <= len(value) <= self.maxlen
        ):
            if object is None:
                return value

            return TraitListObject(self, object, name, value)

        self.error(object, name, value)

    def full_info(self, object, name, value):
        """ Returns a description of the trait.
        """
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

        return "a list of %s which are %s" % (
            size,
            self.item_trait.full_info(object, name, value),
        )

    def create_editor(self):
        """ Returns the default UI editor for the trait.
        """
        return list_editor(self, self)

    def inner_traits(self):
        """ Returns the *inner trait* (or traits) for this trait.
        """
        return (self.item_trait,)

    # -- Private Methods --------------------------------------------------------

    def items_event(self):
        cls = self.__class__
        if cls._items_event is None:
            cls._items_event = Event(
                TraitListEvent, is_base=False
            ).as_ctrait()

        return cls._items_event


class CList(List):
    """ A coercing trait type for a list of values of the specified type.
    """

    def validate(self, object, name, value):
        """ Validates that the values is a valid list.
        """
        if not isinstance(value, list):
            try:
                # Should work for all iterables as well as strings (which do
                # not define an __iter__ method)
                value = list(value)
            except (ValueError, TypeError):
                value = [value]

        return super(CList, self).validate(object, name, value)

    def full_info(self, object, name, value):
        """ Returns a description of the trait.
        """
        return "%s or %s" % (
            self.item_trait.full_info(object, name, value),
            super(CList, self).full_info(object, name, value),
        )


class Set(TraitType):
    """ A trait type for a set of values of the specified type.

    Parameters
    ----------
    trait : a trait or value that can be converted to a trait using Trait()
        The type of item that the list contains. If not specified, the list
        can contain items of any type.
    value : set
        Default value for the set.
    items : bool
        Whether there is a corresponding `<name>_items` trait.
    **metadata
        Trait metadata for the trait.

    Attributes
    ----------
    item_trait : a trait or value that can be converted to a trait using Trait()
        The type of item that the list contains. If not specified, the list
        can contain items of any type.
    has_items : bool
        Whether there is a corresponding `<name>_items` trait.
    """

    info_trait = None
    default_value_type = DefaultValue.trait_set_object
    _items_event = None

    def __init__(self, trait=None, value=None, items=True, **metadata):
        metadata.setdefault("copy", "deep")

        if isinstance(trait, SetTypes):
            trait, value = value, set(trait)

        if value is None:
            value = set()

        self.item_trait = trait_from(trait)
        self.has_items = items

        super(Set, self).__init__(value, **metadata)

    def validate(self, object, name, value):
        """ Validates that the values is a valid set.

        .. note::

            `object` can be None when validating a default value (see e.g.
            :meth:`~traits.trait_handlers.TraitType.clone`)

        """
        if isinstance(value, set):
            if object is None:
                return value

            return TraitSetObject(self, object, name, value)

        self.error(object, name, value)

    def full_info(self, object, name, value):
        """ Returns a description of the trait.
        """
        return "a set of %s" % self.item_trait.full_info(object, name, value)

    def create_editor(self):
        """ Returns the default UI editor for the trait.
        """
        from traitsui.api import TextEditor

        return TextEditor(evaluate=eval)

    def inner_traits(self):
        """ Returns the *inner trait* (or traits) for this trait.
        """
        return (self.item_trait,)

    # -- Private Methods --------------------------------------------------------

    def items_event(self):
        if self.__class__._items_event is None:
            self.__class__._items_event = Event(
                TraitSetEvent, is_base=False
            ).as_ctrait()

        return self.__class__._items_event


class CSet(Set):
    """ A coercing trait type for a set of values of the specified type.
    """

    def validate(self, object, name, value):
        """ Validates that the values is a valid list.
        """
        if not isinstance(value, set):
            try:
                # Should work for all iterables as well as strings (which do
                # not define an __iter__ method)
                value = set(value)
            except (ValueError, TypeError):
                value = set([value])

        return super(CSet, self).validate(object, name, value)

    def full_info(self, object, name, value):
        """ Returns a description of the trait.
        """
        return "%s or %s" % (
            self.item_trait.full_info(object, name, value),
            super(CSet, self).full_info(object, name, value),
        )


class Dict(TraitType):
    """ A trait type for a dictionary with specified key and value types.


    Parameters
    ----------
    key_trait : a trait or value that can be converted using trait_from()
        The trait type for keys in the dictionary; if not specified, any
        values can be used as keys.
    value_trait : a trait or value that can be converted using trait_from()
        The trait type for values in the dictionary; if not specified, any
        values can be used as dictionary values.
    value : dict
        The default value for the returned trait.
    items : bool
        Indicates whether the value contains items.

    Attributes
    ----------
    key_trait : a trait
        The trait type for keys in the dictionary; if not specified, any
        values can be used as keys.
    value_trait : a trait
        The trait type for values in the dictionary; if not specified, any
        values can be used as dictionary values.
    value_trait_handler : TraitHandler
        The TraitHandler for the value_trait.
    has_items : bool
        Indicates whether the value contains items.
    """

    info_trait = None
    default_value_type = DefaultValue.trait_dict_object
    _items_event = None

    def __init__(
        self,
        key_trait=None,
        value_trait=None,
        value=None,
        items=True,
        **metadata
    ):
        if isinstance(key_trait, dict):
            key_trait, value_trait, value = value_trait, value, key_trait

        if value is None:
            value = {}

        self.key_trait = trait_from(key_trait)
        self.value_trait = trait_from(value_trait)
        self.has_items = items

        handler = self.value_trait.handler
        if (handler is not None) and handler.has_items:
            handler = handler.clone()
            handler.has_items = False
        self.value_handler = handler

        super(Dict, self).__init__(value, **metadata)

    def validate(self, object, name, value):
        """ Validates that the value is a valid dictionary.

        Note
        ----
        `object` can be None when validating a default value (see e.g.
        :meth:`~traits.trait_handlers.TraitType.clone`)
        """
        if isinstance(value, dict):
            if object is None:
                return value
            return TraitDictObject(self, object, name, value)

        self.error(object, name, value)

    def full_info(self, object, name, value):
        """ Returns a description of the trait.
        """
        return (
            "a dictionary with keys which are %s and with values which "
            "are %s"
        ) % (
            self.key_trait.full_info(object, name, value),
            self.value_trait.full_info(object, name, value),
        )

    def create_editor(self):
        """ Returns the default UI editor for the trait.
        """
        from traitsui.api import TextEditor

        return TextEditor(evaluate=eval)

    def inner_traits(self):
        """ Returns the *inner trait* (or traits) for this trait.
        """
        return (self.key_trait, self.value_trait)

    # -- Private Methods --------------------------------------------------------

    def items_event(self):
        cls = self.__class__
        if cls._items_event is None:
            cls._items_event = Event(TraitDictEvent, is_base=False).as_ctrait()

        return cls._items_event


#: Allowed values and mappings for the 'adapt' keyword.
#:
#: - 'no': Adaptation is not allowed.
#: - 'yes': Adaptation is allowed. If adaptation fails, an
#:   exception should be raised.
#: - 'default': Adaptation is allowed. If adaptation fails, the
#:   default value for the trait should be used.
AdaptMap = {"no": 0, "yes": 1, "default": 2}


class BaseClass(TraitType):
    """ A base trait type for trait types which have an associated class.

    Traits sometimes need to be able to access classes which have not
    yet been defined, or which are from a module that we want to defer
    importing from.  To support this, classes can be determined
    dynamically by specifying a string name for the class (e.g.
    ``'package1.package2.module.class'``).  This base class provides the
    machinery for this sort of deferred access to classes.

    Any subclass must define instances with 'klass' and 'module' attributes
    that contain the string name of the class (or actual class object) and
    the module name that contained the original trait definition (used for
    resolving local class names (e.g. 'LocalClass')).

    This is an abstract class that only provides helper methods used to
    resolve the class name into an actual class object.

    Attributes
    ----------
    klass : type or str
        The class object or a string that refers to it.
    module : str
        The name of the module that contains the class.
    """

    def resolve_class(self, object, name, value):
        """ Resolve the class object as part of validation.

        This is called when the ``klass`` attribute is a string and sets the
        ``klass`` attribute to the actual klass object as a side-effect.  If
        the class cannot be resolved, it will call validate_failed().
        """
        klass = self.validate_class(self.find_class(self.klass))
        if klass is None:
            self.validate_failed(object, name, value)

        self.klass = klass

    def validate_class(self, klass):
        """ Validate a class object. """
        return klass

    def find_class(self, klass):
        """ Given a string describing a class, get the class object.
        """
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

    def validate_failed(self, object, name, value):
        """ Raise a TraitError if the class could not be resolved. """
        self.error(object, name, value)


class BaseInstance(BaseClass):
    """ A trait type whose value is an instance of a class or its subclasses.

    The default value is **None** if *klass* is an instance or if it is a
    class and *args* and *kw* are not specified. Otherwise, the default value
    is the instance obtained by calling ``klass(*args, **kw)``. Note that the
    constructor call is performed each time a default value is assigned, so
    each default value assigned is a unique instance.

    Parameters
    ----------
    klass : class, str or instance
        The object that forms the basis for the trait; if it is an
        instance, then trait values must be instances of the same class or
        a subclass. This object is not the default value, even if it is an
        instance.  If the provided value is a string, it is expected to be
        a reference to a class that will be resolved at run-time.
    factory : callable
        A callable, typically a class, that when called with *args* and
        *kw*, returns the default value for the trait. If not specified,
        or *None*, *klass* is used as the factory.
    args : tuple
        Positional arguments for generating the default value.
    kw : dictionary
        Keyword arguments for generating the default value.
    allow_none : bool
        Indicates whether None is allowed as a value.
    adapt : str
        A string specifying how adaptation should be applied. The possible
        values are:

        - 'no': Adaptation is not allowed.
        - 'yes': Adaptation is allowed. If adaptation fails, an
          exception should be raised.
        - 'default': Adaptation is allowed. If adaptation fails, the
          default value for the trait should be used.

    Attributes
    ----------
    factory : callable
        A callable, typically a class, that when called with *args* and
        *kw*, returns the default value for the trait. If not specified,
        or *None*, *klass* is used as the factory.
    args : tuple
        Positional arguments for generating the default value.
    kw : dictionary
        Keyword arguments for generating the default value.
    allow_none : bool
        Indicates whether None is allowed as a value.
    adapt : str
        A string specifying how adaptation should be applied. The possible
        values are:

        - 'no': Adaptation is not allowed.
        - 'yes': Adaptation is allowed. If adaptation fails, an
          exception should be raised.
        - 'default': Adaptation is allowed. If adaptation fails, the
          default value for the trait should be used.
    """

    #: Default adaptation behavior.
    adapt_default = "no"

    def __init__(
        self,
        klass=None,
        factory=None,
        args=None,
        kw=None,
        allow_none=True,
        adapt=None,
        module=None,
        **metadata
    ):
        if klass is None:
            raise TraitError(
                "A %s trait must have a class specified."
                % self.__class__.__name__
            )

        metadata.setdefault("copy", "deep")
        metadata.setdefault("instance_handler", "_instance_changed_handler")

        adapt = adapt or self.adapt_default
        if adapt not in AdaptMap:
            raise TraitError("'adapt' must be 'yes', 'no' or 'default'.")

        if isinstance(factory, tuple):
            if args is None:
                args, factory = factory, klass
            elif isinstance(args, dict):
                factory, args, kw = klass, factory, args

        elif (kw is None) and isinstance(factory, dict):
            kw, factory = factory, klass

        elif ((args is not None) or (kw is not None)) and (factory is None):
            factory = klass

        self._allow_none = allow_none
        self.adapt = AdaptMap[adapt]
        self.module = module or get_module_name()

        if isinstance(klass, str):
            self.klass = klass
        else:
            if not isinstance(klass, type):
                klass = klass.__class__

            self.klass = klass
            self.init_fast_validate()

        value = factory
        if factory is not None:
            if args is None:
                args = ()

            if kw is None:
                if isinstance(args, dict):
                    kw = args
                    args = ()
                else:
                    kw = {}
            elif not isinstance(kw, dict):
                raise TraitError("The 'kw' argument must be a dictionary.")

            if (not callable(factory)) and (
                not isinstance(factory, str)
            ):
                if (len(args) > 0) or (len(kw) > 0):
                    raise TraitError("'factory' must be callable")
            else:
                value = _InstanceArgs(factory, args, kw)

        self.default_value = value

        super(BaseInstance, self).__init__(value, **metadata)

    def validate(self, object, name, value):
        """ Validates that the value is a valid object instance.
        """
        from traits.adaptation.api import adapt

        if value is None:
            if self._allow_none:
                return value

            self.validate_failed(object, name, value)

        if isinstance(self.klass, str):
            self.resolve_class(object, name, value)

        # Adaptation mode 0: do a simple isinstance check.
        if self.adapt == 0:
            if isinstance(value, self.klass):
                return value
            else:
                self.validate_failed(object, name, value)

        # Try adaptation; return adapted value on success.
        result = adapt(value, self.klass, None)
        if result is not None:
            return result

        # Adaptation failed. Move on to an isinstance check.
        if isinstance(value, self.klass):
            return value

        # Adaptation and isinstance both failed. In mode 1, fail.
        # Otherwise, return the default.
        if self.adapt == 1:
            self.validate_failed(object, name, value)
        else:
            result = self.default_value
            if isinstance(result, _InstanceArgs):
                return result[0](*result[1], **result[2])
            else:
                return result

    def info(self):
        """ Returns a description of the trait.
        """
        klass = self.klass
        if not isinstance(klass, str):
            klass = klass.__name__

        if self.adapt == 0:
            result = class_of(klass)
        else:
            result = (
                "an implementor of, or can be adapted to implement, %s" % klass
            )

        if self._allow_none:
            return result + " or None"

        return result

    def get_default_value(self):
        """ Returns a tuple of the form: ( default_value_type, default_value )
            which describes the default value for this trait.
        """
        dv = self.default_value
        dvt = self.default_value_type
        if dvt < 0:
            if not isinstance(dv, _InstanceArgs):
                return super(BaseInstance, self).get_default_value()

            self.default_value_type = dvt = DefaultValue.callable_and_args
            self.default_value = dv = (
                self.create_default_value,
                dv.args,
                dv.kw,
            )

        return (dvt, dv)

    def create_editor(self):
        """ Returns the default traits UI editor for this type of trait.
        """
        from traitsui.api import InstanceEditor

        return InstanceEditor(
            label=self.label or "",
            view=self.view or "",
            kind=self.kind or "live",
        )

    # -- Private Methods --------------------------------------------------------

    def create_default_value(self, *args, **kw):
        klass = args[0]
        if isinstance(klass, str):
            klass = self.validate_class(self.find_class(klass))
            if klass is None:
                raise TraitError("Unable to locate class: " + args[0])

        return klass(*args[1:], **kw)

    #: fixme: Do we still need this method using the new style?...
    def allow_none(self):
        self._allow_none = True
        self.init_fast_validate()

    def init_fast_validate(self):
        """ Does nothing for the BaseInstance' class. Used by the 'Instance',
            'Supports' and 'AdaptsTo' classes to set up the C-level fast
            validator.
        """
        pass

    def resolve_class(self, object, name, value):
        super(BaseInstance, self).resolve_class(object, name, value)

        #: fixme: The following is quite ugly, because it wants to try and fix
        #: the trait referencing this handler to use the 'fast path' now that the
        #: actual class has been resolved. The problem is finding the trait,
        # especially in the case of List(Instance('foo')), where the
        # object.base_trait(...) value is the List trait, not the Instance
        # trait, so we need to check for this and pull out the List
        # 'item_trait'. Obviously this does not extend well to other traits
        # containing nested trait references (Dict?)...
        self.init_fast_validate()
        trait = object.base_trait(name)
        handler = trait.handler
        if handler is not self:
            set_validate = getattr(handler, "set_validate", None)
            if set_validate is not None:
                # The outer trait is a TraitCompound. Recompute its
                # fast_validate table now that we have updated ours.
                # FIXME: there are probably still issues if the TraitCompound is
                # further nested.
                set_validate()
            else:
                item_trait = getattr(handler, "item_trait", None)
                if item_trait is not None and item_trait.handler is self:
                    # The outer trait is a List trait.
                    trait = item_trait
                    handler = self
                else:
                    return
        if handler.fast_validate is not None:
            trait.set_validate(handler.fast_validate)


class Instance(BaseInstance):
    """ A fast-validated trait type whose value is an instance of a class.
    """

    def init_fast_validate(self):
        """ Sets up the C-level fast validator. """

        if self.adapt == 0:
            fast_validate = [ValidateTrait.instance, self.klass]
            if self._allow_none:
                fast_validate = [ValidateTrait.instance, None, self.klass]
            else:
                fast_validate = [ValidateTrait.instance, self.klass]

            if self.klass in TypeTypes:
                fast_validate[0] = ValidateTrait.type

            self.fast_validate = tuple(fast_validate)
        else:
            self.fast_validate = (ValidateTrait.adapt, self.klass, self.adapt, self._allow_none)


class Supports(Instance):
    """ A trait type whose value is adatped to a specified protocol.

    In other words, the value of the trait directly provide, or can be adapted
    to, the given protocol (Interface or type).

    The value of the trait after assignment is the possibly adapted value
    (i.e., it is the original assigned value if that provides the protocol,
    or is an adapter otherwise).

    The original, unadapted value is stored in a "shadow" attribute with
    the same name followed by an underscore (e.g., ``foo`` and ``foo_``).
    """

    adapt_default = "yes"

    def post_setattr(self, object, name, value):
        """ Performs additional post-assignment processing.
        """
        # Save the original, unadapted value in the mapped trait:
        object.__dict__[name + "_"] = value

    def as_ctrait(self):
        """ Returns a CTrait corresponding to the trait defined by this class.
        """
        return self.modify_ctrait(super(Supports, self).as_ctrait())

    def modify_ctrait(self, ctrait):

        # Tell the C code that the 'post_setattr' method wants the original,
        # unadapted value passed to 'setattr':
        ctrait.post_setattr_original_value = True
        return ctrait


class AdaptsTo(Supports):
    """ A trait type whose value must support a specified protocol.

    In other words, the value of the trait directly provide, or can be adapted
    to, the given protocol (Interface or type).

    The value of the trait after assignment is the original, unadapted value.

    A possibly adapted value is stored in a "shadow" attribute with
    the same name followed by an underscore (e.g., ``foo`` and ``foo_``).
    """

    def modify_ctrait(self, ctrait):
        # Tell the C code that 'setattr' should store the original, unadapted
        # value passed to it:
        ctrait.setattr_original_value = True
        return ctrait


class Type(BaseClass):
    """ A trait type whose value must be a subclass of a specified class.

    Parameters
    ----------
    value : class or None
        The default value of the trait.
    klass : class, str or None
        The class that trait values must be subclasses of.  If None, then
        the default value is used instead.  If both are None, then the
        ``object`` type is used.  If it is a string, the first time that
        the validate method is called, the class will be imported and
        the value replaced with the class object.
    allow_none : bool
        Indicates whether None is allowed as an assignable value. Even if
        **False**, the default *value* may be **None**.
    **metadata
        Trait metadata for the trait.

    Attributes
    ----------
    klass : class or str
        The class that trait values must be subclasses of.  If this is a
        string, the first time that the validate method is called, the
        class will be imported and the value replaced with the class object.
    module : str
        The name of the module where local class names (ie. class names
        with no module components) are presumed to be importable from.
        This is the caller's caller's module, as determined by the
        ``get_module_method``.
    """

    def __init__(self, value=None, klass=None, allow_none=True, **metadata):
        if value is None:
            if klass is None:
                klass = object

        elif klass is None:
            klass = value

        if isinstance(klass, str):
            self.validate = self.resolve

        elif not isinstance(klass, type):
            raise TraitError("A Type trait must specify a class.")

        self.klass = klass
        self._allow_none = allow_none
        self.module = get_module_name()

        super(Type, self).__init__(value, **metadata)

    def validate(self, object, name, value):
        """ Validates that the value is a valid object instance.
        """
        try:
            if issubclass(value, self.klass):
                return value
        except:
            if (value is None) and (self._allow_none):
                return value

        self.error(object, name, value)

    def resolve(self, object, name, value):
        """ Resolves a class originally specified as a string into an actual
            class, then resets the trait so that future calls will be handled by
            the normal validate method.
        """
        if isinstance(self.klass, str):
            self.resolve_class(object, name, value)
            del self.validate

        return self.validate(object, name, value)

    def info(self):
        """ Returns a description of the trait.
        """
        klass = self.klass
        if not isinstance(klass, str):
            klass = klass.__name__

        result = "a subclass of " + klass

        if self._allow_none:
            return result + " or None"

        return result

    def get_default_value(self):
        """ Returns a tuple of the form: ( default_value_type, default_value )
        which describes the default value for this trait.
        """
        if not isinstance(self.default_value, str):
            return super(Type, self).get_default_value()

        return (
            DefaultValue.callable_and_args,
            (self.resolve_default_value, (), None),
        )

    def resolve_default_value(self):
        """ Resolves a class name into a class so that it can be used to
            return the class as the default value of the trait.
        """
        if isinstance(self.klass, str):
            try:
                self.resolve_class(None, None, None)
                del self.validate
            except:
                raise TraitError(
                    "Could not resolve %s into a valid class" % self.klass
                )

        return self.klass


#: An alias for the Type trait
Subclass = Type


class Event(TraitType):
    """ A trait type that holds no value but can be set and listend to.

    Event traits are write-only traits.  They do not hold any value, but
    they can be assigned to, and listeners to the trait will be notified
    of the assignment.  Since no value is held, trait change functions that
    ask for the ``old`` value of the trait will be given the Undefined
    special value.

    Event traits can be given an optional trait type that is used to validate
    values assigned to the trait.  If the assigned value does not validate,
    then a TraitError will occur.

    Parameters
    ----------
    trait : a trait
        The type of value that can be assigned to the event.
    """

    def __init__(self, trait=None, **metadata):
        metadata["type"] = "event"
        metadata["transient"] = True

        super(Event, self).__init__(**metadata)

        self.trait = None
        if trait is not None:
            self.trait = trait_from(trait)
            validate = self.trait.get_validate()
            if validate is not None:
                self.fast_validate = validate

    def full_info(self, object, name, value):
        """ Returns a description of the trait.
        """
        trait = self.trait
        if trait is None:
            return "any value"

        return trait.full_info(object, name, value)


class Button(Event):
    """ An Event trait type whose UI editor is a button.

    Parameters
    ----------
    label : str
        The label for the button.
    image : pyface.ImageResource
        An image to display on the button.
    style : 'button', 'radio', 'toolbar' or 'checkbox'
        The style of button to display.
    values_trait : str
        For a "button" or "toolbar" style, the name of an enum
        trait whose values will populate a drop-down menu on the button.
        The selected value will replace the label on the button.
    orientation : 'horizontal' or 'vertical'
        The orientation of the label relative to the image.
    width_padding : integer between 0 and 31
        Extra padding (in pixels) added to the left and right sides of
        the button.
    height_padding : integer between 0 and 31
        Extra padding (in pixels) added to the top and bottom of the
        button.
    view : traitsui View, optional
        An optional View to display when the button is clicked.
    **metadata
        Trait metadata for the trait.

    Attributes
    ----------
    label : str
        The label for the button.
    image : pyface.ImageResource
        An image to display on the button.
    style : 'button', 'radio', 'toolbar' or 'checkbox'
        The style of button to display.
    values_trait : str
        For a "button" or "toolbar" style, the name of an enum
        trait whose values will populate a drop-down menu on the button.
        The selected value will replace the label on the button.
    orientation : 'horizontal' or 'vertical'
        The orientation of the label relative to the image.
    width_padding : integer between 0 and 31
        Extra padding (in pixels) added to the left and right sides of
        the button.
    height_padding : integer between 0 and 31
        Extra padding (in pixels) added to the top and bottom of the
        button.
    view : traitsui View, optional
        An optional View to display when the button is clicked.
    """

    def __init__(
        self,
        label="",
        image=None,
        values_trait=None,
        style="button",
        orientation="vertical",
        width_padding=7,
        height_padding=5,
        view=None,
        **metadata
    ):
        self.label = label
        self.values_trait = values_trait
        self.image = image
        self.style = style
        self.orientation = orientation
        self.width_padding = width_padding
        self.height_padding = height_padding
        self.view = view
        super(Button, self).__init__(**metadata)

    def create_editor(self):
        from traitsui.api import ButtonEditor

        editor = ButtonEditor(
            label=self.label,
            values_trait=self.values_trait,
            image=self.image,
            style=self.style,
            orientation=self.orientation,
            width_padding=self.width_padding,
            height_padding=self.height_padding,
            view=self.view,
        )
        return editor


class ToolbarButton(Button):
    """ A Button trait type whose UI editor is a toolbar button.

    This is just a Button trait with different defaults to style it like
    a toolbar button.

    Parameters
    ----------
    label : str
        The label for the button.
    image : pyface.ImageResource
        An image to display on the button.
    style : 'button', 'radio', 'toolbar' or 'checkbox'
        The style of button to display.
    orientation : 'horizontal' or 'vertical'
        The orientation of the label relative to the image.
    width_padding : integer between 0 and 31
        Extra padding (in pixels) added to the left and right sides of
        the button.
    height_padding : integer between 0 and 31
        Extra padding (in pixels) added to the top and bottom of the
        button.
    **metadata
        Trait metadata for the trait.

    Attributes
    ----------
    label : str
        The label for the button.
    image : pyface.ImageResource
        An image to display on the button.
    style : 'button', 'radio', 'toolbar' or 'checkbox'
        The style of button to display.
    values_trait : str
        For a "button" or "toolbar" style, the name of an enum
        trait whose values will populate a drop-down menu on the button.
        The selected value will replace the label on the button.
    orientation : 'horizontal' or 'vertical'
        The orientation of the label relative to the image.
    width_padding : integer between 0 and 31
        Extra padding (in pixels) added to the left and right sides of
        the button.
    height_padding : integer between 0 and 31
        Extra padding (in pixels) added to the top and bottom of the
        button.
    view : traitsui View, optional
        An optional View to display when the button is clicked.
    """

    def __init__(
        self,
        label="",
        image=None,
        style="toolbar",
        orientation="vertical",
        width_padding=2,
        height_padding=2,
        **metadata
    ):
        super(ToolbarButton, self).__init__(
            label,
            image=image,
            style=style,
            orientation=orientation,
            width_padding=width_padding,
            height_padding=height_padding,
            **metadata
        )


class Either(TraitType):
    """ A trait type whose value can be any of of a specified list of traits.

    Parameters
    ----------
    *traits
        Arguments that define allowable trait values.
    **metadata
        Trait metadata for the trait.

    Attributes
    ----------
    trait_maker : TraitHandler
        A TraitHandler generated by _TraitMaker from the arguments.
    """

    def __init__(self, *traits, **metadata):
        self.trait_maker = _TraitMaker(
            metadata.pop("default", None), *traits, **metadata
        )

    def as_ctrait(self):
        """ Returns a CTrait corresponding to the trait defined by this class.
        """
        return self.trait_maker.as_ctrait()


class Symbol(TraitType):
    """ A property trait type that refers to a Python object by name.

    The value set to the trait must be a value of the form
    ``'[package.package...package.]module[:symbol[([arg1,...,argn])]]'``
    which is imported and evaluated to get underlying value.

    The value returned by the trait is the actual object that this string
    refers to.  The value is cached, so any calls are only evaluated once.
    """

    #: A description of the type of value this trait accepts:
    info_text = (
        "an object or a string of the form "
        "'[package.package...package.]module[:symbol[([arg1,...,argn])]]' "
        "specifying where to locate the object"
    )

    def get(self, object, name):
        value = object.__dict__.get(name, Undefined)
        if value is Undefined:
            cache = TraitsCache + name
            ref = object.__dict__.get(cache)
            if ref is None:
                object.__dict__[cache] = ref = object.trait(
                    name
                ).default_value_for(object, name)

            if isinstance(ref, str):
                object.__dict__[name] = value = self._resolve(ref)

        return value

    def set(self, object, name, value):
        dict = object.__dict__
        old = dict.get(name, Undefined)
        if isinstance(value, str):
            dict.pop(name, None)
            dict[TraitsCache + name] = value
            object.trait_property_changed(name, old)
        else:
            dict[name] = value
            object.trait_property_changed(name, old, value)

    def _resolve(self, ref):
        try:
            elements = ref.split("(", 1)
            symbol = import_symbol(elements[0])
            if len(elements) == 1:
                return symbol

            args = eval("(" + elements[1])
            if not isinstance(args, tuple):
                args = (args,)

            return symbol(*args)
        except Exception:
            raise TraitError(
                "Could not resolve '%s' into a valid symbol." % ref
            )


class UUID(TraitType):
    """ A read-only trait type whose value is a globally unique UUID (type 4).

    Parameters
    ----------
    can_init : bool
        Whether the value can be set during object instantiation.  Otherwise
        the UUID is generated automatically.

    Example
    -------

    Passing `can_init=True` allows the UUID value to be set during
    object instantiation, e.g.::

        class A(HasTraits):
            id = UUID

        class B(HasTraits):
            id = UUID(can_init=True)

        # TraitError!
        A(id=uuid.uuid4())

        # Okay!
        B(id=uuid.uuid4())

    Note however that in both cases, the UUID trait is set automatically
    to a `uuid.UUID` instance (assuming none is provided during initialization
    in the latter case).
    """

    #: A description of the type of value this trait accepts:
    info_text = "a read-only UUID"

    def __init__(self, can_init=False, **metadata):
        super(UUID, self).__init__(None, **metadata)
        self.can_init = can_init

    def validate(self, object, name, value):
        """ Raises an error, since no values can be assigned to the trait.
        """
        if not self.can_init:
            raise TraitError(
                "The '%s' trait of %s instance is a read-only "
                "UUID." % (name, class_of(object))
            )

        if object.traits_inited():
            msg = ("Initializable UUID trait is read-only "
                   "after initialization")
            raise TraitError(msg)

        if isinstance(value, uuid.UUID):
            return value

        try:
            # Construct the UUID from a string
            return uuid.UUID(value)
        except ValueError:
            msg = ("The '{}' trait of '{}' expects an RFC 4122-compatible "
                   "UUID value, but '{}' was given")
            raise TraitError(msg.format(name, type(object).__name__, value))

    def get_default_value(self):
        """ Return a Traits default value tuple for the trait.

        This uses the _create_uuid method to generate the defualt value.
        """
        return (
            DefaultValue.callable_and_args,
            (self._create_uuid, (), None),
        )

    # -- Private Methods ---------------------------------------------------

    def _create_uuid(self):
        return uuid.uuid4()


class WeakRef(Instance):
    """ A trait type holding a weak reference to an instance of a class.

    Only a weak reference is maintained to any object assigned to a WeakRef
    trait. If no other references exist to the assigned value, the value
    may be garbage collected, in which case the value of the trait becomes
    None. In all other cases, the value returned by the trait is the
    original object.

    Parameters
    ----------
    klass : class, str or instance
        The object that forms the basis for the trait. If *klass* is
        omitted, then values must be an instance of HasTraits.  If a string,
        the value will be resolved to a class object at runtime.
    allow_none : boolean
        Indicates whether None can be _assigned_.  The trait attribute may
        give a None value if the object referred to has been garbage collected
        even if allow_none is False.
    adapt : str
        How to use the adaptation infrastructure when setting the value.
    """

    def __init__(
        self,
        klass="traits.has_traits.HasTraits",
        allow_none=False,
        adapt="yes",
        **metadata
    ):
        metadata.setdefault("copy", "ref")

        super(WeakRef, self).__init__(
            klass,
            allow_none=allow_none,
            adapt=adapt,
            module=get_module_name(),
            **metadata
        )

    def get(self, object, name):
        value = getattr(object, name + "_", None)
        if value is not None:
            return value.value()

        return None

    def set(self, object, name, value):
        old = self.get(object, name)

        if value is None:
            object.__dict__[name + "_"] = None
        else:
            object.__dict__[name + "_"] = HandleWeakRef(object, name, value)

        if value is not old:
            object.trait_property_changed(name, old, value)

    def resolve_class(self, object, name, value):
        # fixme: We have to override this method to prevent the 'fast validate'
        # from being set up, since the trait using this is a 'property' style
        # trait which is not currently compatible with the 'fast_validate'
        # style (causes internal Python SystemError messages).
        klass = self.find_class(self.klass)
        if klass is None:
            self.validate_failed(object, name, value)

        self.klass = klass


#: A trait type for datetime.date instances.
Date = BaseInstance(datetime.date, editor=date_editor)


#: A trait type for datetime.datetime instances.
Datetime = BaseInstance(datetime.datetime, editor=datetime_editor)


#: A trait type for datetime.time instances.
Time = BaseInstance(datetime.time, editor=time_editor)


# -----------------------------------------------------------------------------
#  Create predefined, reusable trait instances:
# -----------------------------------------------------------------------------

# Everything from this point onwards is deprecated, and has a simple
# drop-in replacement.

#: A trait whose value must support a specified protocol. This is
#: an alias for :class:`Supports`. Use ``Supports`` instead.
AdaptedTo = Supports

#: A trait whose value must be a (Unicode) string. This is an alias for
#: :class:`BaseStr`. Use ``BaseStr`` instead.
BaseUnicode = BaseStr

#: A trait whose value must be a (Unicode) string, using a C-level
#: fast validator. This is an alias for :class:`Str`. Use ``Str`` instead.
Unicode = Str

#: A trait whose value must be a (Unicode) string and which supports
#: coercions of non-string values to string. This is
#: an alias for :class:`BaseCStr`. Use ``BaseCStr`` instead.
BaseCUnicode = BaseCStr

#: A trait whose value must be a (Unicode) string and which supports
#: coercions of non-string values to string, using a C-level fast validator.
#: This is an alias for :class:`CStr`. Use ``CStr`` instead.
CUnicode = CStr

#: A trait whose value must be an integer. This is an alias for
#: :class:`BaseInt`. Use ``BaseInt`` instead.
BaseLong = BaseInt

#: A trait whose value must be an integer, using a C-level fast validator.
#: This is an alias for :class:`Int`. Use ``Int`` instead.
Long = Int

#: A trait whose value must be an integer and which supports coercions
#: of non-integer values to integer. This is an alias for
#: :class:`BaseCInt`. Use ``BaseCInt`` instead.
BaseCLong = BaseCInt

#: A trait whose value must be an integer and which supports coercions
#: of non-integer values to integer, using a C-level fast validator.
#: This is an alias for :class:`CInt`. Use ``CInt`` instead.
CLong = CInt

#: Synonym for Bool; default value is ``False``. This trait type is
#: deprecated. Use ``Bool(False)`` or ``Bool()`` instead.
false = Bool

#: Boolean values only; default value is ``True``. This trait type is
#: deprecated. Use ``Bool(True)`` instead.
true = Bool(True)

#: Allows any value to be assigned; no type-checking is performed.
#: Default value is ``Undefined``. This trait type is deprecated. Use
#: ``Any(Undefined)`` instead.
undefined = Any(Undefined)

# -- List Traits --------------------------------------------------------------

#: List of integer values; default value is ``[]``. This trait type is
#: deprecated. Use ``List(Int)`` instead.
ListInt = List(int)

#: List of float values; default value is ``[]``. This trait type is
#: deprecated. Use ``List(Float)`` instead.
ListFloat = List(float)

#: List of string values; default value is ``[]``. This trait type is
#: deprecated. Use ``List(Str)`` instead.
ListStr = List(str)

#: List of string values; default value is ``[]``. This trait type is
#: deprecated. Use ``List(Str)`` instead.
ListUnicode = List(str)

#: List of complex values; default value is ``[]``. This trait type is
#: deprecated. Use ``List(Complex)`` instead.
ListComplex = List(complex)

#: List of Boolean values; default value is ``[]``. This trait type is
#: deprecated. Use ``List(Bool)`` instead.
ListBool = List(bool)

#: List of function values; default value is ``[]``. This trait type is
#: deprecated. Use ``List(Instance(types.FunctionType, allow_none=False))``
#: instead.
ListFunction = List(FunctionType)

#: List of method values; default value is ``[]``. This trait type is
#: deprecated. Use ``List(Instance(types.MethodType, allow_none=False))``
#: instead.
ListMethod = List(MethodType)

#: List of container type values; default value is ``[]``. This trait type is
#: deprecated. Use ``List(This(allow_none=False))`` instead.
ListThis = List(This(allow_none=False))

# -- Dictionary Traits --------------------------------------------------------

#: Only a dictionary with strings as keys can be assigned; only string keys
#: can be inserted. The default value is {}. This trait type is deprecated. Use
#: ``Dict(Str, Any)`` instead.
DictStrAny = Dict(str, Any)

#: Only a dictionary mapping strings to strings can be assigned; only string
#: keys with string values can be inserted. The default value is {}. This trait
#: type is deprecated. Use ``Dict(Str, Str)`` instead.
DictStrStr = Dict(str, str)

#: Only a dictionary mapping strings to integers can be assigned; only string
#: keys with integer values can be inserted. The default value is {}. This
#: trait type is deprecated. Use ``Dict(Str, Int)`` instead.
DictStrInt = Dict(str, int)

#: Only a dictionary mapping strings to floats can be assigned; only string
#: keys with float values can be inserted. The default value is {}. This trait
#: type is deprecated. Use ``Dict(Str, Float)`` instead.
DictStrFloat = Dict(str, float)

#: Only a dictionary mapping strings to booleans can be assigned; only string
#: keys with boolean values can be inserted. The default value is {}. This
#: trait type is deprecated. Use ``Dict(Str, Bool)`` instead.
DictStrBool = Dict(str, bool)

#: Only a dictionary mapping strings to lists can be assigned; only string keys
#: with list values can be inserted. The default value is {}. This trait type
#: is deprecated. Use ``Dict(Str, List)`` instead.
DictStrList = Dict(str, list)
