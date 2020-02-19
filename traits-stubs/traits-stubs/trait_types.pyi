import datetime
from pathlib import PurePath as _PurePath
from typing import (
    Any as _Any,
    Callable as _CallableType,
    Dict as _DictType,
    List as _ListType,
    Optional,
    Sequence as _Sequence,
    Set as _SetType,
    Type as _Type,
    TypeVar,
    Union as _Union,
)

from uuid import UUID as _UUID

from .trait_type import TraitType as TraitType
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


class Any(_TraitType[_Any, _Any]):
    ...


# -----------------Int--------------------
class _BaseInt(_TraitType[_T, int]):
    ...


class BaseInt(_BaseInt[int]):
    ...


class Int(BaseInt):
    ...


# -----------------Float--------------------
class _BaseFloat(_TraitType[_T, float]):
    ...


class BaseFloat(_BaseFloat[float]):
    ...


class Float(BaseFloat):
    ...


# -----------------Complex--------------------
class _BaseComplex(_TraitType[_T, complex]):
    ...


class BaseComplex(_BaseComplex[complex]):
    ...


class Complex(BaseComplex):
    ...


# -----------------Str--------------------

class _BaseStr(_TraitType[_T, str]):
    ...


class BaseStr(_BaseStr[str]):
    ...


class Str(BaseStr):
    ...


# -----------------Title--------------------

class Title(Str):
    ...


# -----------------Bytes--------------------
class _BaseBytes(_TraitType[_T, bytes]):
    ...


class BaseBytes(_BaseBytes[bytes]):
    ...


class Bytes(BaseBytes):
    ...


# -----------------Bool--------------------
class _BaseBool(_TraitType[_T, bool]):
    ...


class BaseBool(_BaseBool[bool]):
    default_value: bool = ...


class Bool(BaseBool):
    default_value: bool = ...


# -----------------BaseCInt--------------------

class _BaseCInt(_BaseInt[_Any]):
    default_value: _Any = ...


class BaseCInt(_BaseCInt):
    ...


class CInt(_BaseCInt):
    ...


# -----------------BaseCFloat--------------------

class BaseCFloat(_BaseFloat[_Any]):
    ...


class CFloat(BaseCFloat):
    ...


# -----------------BaseCComplex--------------------

class BaseCComplex(_BaseComplex[_Any]):
    ...


class CComplex(BaseCComplex):
    ...


# -----------------BaseCStr--------------------

class _BaseCStr(_BaseStr[_Any]):
    ...


class BaseCStr(_BaseCStr):
    ...


class CStr(_BaseCStr):
    ...


# -----------------BaseCBytes--------------------

class BaseCBytes(_BaseBytes[_Any]):
    ...


class CBytes(BaseCBytes):
    ...


# -----------------BaseCBool--------------------

class BaseCBool(_BaseBool[_Any]):
    ...


class CBool(BaseCBool):
    ...


# -----------------String--------------------

class _String(_TraitType[_T, str]):
    ...


class String(_String[str]):
    def __init__(self,
                 value: str = ...,
                 minlen: int = ...,
                 maxlen: int = ...,
                 regex: str = ...,
                 **metadata: _DictType[str, _Any]
                 ):
        ...


# -----------------Regex--------------------

class Regex(String):
    ...


# -----------------Code--------------------

class Code(String):
    ...


# -----------------HTML--------------------

class HTML(String):
    ...


# -----------------Password--------------------

class Password(String):
    ...


# -----------------Callable--------------------


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
    def __init__(self,
                 deligate: str = ...,
                 prefix: str = ...,
                 modify: bool = ...,
                 listenable: bool = ...,
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
    def __init__(self,
                 value: str = ...,
                 filter: str = ...,
                 auto_set: bool = ...,
                 entries: int = ...,
                 exists: bool = ...,
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
            **metadata: _DictType[str, _Any]
    ) -> None:
        ...


class BaseRange(_BaseRange[_Union[int, float]]):
    ...


class Range(BaseRange):
    ...


# ----------------BaseEnum---------------------
class _BaseEnum(_TraitType[_T, _Any]):
    ...


class BaseEnum(_BaseEnum[_Any]):
    ...


class Enum(BaseEnum):
    ...


class _BaseTuple(_TraitType[_T, tuple]):
    ...


class BaseTuple(_BaseTuple[tuple]):
    ...


class Tuple(BaseTuple):
    ...


class ValidatedTuple(BaseTuple):
    def __init__(self,
                 types: _Any = ...,
                 fvalidate: _OptionalCallable = ...,
                 fvalidate_info: Optional[str] = ...,
                 **metadata: _DictType[str, _Any]
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
            **metadata: _DictType[str, _Any]
    ) -> None:
        ...


class List(_List[_S, _T]):
    ...


class PrefixList(BaseStr):
    ...


class _Set(_TraitType[_SetType[_S], _SetType[_T]]):
    def __init__(
            self,
            trait: _Union[_TraitType[_S, _T], _Type[_TraitType[_S, _T]]] = ...,
            value: _Sequence[_S] = ...,
            items: bool = ...,
            **metadata: _DictType[str, _Any]
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
            **metadata: _DictType[str, _Any]
    ) -> None:
        ...


class Dict(_Dict[_S, _T]):
    ...


class BaseClass(_TraitType[Optional[_Type, str], Optional[_Type, str]]):
    ...


class BaseInstance(BaseClass):
    ...


class Instance(BaseInstance):
    ...


class Supports(Instance):
    ...


class AdaptsTo(Supports):
    ...


class Type(BaseClass):
    ...


class Subclass(Type):
    ...


class Event(_TraitType[_Any, _Any]):
    ...


class Button(Event):
    def __init__(self,
                 label: str = ...,
                 image: _Any = ...,
                 style: str = ...,
                 values_trait: str = ...,
                 orientation: str = ...,
                 width_padding: int = ...,
                 height_padding: int = ...,
                 view: Optional[_Any] = ...,
                 **metadata: _DictType[str, _Any]
                 ):
        ...


class ToolbarButton(Button):
    ...


class Either(_TraitType[_Any, _Any]):
    ...


class NoneTrait(_TraitType[None, None]):
    ...


class Union(_TraitType[_Any, _Any]):
    ...


class UUID(_TraitType[_Union[str, _UUID], _UUID]):
    ...


class Symbol(_TraitType[_Any, _Any]):
    ...


class WeakRef(Instance):
    ...


class Date(BaseInstance):
    ...


class Datetime(BaseInstance):
    ...


class Time(BaseInstance):
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


class undefined(Any):
    ...


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


class DictStrAny(_Dict[str, _Any]):
    ...


class DictStrInt(_Dict[str, int]):
    ...


class DictStrFloat(_Dict[str, float]):
    ...


class DictStrBool(_Dict[str, bool]):
    ...


class DictStrList(_Dict[str, list]):
    ...
