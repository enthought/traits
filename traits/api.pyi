# (C) Copyright 2020-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from .constants import (
    ComparisonMode as ComparisonMode,
    DefaultValue as DefaultValue,
    TraitKind as TraitKind,
    ValidateTrait as ValidateTrait,
    NO_COMPARE as NO_COMPARE,
    OBJECT_IDENTITY_COMPARE as OBJECT_IDENTITY_COMPARE,
    RICH_COMPARE as RICH_COMPARE,
)

from .trait_errors import (
    TraitError as TraitError,
    TraitNotificationError as TraitNotificationError,
    DelegationError as DelegationError,
)

from .traits import (
    Default as Default,
    Property as Property,
    Trait as Trait
)

from .ctrait import CTrait as CTrait

from .has_traits import (
    ABCHasStrictTraits as ABCHasStrictTraits,
    ABCHasTraits as ABCHasTraits,
    ABCMetaHasTraits as ABCMetaHasTraits,
    AbstractViewElement as AbstractViewElement,
    HasTraits as HasTraits,
    HasStrictTraits as HasStrictTraits,
    HasPrivateTraits as HasPrivateTraits,
    HasRequiredTraits as HasRequiredTraits,
    Interface as Interface,
    MetaHasTraits as MetaHasTraits,
    Vetoable as Vetoable,
    VetoableEvent as VetoableEvent,
    observe as observe,
    on_trait_change as on_trait_change,
    cached_property as cached_property,
    property_depends_on as property_depends_on,
    provides as provides,
    isinterface as isinterface,
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
    false as false,
    true as true,
    undefined as undefined,
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

from .base_trait_handler import BaseTraitHandler as BaseTraitHandler
from .trait_handler import TraitHandler as TraitHandler
from .trait_type import TraitType as TraitType
from .trait_handlers import (
    TraitCoerceType as TraitCoerceType,
    TraitCastType as TraitCastType,
    TraitInstance as TraitInstance,
    TraitFunction as TraitFunction,
    TraitEnum as TraitEnum,
    TraitMap as TraitMap,
    TraitCompound as TraitCompound,
)

from .trait_numeric import (
    Array as Array,
    ArrayOrNone as ArrayOrNone,
    CArray as CArray,
)

from .trait_notifiers import (
    get_ui_handler as get_ui_handler,
    set_ui_handler as set_ui_handler,
)
