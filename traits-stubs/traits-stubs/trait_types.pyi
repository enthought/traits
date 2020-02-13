from .constants import DefaultValue as DefaultValue, TraitKind as TraitKind, \
    ValidateTrait as ValidateTrait
from .editor_factories import code_editor as code_editor, \
    date_editor as date_editor, datetime_editor as datetime_editor, \
    html_editor as html_editor, list_editor as list_editor, \
    password_editor as password_editor, shell_editor as shell_editor, \
    time_editor as time_editor
from .trait_base import EnumTypes as EnumTypes, HandleWeakRef as HandleWeakRef, \
    RangeTypes as RangeTypes, SequenceTypes as SequenceTypes, \
    TraitsCache as TraitsCache, TypeTypes as TypeTypes, Undefined as Undefined, \
    class_of as class_of, enum_default as enum_default, \
    get_module_name as get_module_name, safe_contains as safe_contains, \
    strx as strx, xgetattr as xgetattr
from .trait_converters import trait_from as trait_from
from .trait_dict_object import TraitDictEvent as TraitDictEvent, \
    TraitDictObject as TraitDictObject
from .trait_errors import TraitError as TraitError
from .trait_list_object import TraitListEvent as TraitListEvent, \
    TraitListObject as TraitListObject
from .trait_set_object import TraitSetEvent as TraitSetEvent, \
    TraitSetObject as TraitSetObject
from .trait_type import TraitType as TraitType
from .traits import Trait as Trait
from .util.import_symbol import import_symbol as import_symbol

from .trait_type import _TraitType, _CoercingTraitType
from typing import (
    Any as _Any,
    Callable as _CallableType,
    SupportsComplex,
    Dict as _Dict,
    Generic,
    List as _List,
    Optional,
    Sequence as _Sequence,
    Tuple as _Tuple,
    Type as _Type,
    TypeVar,
    Union,
)

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

_Trait = Union[_TraitType[_S, _T], _Type[_TraitType[_S, _T]]]


class Any(TraitType):
    ...


# -----------------Int--------------------
class _BaseInt(_TraitType[_T, int]):
    ...


class BaseInt(_BaseInt[int]):
    ...


class Int(BaseInt):
    default_value: int = ...


class CInt(BaseInt):
    default_value: int = ...


# -----------------Float--------------------
class _BaseFloat(_TraitType[_T, float]):
    ...


class BaseFloat(_BaseFloat[float]):
    ...


class Float(BaseFloat):
    default_value: float = ...


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


# -----------------Complex--------------------
class _BaseComplex(_TraitType[_T, complex]):
    ...


class BaseComplex(_BaseComplex[complex]):
    ...


class Complex(BaseComplex):
    default_value: complex = ...


# -----------------Bytes--------------------
class _BaseBytes(_TraitType[_T, bytes]):
    ...


class BaseBytes(_BaseBytes[bytes]):
    ...


class Bytes(BaseBytes):
    default_value: bytes = ...


# -----------------Bool--------------------
class _BaseBool(_TraitType[_T, bool]):
    ...


class BaseBool(_BaseBool[bool]):
    default_value: bool = ...


class Bool(BaseBool):
    default_value: bool = ...


# -----------------String--------------------

class _String(_TraitType[_T, bool]):
    ...


class String(_String[str]):
    value: str = ...
    minlen: int = ...
    maxlen: int = ...
    regex: str = ...


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


# -----------------Function--------------------

# TODO
class Function(_Any):
    ...


# -----------------Method--------------------

# TODO
class Method(_Any):
    ...


# -----------------Module--------------------

# TODO
class Module(_Any):
    ...


# -----------------Python--------------------
# TODO
class Python(_Any):
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
# TODO
class Constant(_Any):
    ...


# -----------------Delegate--------------------
# TODO
class Delegate(_Any):
    ...


# -----------------DelegatesTo--------------------
# TODO
class DelegaatesTo(Delegate):
    ...


# -----------------PrototypedFrom--------------------
# TODO
class PrototypedFrom(Delegate):
    ...


# -----------------Expression--------------------
# TODO
class Expression(Any):
    ...


# ---------------------PythonValue----------------
# TODO
class PythonValue(Any):
    ...


# ----------------BaseFile---------------------
# TODO
class BaseFile(BaseStr):
    ...


# ----------------File---------------------
# TODO
class File(BaseFile):
    ...


# ----------------BaseDirectory---------------------
# TODO
class BaseDirectory(BaseFile):
    ...


# ----------------Directory---------------------
# TODO
class Directory(BaseDirectory):
    ...


class List(_TraitType[_Sequence[_S], _List[_T]]):
    def __init__(
            self,
            trait: Union[_TraitType[_S, _T], _Type[_TraitType[_S, _T]]],
            value: _Sequence[_S] = [],
            minlen: int = ...,
            maxlen: int = ...,
            items: bool = ...,
            **metadata: _Dict[str, _Any]
    ) -> None:
        ...
