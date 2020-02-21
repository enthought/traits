# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import datetime
from pathlib import PurePath as _PurePath
from typing import (
    Any as _Any,
    Callable as _CallableType,
    Dict as _DictType,
    Generic as Generic,
    List as _ListType,
    Optional,
    Sequence as _Sequence,
    Set as _SetType,
    Type as _Type,
    TypeVar,
    Union as _Union,
)
from uuid import UUID as _UUID

from .trait_type import _TraitType

MutableTypes: _Any
SetTypes: _Any
int_fast_validate: _Any
float_fast_validate: _Any
complex_fast_validate: _Any
bool_fast_validate: _Any


def default_text_editor(trait: _Any, type: Optional[_Any] = ...):
    ...


_T = TypeVar("_T")
_S = TypeVar("_S")

_Trait = _Union[_TraitType[_S, _T], _Type[_TraitType[_S, _T]]]

Any = _Any


class _BaseInt(_TraitType[_T, int]):
    ...


class BaseInt(_BaseInt[int]):
    ...


class Int(BaseInt):
    ...


class _BaseFloat(_TraitType[_T, float]):
    ...


class BaseFloat(_BaseFloat[float]):
    ...


class Float(BaseFloat):
    ...


class _BaseComplex(_TraitType[_T, complex]):
    ...


class BaseComplex(_BaseComplex[complex]):
    ...


class Complex(BaseComplex):
    ...


class _BaseStr(_TraitType[_T, str]):
    ...


class BaseStr(_BaseStr[str]):
    ...


class Str(BaseStr):
    ...


class Title(Str):
    ...


class _BaseBytes(_TraitType[_T, bytes]):
    ...


class BaseBytes(_BaseBytes[bytes]):
    ...


class Bytes(BaseBytes):
    ...


class _BaseBool(_TraitType[_T, bool]):
    ...


class BaseBool(_BaseBool[bool]):
    default_value: bool = ...


class Bool(BaseBool):
    default_value: bool = ...


class _BaseCInt(_BaseInt[_Any]):
    default_value: _Any = ...


class BaseCInt(_BaseCInt):
    ...


class CInt(_BaseCInt):
    ...


class BaseCFloat(_BaseFloat[_Any]):
    ...


class CFloat(BaseCFloat):
    ...


class BaseCComplex(_BaseComplex[_Any]):
    ...


class CComplex(BaseCComplex):
    ...


class _BaseCStr(_BaseStr[_Any]):
    ...


class BaseCStr(_BaseCStr):
    ...


class CStr(_BaseCStr):
    ...


class BaseCBytes(_BaseBytes[_Any]):
    ...


class CBytes(BaseCBytes):
    ...


class BaseCBool(_BaseBool[_Any]):
    ...


class CBool(BaseCBool):
    ...


class _String(_TraitType[_T, str]):
    ...


class String(_String[str]):
    def __init__(
            self,
            value: str = ...,
            minlen: int = ...,
            maxlen: int = ...,
            regex: str = ...,
            **metadata: _Any
    ):
        ...


class Regex(String):
    ...


class Code(String):
    ...


class HTML(String):
    ...


class Password(String):
    ...


_OptionalCallable = Optional[_CallableType[..., _Any]]


class _BaseCallable(_TraitType[_OptionalCallable, _OptionalCallable]):
    ...


class BaseCallable(_BaseCallable[_CallableType[..., _Any]]):
    ...


class Callable(BaseCallable):
    ...


class BaseType(_TraitType[_Any, _Any]):
    ...


class This(BaseType):
    ...


class self(This):
    ...


class Function(_TraitType[_OptionalCallable, _OptionalCallable]):
    ...


class Method(_TraitType[_OptionalCallable, _OptionalCallable]):
    ...


class Module(_TraitType[_Any, _Any]):
    ...


class Python(_TraitType[_Any, _Any]):
    ...


class ReadOnly(_TraitType[_Any, _Any]):
    ...


