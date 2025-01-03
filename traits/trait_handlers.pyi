# (C) Copyright 2020-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from typing import (
    Any as _Any,
    Callable as _CallableType,
    Dict as _Dict,
    Type as _Type,
    Union as _Union,
)
from .trait_handler import TraitHandler


class TraitCoerceType(TraitHandler):
    def __init__(self,
                 atype: _Union[_Type, str] = ...,
                 ) -> None:
        ...


class TraitCastType(TraitCoerceType):
    ...


class TraitInstance(TraitHandler):
    def __init__(self,
                 aclass: _Union[_Type, str] = ...,
                 allow_none: bool = ...,
                 module: str = ...,
                 ) -> None:
        ...


class TraitFunction(TraitHandler):
    def __init__(self,
                 afunc: _CallableType = ...) -> None:
        ...


class TraitEnum(TraitHandler):
    def __init__(self,
                 afunc: _CallableType = ...) -> None:
        ...


class TraitMap(TraitHandler):
    def __init__(self,
                 map: _Dict = ...) -> None:
        ...


class TraitCompound(TraitHandler):
    def __init__(self,
                 *handlers: _Any) -> None:
        ...
