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


class Any(TraitType):
    ...


# -----------------Int--------------------
class _BaseInt(_TraitType[_T, int]):
    ...


class BaseInt(_BaseInt[int]):
    default_value: int = ...


class Int(BaseInt):
    default_value: int = ...


# -----------------Float--------------------
class _BaseFloat(_TraitType[_T, float]):
    ...


class BaseFloat(_BaseFloat[float]):
    default_value: float = ...


class Float(BaseFloat):
    default_value: float = ...


# -----------------Complex--------------------
class _BaseComplex(_TraitType[_T, complex]):
    ...


class BaseComplex(_BaseComplex[complex]):
    default_value: complex = ...


class Complex(BaseComplex):
    default_value: complex = ...


# -----------------Str--------------------

class _BaseStr(_TraitType[_T, str]):
    default_value: str = ...


class BaseStr(_BaseStr[str]):
    default_value: str = ...


class _Str(BaseStr):
    default_value: str = ...


class Str(_Str):
    ...


# -----------------Title--------------------

class Title(_Str):
    default_value: str = ...


# -----------------Bytes--------------------
class _BaseBytes(_TraitType[_T, bytes]):
    ...


class BaseBytes(_BaseBytes[bytes]):
    default_value: bytes = ...


class Bytes(BaseBytes):
    default_value: bytes = ...


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


class _CStr(_BaseCStr):
    ...


class CStr(_CStr):
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
    def __init__(self, value: str = ..., minlen: int = ..., maxlen: int = ...,
                 regex: str = ...):
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


# -----------------Type--------------------

# TODO
class BaseType(_Any):
    ...


class Type(BaseType):
    ...


# -----------------This--------------------
class This(BaseType):
    ...


# -----------------self--------------------
class self(This):
    ...


# -----------------Function--------------------
class Function(_TraitType):
    ...


# -----------------Method--------------------

class Method(_TraitType):
    ...


# -----------------Module--------------------

class Module(_TraitType):
    ...


# -----------------Python--------------------
class Python(_TraitType):
    ...


# -----------------ReadOnly--------------------
# TODO
class ReadOnly(_Any):
    ...


# -----------------Disallow--------------------
# TODO
class Disallow(_Any):
    ...


# -----------------Constant--------------------
class Constant(_TraitType):
    ...


# -----------------Delegate--------------------
class Delegate(_TraitType):
    ...


# -----------------DelegatesTo--------------------
class DelegatesTo(Delegate):
    ...


# -----------------PrototypedFrom--------------------
class PrototypedFrom(Delegate):
    ...


# -----------------Expression--------------------
class Expression(_TraitType):
    ...


# ---------------------PythonValue----------------
class PythonValue(_Any):
    ...


# ----------------BaseFile---------------------
class _BaseFile(_TraitType[_Union[str, _PurePath], str]):
    ...


class BaseFile(_BaseFile):
    ...


# ----------------File---------------------
class _File(_BaseFile):
    ...


class File(_File):
    ...


# ----------------BaseDirectory---------------------
class _BaseDirectory(_BaseStr):
    ...


class BaseDirectory(_BaseDirectory):
    ...


# ----------------Directory---------------------
class Directory(_BaseDirectory):
    ...


# ----------------BaseRange---------------------
class _BaseRange(_TraitType):
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


class BaseRange(_BaseRange):
    ...


# ----------------Range---------------------
class _Range(_BaseRange):
    ...


class Range(_Range):
    ...


# ----------------BaseEnum---------------------
class _BaseEnum(_TraitType[_T, _Any]):
    ...


class BaseEnum(_BaseEnum):
    ...


class Enum(_BaseEnum):
    ...


# ----------------Tuple---------------------
class _BaseTuple(_TraitType[_T, tuple]):
    ...


class BaseTuple(_BaseTuple[tuple]):
    ...


class Tuple(BaseTuple):
    ...


# ----------------UUID---------------------
class UUID(_TraitType[_Union[str, _UUID], _UUID]):
    ...


# ----------------List---------------------

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


# ----------------Set---------------------
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


class CSet(_Set[_S, _T]):
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


class Dict(_Dict):
    ...


class _BaseClass(_TraitType[Optional[_Type, str], Optional[_Type, str]]):
    ...


class BaseClass(_BaseClass):
    ...


class _BaseInstance(_BaseClass):
    ...


class BaseInstance(_BaseInstance):
    ...


class _Instance(_BaseInstance):
    ...


class Instance(_Instance):
    ...


class _Supports(_Instance):
    ...


class Supports(_Supports):
    ...


class AdaptsTo(_Supports):
    ...


# class Type(_BaseClass):
#     ...


class _Event(_TraitType[_Any, _Any]):
    ...


class Event(_Event):
    ...


class _Button(_Event):
    ...


class Button(_Button):
    ...


class ToolbarButton(_Button):
    ...


class Either(_TraitType[_Any, _Any]):
    ...


class NoneTrait(_TraitType[None, None]):
    ...


class Union(_TraitType[_Any, _Any]):
    ...


class Symbol(_TraitType[_Any, _Any]):
    ...


class WeakRef(_Instance):
    ...


class Date(_BaseInstance):
    ...


class Datetime(_BaseInstance):
    ...


class Time(_BaseInstance):
    ...


class AdaptedTo(Supports):
    ...


class BaseUnicode(_BaseStr):
    ...


class Unicode(_Str):
    ...


class BaseCUnicode(_BaseStr):
    ...


class CUnicode(_CStr):
    ...


class BaseCLong(_BaseCInt):
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