class Disallow(_TraitType[_Any, _Any]):
    ...


class Constant(_TraitType[_Any, _Any]):
    ...


class Delegate(_TraitType[_Any, _Any]):
    def __init__(
            self,
            deligate: str = ...,
            prefix: str = ...,
            modify: bool = ...,
            listenable: bool = ...,
            **metadata: _Any
    ):
        ...


class DelegatesTo(Delegate):
    ...


class PrototypedFrom(Delegate):
    ...


class Expression(_TraitType[_Any, _Any]):
    ...


class PythonValue(Any):
    ...


class BaseFile(_TraitType[_Union[str, _PurePath], str]):
    def __init__(
            self,
            value: str = ...,
            filter: str = ...,
            auto_set: bool = ...,
            entries: int = ...,
            exists: bool = ...,
            **metadata: _Any
    ):
        ...


class File(BaseFile):
    ...


class BaseDirectory(_BaseStr):
    ...


class Directory(BaseDirectory):
    ...


# ----------------BaseRange---------------------
class _BaseRange(_TraitType[_T, _Union[int, float]]):
    def __init__(
            self,
            low: _Union[int, float, str] = ...,
            high: _Union[int, float, str] = ...,
            value: _Union[int, float, str] = ...,
            exclude_low: bool = ...,
            exclude_high: bool = ...,
            **metadata: _Any
    ) -> None:
        ...


class BaseRange(_BaseRange[_Union[int, float]]):
    ...


class Range(BaseRange):
    ...


class _BaseEnum(_TraitType[_T, _Any]):
    def __init__(self,
                 *args: _Any,
                 **metadata: _Any,
                 ) -> None:
        ...


class BaseEnum(_BaseEnum[_Any]):
    ...


class Enum(BaseEnum):
    ...


class _BaseTuple(_TraitType[_T, tuple]):
    def __init__(
            self,
            *types: _Any,
            **metadata: _Any,
    ) -> None:
        ...


class BaseTuple(_BaseTuple[tuple]):
    ...


class Tuple(BaseTuple):
    ...


class ValidatedTuple(BaseTuple):
    def __init__(
            self,
            *types: _Any,
            fvalidate: _OptionalCallable = ...,
            fvalidate_info: Optional[str] = ...,
            **metadata: _Any
    ):
        ...


class _List(_TraitType[_Sequence[_S], _ListType[_T]]):
    def __init__(
            self,
            trait: _Union[_TraitType[_S, _T], _Type[_TraitType[_S, _T]]] = ...,
            value: _Sequence[_S] = [],
            minlen: int = ...,
            maxlen: int = ...,
            items: bool = ...,
            **metadata: _Any
    ) -> None:
        ...


class List(_List[_S, _T]):
    ...


class CList(_List[_S, _T]):
    ...


class PrefixList(BaseStr):
    def __init__(self,
                 *values: _Union[str, _Sequence[str]],
                 **metadata: _Any,
                 ) -> None:
        ...


class _Set(_TraitType[_SetType[_S], _SetType[_T]]):
    def __init__(
            self,
            trait: _Union[_TraitType[_S, _T], _Type[_TraitType[_S, _T]]] = ...,
            value: _Sequence[_S] = ...,
            items: bool = ...,
            **metadata: _Any
    ) -> None:
        ...


class Set(_Set[_S, _T]):
    ...


class CSet(Set):
    ...


class _Dict(_TraitType[_DictType[_S, _T], _DictType[_S, _T]]):
    def __init__(
            self,
            key_trait: _Union[
                _TraitType[_S, _T], _Type[_TraitType[_S, _T]]] = ...,
            value_trait: _Union[
                _TraitType[_S, _T], _Type[_TraitType[_S, _T]]] = ...,
            value: dict = ...,
            items: bool = ...,
            **metadata: _Any
    ) -> None:
        ...


class Dict(_Dict[_S, _T]):
    ...


class _BaseClass(_TraitType[_Union[_T, str, None], _Union[_T, str, None]]):
    ...


