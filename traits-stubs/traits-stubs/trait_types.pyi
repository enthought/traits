from typing import (
    Any as _Any,
    Callable as _CallableType,
    Dict as _Dict,
    List as _List,
    Optional,
    Sequence as _Sequence,
    Set as _Set,
    Type as _Type,
    TypeVar,
    Union as _Union,
)
from uuid import UUID as _UUIDType

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


class Str(BaseStr):
    default_value: str = ...


# -----------------Title--------------------

class Title(Str):
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

class BaseCInt(BaseInt):
    ...


class CInt(BaseCInt):
    ...


# -----------------BaseCFloat--------------------

class BaseCFloat(BaseFloat):
    ...


class CFloat(BaseCFloat):
    ...


# -----------------BaseCComplex--------------------

class BaseCComplex(BaseComplex):
    ...


class CComplex(BaseCComplex):
    ...


# -----------------BaseCStr--------------------

class BaseCStr(BaseStr):
    ...


class CStr(BaseCStr):
    ...


# -----------------BaseCBytes--------------------

class BaseCBytes(BaseBytes):
    ...


class CBytes(BaseCBytes):
    ...


# -----------------BaseCBool--------------------

class BaseCBool(BaseBool):
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

class _BaseCallable(_TraitType[_T, _CallableType[..., _Any]]):
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
class DelegaatesTo(Delegate):
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
class _BaseFile(_BaseStr):
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
class _UUID(_TraitType[_T, _UUIDType]):
    ...


class UUID(_UUID[_Union[str, _UUIDType]]):
    ...


class List(_TraitType[_Sequence[_S], _List[_T]]):
    def __init__(
            self,
            trait: _Union[_TraitType[_S, _T], _Type[_TraitType[_S, _T]]],
            value: _Sequence[_S] = [],
            minlen: int = ...,
            maxlen: int = ...,
            items: bool = ...,
            **metadata: _Dict[str, _Any]
    ) -> None:
        ...


class Set(_TraitType[_Sequence[_S], _Set[_T]]):
    def __init__(
            self,
            trait: _Union[_TraitType[_S, _T], _Type[_TraitType[_S, _T]]],
            value: _Sequence[_S] = ...,
            items: bool = ...,
            **metadata: _Dict[str, _Any]
    ) -> None:
        ...
