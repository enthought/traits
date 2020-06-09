# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from .trait_type import TraitType as TraitType
from .traits import (
    Color as Color,
    Default as Default,
    Font as Font,
    Property as Property,
    RGBColor as RGBColor,
    Trait as Trait
)

from .has_traits import (
    HasTraits as HasTraits,
    observe as observe,
)

from .trait_types import (
    Any as Any,
    Int as Int,
    Float as Float,
    Complex as Complex,
    Str as Str,
    Title as Title,
    Bytes as Bytes,
    Bool as Bool,
    CInt as CInt,
    CFloat as CFloat,
    CComplex as CComplex,
    CStr as CStr,
    CBytes as CBytes,
    CBool as CBool,
    String as String,
    Regex as Regex,
    Code as Code,
    HTML as HTML,
    Password as Password,
    Callable as Callable,
    This as This,
    self as self,
    Function as Function,
    Method as Method,
    Module as Module,
    Python as Python,
    ReadOnly as ReadOnly,
    Disallow as Disallow,
    Constant as Constant,
    Delegate as Delegate,
    DelegatesTo as DelegatesTo,
    PrototypedFrom as PrototypedFrom,
    Expression as Expression,
    PythonValue as PythonValue,
    File as File,
    Directory as Directory,
    Range as Range,
    Enum as Enum,
    Tuple as Tuple,
    List as List,
    CList as CList,
    PrefixList as PrefixList,
    Set as Set,
    CSet as CSet,
    Dict as Dict,
    Map as Map,
    PrefixMap as PrefixMap,
    Instance as Instance,
    AdaptedTo as AdaptedTo,
    AdaptsTo as AdaptsTo,
    Event as Event,
    Button as Button,
    ToolbarButton as ToolbarButton,
    Either as Either,
    Union as Union,
    Type as Type,
    Subclass as Subclass,
    Symbol as Symbol,
    WeakRef as WeakRef,
    Date as Date,
    Datetime as Datetime,
    Time as Time,
    Supports as Supports,
)

# Deprecated TraitType subclasses and instances.

from .trait_types import (
    BaseUnicode as BaseUnicode,
    Unicode as Unicode,
    BaseCUnicode as BaseCUnicode,
    CUnicode as CUnicode,
    BaseLong as BaseLong,
    Long as Long,
    BaseCLong as BaseCLong,
    CLong as CLong,
    false as false,
    true as true,
    undefined as undefined,
    ListInt as ListInt,
    ListFloat as ListFloat,
    ListStr as ListStr,
    ListUnicode as ListUnicode,
    ListComplex as ListComplex,
    ListBool as ListBool,
    ListFunction as ListFunction,
    ListMethod as ListMethod,
    ListThis as ListThis,
    DictStrAny as DictStrAny,
    DictStrStr as DictStrStr,
    DictStrInt as DictStrInt,
    DictStrFloat as DictStrFloat,
    DictStrBool as DictStrBool,
    DictStrList as DictStrList,
)

from .trait_types import (
    BaseCallable as BaseCallable,
    BaseInt as BaseInt,
    BaseFloat as BaseFloat,
    BaseComplex as BaseComplex,
    BaseStr as BaseStr,
    BaseBytes as BaseBytes,
    BaseBool as BaseBool,
    BaseCInt as BaseCInt,
    BaseCFloat as BaseCFloat,
    BaseCComplex as BaseCComplex,
    BaseCStr as BaseCStr,
    BaseCBool as BaseCBool,
    BaseFile as BaseFile,
    BaseDirectory as BaseDirectory,
    BaseRange as BaseRange,
    BaseEnum as BaseEnum,
    BaseTuple as BaseTuple,
    BaseInstance as BaseInstance,
)

from .trait_types import (
    UUID as UUID,
    ValidatedTuple as ValidatedTuple
)

from .trait_handlers import (
    TraitCoerceType as TraitCoerceType,
    TraitCastType as TraitCastType,
    TraitInstance as TraitInstance,
    TraitFunction as TraitFunction,
    TraitEnum as TraitEnum,
    TraitPrefixList as TraitPrefixList,
    TraitMap as TraitMap,
    TraitPrefixMap as TraitPrefixMap,
    TraitCompound as TraitCompound,
    TraitList as TraitList,
    TraitDict as TraitDict,
    TraitTuple as TraitTuple,
)
