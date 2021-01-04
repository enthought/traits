# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Trait definitions related to the numpy library.
"""

import warnings

from .constants import ComparisonMode, DefaultValue
from .trait_base import SequenceTypes
from .trait_errors import TraitError
from .trait_type import TraitType
from .trait_types import Str, Any, Int as TInt, Float as TFloat


# Deferred imports from numpy:
ndarray = None
asarray = None


def dtype2trait(dtype):
    """ Get the corresponding trait for a numpy dtype.
    """

    import numpy

    if dtype.char in numpy.typecodes["Float"]:
        return TFloat

    elif dtype.char in numpy.typecodes["AllInteger"]:
        return TInt

    elif dtype.char[0] == "S":
        return Str

    else:
        return Any


class AbstractArray(TraitType):
    """ Abstract base class for defining numpy-based arrays.
    """

    def __init__(
        self,
        dtype=None,
        shape=None,
        value=None,
        coerce=False,
        typecode=None,
        *,
        casting="unsafe",
        **metadata
    ):
        global ndarray, asarray

        try:
            import numpy
        except ImportError:
            raise TraitError(
                "Using Array or CArray trait types requires the "
                "numpy package to be installed."
            )

        from numpy import asarray, ndarray

        # Mark this as being an 'array' trait:
        metadata["array"] = True

        # Normally use object identity to detect array values changing:
        metadata.setdefault("comparison_mode", ComparisonMode.identity)

        if typecode is not None:
            warnings.warn(
                "typecode is a deprecated argument; use dtype " "instead",
                DeprecationWarning,
            )

            if (dtype is not None) and (dtype != typecode):
                raise TraitError(
                    "Inconsistent usage of the dtype and "
                    "typecode arguments; use dtype alone."
                )
            else:
                dtype = typecode

        if dtype is not None:
            try:
                # Convert the argument into an actual numpy dtype object:
                dtype = numpy.dtype(dtype)
            except TypeError:
                raise TraitError(
                    "could not convert %r to a numpy dtype" % dtype
                )

        if shape is not None:
            if isinstance(shape, SequenceTypes):
                for item in shape:
                    if (
                        (item is None)
                        or (type(item) is int)
                        or (
                            isinstance(item, SequenceTypes)
                            and (len(item) == 2)
                            and (type(item[0]) is int)
                            and (item[0] >= 0)
                            and (
                                (item[1] is None)
                                or (
                                    (type(item[1]) is int)
                                    and (item[0] <= item[1])
                                )
                            )
                        )
                    ):
                        continue

                    raise TraitError("shape should be a list or tuple")
            else:
                raise TraitError("shape should be a list or tuple")

        if value is None:
            value = self._default_for_dtype_and_shape(dtype, shape)

        self.dtype = dtype
        self.shape = shape
        self.coerce = coerce
        self.casting = casting

        super().__init__(value, **metadata)

    def validate(self, object, name, value):
        """ Validates that the value is a valid array.
        """
        try:
            # Make sure the value is an array:
            if not isinstance(value, ndarray):
                if not isinstance(value, SequenceTypes):
                    self.error(object, name, value)
                if self.dtype is not None:
                    value = asarray(value, self.dtype)
                else:
                    value = asarray(value)

            # Make sure the array is of the right type:
            if (self.dtype is not None) and (value.dtype != self.dtype):
                value = value.astype(self.dtype, casting=self.casting)

            # If no shape requirements, then return the value:
            trait_shape = self.shape
            if trait_shape is None:
                return value

            # Else make sure that the value's shape is compatible:
            value_shape = value.shape
            if len(trait_shape) == len(value_shape):
                for i, dim in enumerate(value_shape):
                    item = trait_shape[i]
                    if item is not None:
                        if type(item) is int:
                            if dim != item:
                                break
                        elif (dim < item[0]) or (
                            (item[1] is not None) and (dim > item[1])
                        ):
                            break
                else:
                    return value
        except:
            pass

        self.error(object, name, value)

    def info(self):
        """ Returns descriptive information about the trait.
        """
        dtype = shape = ""

        if self.shape is not None:
            shape = []
            for item in self.shape:
                if item is None:
                    item = "*"
                elif type(item) is not int:
                    if item[1] is None:
                        item = "%d.." % item[0]
                    else:
                        item = "%d..%d" % item
                shape.append(item)
            shape = " with shape %s" % (tuple(shape),)

        if self.dtype is not None:
            # FIXME: restore nicer descriptions of dtypes.
            dtype = " of %s values" % self.dtype

        return "an array%s%s" % (dtype, shape)

    def create_editor(self):
        """ Returns the default UI editor for the trait.
        """
        editor = None

        auto_set = False
        if self.auto_set is None:
            auto_set = True
        enter_set = self.enter_set or False

        if self.shape is not None and len(self.shape) == 2:
            from traitsui.api import ArrayEditor

            editor = ArrayEditor(auto_set=auto_set, enter_set=enter_set)
        else:
            from traitsui.api import TupleEditor

            if self.dtype is None:
                types = Any
            else:
                types = dtype2trait(self.dtype)
            editor = TupleEditor(
                types=types,
                labels=self.labels or [],
                cols=self.cols or 1,
                auto_set=auto_set,
                enter_set=enter_set,
            )
        return editor

    # -- Private Methods ------------------------------------------------------

    def get_default_value(self):
        """ Returns the default value constructor for the type (called from the
            trait factory.
        """
        return (
            DefaultValue.callable_and_args,
            (
                self.copy_default_value,
                (self.validate(None, None, self.default_value),),
                None,
            ),
        )

    def copy_default_value(self, value):
        """ Returns a copy of the default value (called from the C code on
            first reference to a trait with no current value).
        """
        return value.copy()

    def _default_for_dtype_and_shape(self, dtype, shape):
        """ Invent a suitable default value for a given dtype and shape. """
        from numpy import zeros

        if dtype is None:
            # Compatibility with the default of Traits 2.0
            dt = int
        else:
            dt = dtype
        if shape is None:
            value = zeros((0,), dt)
        else:
            size = []
            for item in shape:
                if item is None:
                    item = 1
                elif type(item) in SequenceTypes:
                    # Given a (minimum-allowed-length, maximum-allowed_length)
                    # pair for a particular axis, use the minimum.
                    item = item[0]
                size.append(item)
            value = zeros(size, dt)
        return value


class Array(AbstractArray):
    """ A trait type whose value must be a NumPy array.

    An Array trait allows only upcasting of assigned values that are
    already numpy arrays. It automatically casts tuples and lists of the
    right shape to the specified *dtype* (just like numpy's **array**
    does).

    The default value is either the *value* argument or
    ``zeros(min(shape))``, where ``min(shape)`` refers to the minimum
    shape allowed by the array. If *shape* is not specified, the minimum
    shape is (0,).

    Parameters
    ----------
    dtype : a numpy dtype (e.g., int32)
        The type of elements in the array; if omitted, no type-checking is
        performed on assigned values.
    shape : a tuple
        Describes the required shape of any assigned value. Wildcards and
        ranges are allowed. The value None within the *shape* tuple means
        that the corresponding dimension is not checked. (For example,
        ``shape=(None,3)`` means that the first dimension can be any size,
        but the second must be 3.) A two-element tuple within the *shape*
        tuple means that the dimension must be in the specified range. The
        second element can be None to indicate that there is no upper
        bound. (For example, ``shape=((3,5),(2,None))`` means that the
        first dimension must be in the range 3 to 5 (inclusive), and the
        second dimension must be at least 2.)
    value : numpy array
        A default value for the array.
    casting : str
        Casting rule for the array's dtype. If ``dtype`` is set, a value can
        only be assigned if it passes the casting rule. Values can be:

        - "no": No casting is allowed
        - "equiv": Only byte-order changes are allowed
        - "safe": Only allow casting that fully preserves values (e.g.
          "float32" to "float64")
        - "same-kind": Only safe casts or casts within a kind (e.g. "float64"
          to "float32") are allowed
        - "unsafe": Any casting is allowed

        Default is "unsafe".
    """

    def __init__(
        self,
        dtype=None,
        shape=None,
        value=None,
        typecode=None,
        *,
        casting="unsafe",
        **metadata
    ):
        super().__init__(
            dtype,
            shape,
            value,
            False,
            typecode=typecode,
            casting=casting,
            **metadata
        )


class CArray(AbstractArray):
    """ A coercing trait type whose value is a NumPy array.

    The trait returned by CArray() is similar to that returned by Array(),
    except that it allows both upcasting and downcasting of assigned values
    that are already numpy arrays. It automatically casts tuples and
    lists of the right shape to the specified *dtype* (just like
    numpy's **array** does).

    The default value is either the *value* argument or
    ``zeros(min(shape))``, where ``min(shape)`` refers to the minimum
    shape allowed by the array. If *shape* is not specified, the minimum
    shape is (0,).

    Parameters
    ----------
    dtype : a numpy dtype (e.g., int32)
        The type of elements in the array.
    shape : a tuple
        Describes the required shape of any assigned value. Wildcards and
        ranges are allowed. The value None within the *shape* tuple means
        that the corresponding dimension is not checked. (For example,
        ``shape=(None,3)`` means that the first dimension can be any size,
        but the second must be 3.) A two-element tuple within the *shape*
        tuple means that the dimension must be in the specified range. The
        second element can be None to indicate that there is no upper
        bound. (For example, ``shape=((3,5),(2,None))`` means that the
        first dimension must be in the range 3 to 5 (inclusive), and the
        second dimension must be at least 2.)
    value : numpy array
        A default value for the array.
    casting : str
        Casting rule for the array's dtype. If ``dtype`` is set, a value can
        only be assigned if it passes the casting rule. Values can be:

        - "no": No casting is allowed
        - "equiv": Only byte-order changes are allowed
        - "safe": Only allow casting that fully preserves values (e.g.
          "float32" to "float64")
        - "same-kind": Only safe casts or casts within a kind (e.g. "float64"
          to "float32") are allowed
        - "unsafe": Any casting is allowed

        Default is "unsafe".
    """

    def __init__(
        self,
        dtype=None,
        shape=None,
        value=None,
        typecode=None,
        *,
        casting="unsafe",
        **metadata
    ):
        super().__init__(
            dtype,
            shape,
            value,
            True,
            typecode=typecode,
            casting=casting,
            **metadata
        )


class ArrayOrNone(CArray):
    """ A coercing trait whose value may be either a NumPy array or None.

    This trait is designed to avoid the comparison issues with numpy arrays
    that can arise from the use of constructs like Either(None, Array).

    The default value is None.
    """

    def __init__(self, *args, **metadata):
        # Normally use object identity to detect array values changing:
        metadata.setdefault("comparison_mode", ComparisonMode.identity)
        super().__init__(*args, **metadata)

    def validate(self, object, name, value):
        if value is None:
            return value
        return super().validate(object, name, value)

    def get_default_value(self):
        dv = self.default_value
        if dv is None:
            return (DefaultValue.constant, dv)
        else:
            return (
                DefaultValue.callable_and_args,
                (
                    self.copy_default_value,
                    (self.validate(None, None, dv),),
                    None,
                ),
            )

    def _default_for_dtype_and_shape(self, dtype, shape):
        # For ArrayOrNone, if no default is explicitly specified, we
        # always default to `None`.
        return None
