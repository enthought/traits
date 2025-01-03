# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from typing import Any, List, Optional, Tuple, Type, Union

import numpy as np

from .trait_type import _TraitType

# Things that are allowed as individual shape elements in the 'shape'
# tuple or list.
_ShapeElement = Union[None, int, Tuple[int, Union[None, int]]]

# Type for the shape parameter.
_Shape = Union[Tuple[_ShapeElement, ...], List[_ShapeElement]]

# The "Array" trait type is not as permissive as NumPy's asarray: it
# accepts only NumPy arrays, lists and tuples.
_ArrayLike = Union[List[Any], Tuple[Any, ...], np.ndarray[Any, Any]]

# Synonym for the "stores" type of the trait.
_Array = np.ndarray[Any, Any]

# Things that are accepted as dtypes. This doesn't attempt to cover
# all legal possibilities - only those that are common.
_DTypeLike = Union[np.dtype[Any], Type[Any], str]

class Array(_TraitType[_ArrayLike, _Array]):
    def __init__(
        self,
        dtype: Optional[_DTypeLike] = ...,
        shape: Optional[_Shape] = ...,
        value: Optional[_ArrayLike] = ...,
        *,
        casting: str = ...,
        **metadata: Any,
    ) -> None: ...

class ArrayOrNone(
    _TraitType[Optional[_ArrayLike], Optional[_Array]]
):
    def __init__(
        self,
        dtype: Optional[_DTypeLike] = ...,
        shape: Optional[_Shape] = ...,
        value: Optional[_ArrayLike] = ...,
        *,
        casting: str = ...,
        **metadata: Any,
    ) -> None: ...

class CArray(_TraitType[_ArrayLike, _Array]):
    def __init__(
        self,
        dtype: Optional[_DTypeLike] = ...,
        shape: Optional[_Shape] = ...,
        value: Optional[_ArrayLike] = ...,
        *,
        casting: str = ...,
        **metadata: Any,
    ) -> None: ...
