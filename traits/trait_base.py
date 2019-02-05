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

""" Defines common, low-level capabilities needed by the Traits package.
"""

# -------------------------------------------------------------------------------
#  Imports:
# -------------------------------------------------------------------------------

from __future__ import absolute_import

import os
import sys
from os import getcwd
from os.path import dirname, exists, join

import six

from . import _py2to3
from ._py2to3 import LONG_TYPE

from .etsconfig.api import ETSConfig

# backwards compatibility: trait_base used to provide a patched enumerate
enumerate = enumerate

# -------------------------------------------------------------------------------
#  Constants:
# -------------------------------------------------------------------------------

ClassTypes = _py2to3.ClassTypes

SequenceTypes = (list, tuple)

ComplexTypes = (float, int)

TypeTypes = (
    str,
    six.text_type,
    int,
    LONG_TYPE,
    float,
    complex,
    list,
    tuple,
    dict,
    bool,
)

TraitNotifier = "__trait_notifier__"

# The standard Traits property cache prefix:
TraitsCache = "_traits_cache_"

# -------------------------------------------------------------------------------
#  Singleton 'Uninitialized' object:
# -------------------------------------------------------------------------------
Uninitialized = None


class _Uninitialized(object):
    """ The singleton value of this class represents the uninitialized state
        of a trait and is specified as the 'old' value in the trait change
        notification that occurs when the value of a trait is read before being
        set.
    """

    def __new__(cls):
        if Uninitialized is not None:
            return Uninitialized
        else:
            self = object.__new__(cls)
            return self

    def __repr__(self):
        return "<uninitialized>"

    def __reduce_ex__(self, protocol):
        return (_Uninitialized, ())


#: When the first reference to a trait is a 'get' reference, the default value of
#: the trait is implicitly assigned and returned as the value of the trait.
#: Because of this implicit assignment, a trait change notification is
#: generated with the Uninitialized object as the 'old' value of the trait, and
#: the default trait value as the 'new' value. This allows other parts of the
#: traits package to recognize the assignment as the implicit default value
#: assignment, and treat it specially.
Uninitialized = _Uninitialized()

# -------------------------------------------------------------------------------
#  Singleton 'Undefined' object (used as undefined trait name and/or value):
# -------------------------------------------------------------------------------

Undefined = None


class _Undefined(object):
    """ Singleton 'Undefined' object (used as undefined trait name and/or value)
    """

    def __new__(cls):
        if Undefined is not None:
            return Undefined
        else:
            self = object.__new__(cls)
            return self

    def __repr__(self):
        return "<undefined>"

    def __reduce_ex__(self, protocol):
        return (_Undefined, ())

    def __eq__(self, other):
        return type(self) is type(other)

    def __hash__(self):
        return hash(type(self))

    def __ne__(self, other):
        return type(self) is not type(other)


#: Singleton object that indicates that a trait attribute has not yet had a
#: value set (i.e., its value is undefined). This object is used instead of
#: None, because None often has other meanings, such as that a value is not
#: used. When a trait attribute is first assigned a value, and its associated
#: trait notification handlers are called, Undefined is passed as the *old*
#: parameter, to indicate that the attribute previously had no value.
Undefined = _Undefined()

# Tell the C-base code about singleton 'Undefined' and 'Uninitialized' objects:
from . import ctraits

ctraits._undefined(Undefined, Uninitialized)

# -------------------------------------------------------------------------------
#  Singleton 'Missing' object (used as missing method argument marker):
# -------------------------------------------------------------------------------


class Missing(object):
    """ Singleton 'Missing' object (used as missing method argument marker).
    """

    def __repr__(self):
        return "<missing>"


#: Singleton object that indicates that a method argument is missing from a
#: type-checked method signature.
Missing = Missing()

# -------------------------------------------------------------------------------
#  Singleton 'Self' object (used as object reference to current 'object'):
# -------------------------------------------------------------------------------


class Self(object):
    """ Singleton 'Self' object (used as object reference to current 'object').
    """

    def __repr__(self):
        return "<self>"


#: Singleton object that references the current 'object'.
Self = Self()

# -------------------------------------------------------------------------------
#  Define a special 'string' coercion function:
# -------------------------------------------------------------------------------


def strx(arg):
    """ Wraps the built-in str() function to raise a TypeError if the
    argument is not of a type in StringTypes.
    """
    if isinstance(arg, StringTypes):
        return str(arg)
    raise TypeError


# -------------------------------------------------------------------------------
#  Constants:
# -------------------------------------------------------------------------------

StringTypes = (str, six.text_type, int, LONG_TYPE, float, complex)

# -------------------------------------------------------------------------------
#  Define a mapping of coercable types:
# -------------------------------------------------------------------------------

# Mapping of coercable types.
CoercableTypes = {
    LONG_TYPE: (11, LONG_TYPE, int),
    float: (11, float, int),
    complex: (11, complex, float, int),
    six.text_type: (11, six.text_type, str),
}

# -------------------------------------------------------------------------------
#  Return a string containing the class name of an object with the correct
#  article (a or an) preceding it (e.g. 'an Image', 'a PlotValue'):
# -------------------------------------------------------------------------------