class BaseClass(_BaseClass[_Type]):
    ...


class _BaseInstance(_BaseClass[_T]):
    def __init__(
            self,
            klass: _T = ...,
            factory: _OptionalCallable = ...,
            args: tuple = ...,
            kw: _Dict[_Any, _Any] = ...,
            allow_none: bool = ...,
            adapt: str = ...,
    ) -> None:
        ...


class BaseInstance(_BaseInstance[_Type]):
    ...


class Instance(BaseInstance[_Any]):
    ...


class Supports(Instance):
    ...


class AdaptsTo(Supports):
    ...


class Type(BaseClass):
    def __init__(self,
                 value: Optional[_Type] = ...,
                 klass: Optional[_Union[_Type, str]] = ...,
                 allow_none: bool = ...,
                 **metadata: _Any
                 ) -> None:
        ...


class Subclass(Type):
    ...


class Event(_TraitType[_Any, _Any]):
    ...


class Button(Event):
    def __init__(
            self,
            label: str = ...,
            image: _Any = ...,
            style: str = ...,
            values_trait: str = ...,
            orientation: str = ...,
            width_padding: int = ...,
            height_padding: int = ...,
            view: Optional[_Any] = ...,
            **metadata: _Any
    ):
        ...


class ToolbarButton(Button):
    def __init__(
            self,
            label: str = ...,
            image: _Any = ...,
            style: str = ...,
            orientation: str = ...,
            width_padding: int = ...,
            height_padding: int = ...,
            **metadata: _Any
    ) -> None:
        ...


class Either(_TraitType[_Any, _Any]):
    def __init__(self,
                 *traits: _Any,
                 **metadata: _Any
                 ) -> None:
        ...


class NoneTrait(_TraitType[None, None]):
    ...


class Union(_TraitType[_Any, _Any]):
    def __init__(self,
                 *traits: _Any,
                 **metadata: _Any
                 ) -> None:
        ...


class Symbol(_TraitType[_Any, _Any]):
    ...


class UUID(_TraitType[_Union[str, _UUID], _UUID]):
    def __init__(self,
                 can_init: bool = ...,
                 **metadata: _Any
                 ) -> None:
        ...


class WeakRef(Instance):
    def __init__(self,
                 klass: _Any = ...,
                 allow_none: bool = ...,
                 adapt: str = ...,
                 **metadata: _Any
                 ) -> None:
        ...


class Date(_BaseInstance[datetime.date]):
    ...


class Datetime(_BaseInstance[datetime.datetime]):
    ...


class Time(_BaseInstance[datetime.time]):
    ...


class AdaptedTo(Supports):
    ...


class BaseUnicode(BaseStr):
    ...


class Unicode(Str):
    ...


class BaseCUnicode(BaseStr):
    ...


class CUnicode(CStr):
    ...


class BaseLong(BaseInt):
    ...


class Long(Int):
    ...


class BaseCLong(BaseCInt):
    ...


class CLong(CInt):
    ...


class false(Bool):
    ...


class true(Bool):
    ...


undefined = _Any


class ListInt(_List[int, int]):
    ...


class ListFloat(_List[float, float]):
    ...


class _ListStr(_List[str, str]):
    ...


class ListStr(_ListStr):
    ...


class ListUnicode(_ListStr):
    ...


class ListComplex(_List[complex, complex]):
    ...


class ListBool(_List[bool, bool]):
    ...


class ListFunction(_List[_CallableType, _CallableType]):
    ...


class ListMethod(_List[_CallableType, _CallableType]):
    ...


class ListThis(_List[_CallableType, _CallableType]):
    ...


class DictStrAny(_Dict[str, _Any]):
    ...


class DictStrStr(_Dict[str, str]):
    ...


class DictStrInt(_Dict[str, int]):
    ...


class DictStrFloat(_Dict[str, float]):
    ...


class DictStrBool(_Dict[str, bool]):
    ...


class DictStrList(_Dict[str, list]):
    ...