def class_of(object):
    """ Returns a string containing the class name of an object with the
    correct indefinite article ('a' or 'an') preceding it (e.g., 'an Image',
    'a PlotValue').
    """
    if isinstance(object, six.string_types):
        return add_article(object)

    return add_article(object.__class__.__name__)


# -------------------------------------------------------------------------------
#  Return a string containing the right article (i.e. 'a' or 'an') prefixed to
#  a specified string:
# -------------------------------------------------------------------------------


def add_article(name):
    """ Returns a string containing the correct indefinite article ('a' or 'an')
    prefixed to the specified string.
    """
    if name[:1].lower() in "aeiou":
        return "an " + name

    return "a " + name


# ----------------------------------------------------------------------------
#  Return a 'user-friendly' name for a specified trait:
# ----------------------------------------------------------------------------


def user_name_for(name):
    """ Returns a "user-friendly" version of a string, with the first letter
    capitalized and with underscore characters replaced by spaces. For example,
    ``user_name_for('user_name_for')`` returns ``'User name for'``.
    """
    name = name.replace("_", " ")
    result = ""
    last_lower = False

    for c in name:
        if c.isupper() and last_lower:
            result += " "
        last_lower = c.islower()
        result += c

    return result.capitalize()


# -------------------------------------------------------------------------------
#  Gets the path to the traits home directory:
# -------------------------------------------------------------------------------

_traits_home = None


def traits_home():
    """ Gets the path to the Traits home directory.
    """
    global _traits_home

    if _traits_home is None:
        _traits_home = verify_path(join(ETSConfig.application_data, "traits"))

    return _traits_home


# -------------------------------------------------------------------------------
#  Verify that a specified path exists, and try to create it if it doesn't:
# -------------------------------------------------------------------------------


def verify_path(path):
    """ Verify that a specified path exists, and try to create it if it
        does not exist.
    """
    if not exists(path):
        try:
            os.mkdir(path)
        except:
            pass

    return path


# -------------------------------------------------------------------------------
#  Returns the name of the module the caller's caller is located in:
# -------------------------------------------------------------------------------


def get_module_name(level=2):
    """ Returns the name of the module that the caller's caller is located in.
    """
    return sys._getframe(level).f_globals.get("__name__", "__main__")


# -------------------------------------------------------------------------------
#  Returns a resource path calculated from the caller's stack:
# -------------------------------------------------------------------------------


def get_resource_path(level=2):
    """Returns a resource path calculated from the caller's stack.
    """
    module = sys._getframe(level).f_globals.get("__name__", "__main__")

    path = None
    if module != "__main__":
        # Return the path to the module:
        try:
            path = dirname(getattr(sys.modules.get(module), "__file__"))
        except:
            # Apparently 'module' is not a registered module...treat it like
            # '__main__':
            pass

    if path is None:
        # '__main__' is not a real module, so we need a work around:
        for path in [dirname(sys.argv[0]), getcwd()]:
            if exists(path):
                break

    # Handle application bundlers.  Since the python source files may be placed
    # in a zip file and therefore won't be directly accessable using standard
    # open/read commands, the app bundlers will look for resources (i.e.  data
    # files, images, etc.) in specific locations.  For py2app, this is in the
    # [myapp].app/Contents/Resources directory.  For py2exe, this is the same
    # directory as the [myapp].exe executable file generated by py2exe.  For
    # pyinstaller, the attribute sys._MEIPASS is set to this directory.
    frozen = getattr(sys, "frozen", False)
    if frozen:
        if hasattr(sys, "_MEIPASS"):
            root = sys._MEIPASS
        elif frozen == "macosx_app":
            root = os.environ["RESOURCEPATH"]
        elif frozen in ("dll", "windows_exe", "console_exe"):
            root = os.path.dirname(sys.executable)
        else:
            # Unknown app bundler, but try anyway
            root = os.path.dirname(sys.executable)
        if ".zip/" in path:
            zippath, image_path = path.split(".zip/")
            path = os.path.join(root, image_path)

    return path


# -------------------------------------------------------------------------------
#  Returns the value of an extended object attribute name of the form:
#  name[.name2[.name3...]]:
# -------------------------------------------------------------------------------


def xgetattr(object, xname, default=Undefined):
    """ Returns the value of an extended object attribute name of the form:
        name[.name2[.name3...]].
    """
    names = xname.split(".")
    for name in names[:-1]:
        if default is Undefined:
            object = getattr(object, name)
        else:
            object = getattr(object, name, None)
            if object is None:
                return default

    if default is Undefined:
        return getattr(object, names[-1])

    return getattr(object, names[-1], default)


# -------------------------------------------------------------------------------
#  Sets the value of an extended object attribute name of the form:
#  name[.name2[.name3...]]:
# -------------------------------------------------------------------------------


def xsetattr(object, xname, value):
    """ Sets the value of an extended object attribute name of the form:
        name[.name2[.name3...]].
    """
    names = xname.split(".")
    for name in names[:-1]:
        object = getattr(object, name)

    setattr(object, names[-1], value)


# -------------------------------------------------------------------------------
#  Traits metadata selection functions:
# -------------------------------------------------------------------------------


def is_none(value):
    return value is None


def not_none(value):
    return value is not None


def not_false(value):
    return value is not False


def not_event(value):
    return value != "event"


def is_str(value):
    return isinstance(value, six.string_types)
