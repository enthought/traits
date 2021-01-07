# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Pseudo-package for all of the core symbols from Traits and TraitsUI.
Use this module for importing Traits names into your namespace. For example::

    from traits.api import HasTraits
"""

from .constants import (
    ComparisonMode,
    DefaultValue,
    TraitKind,
    ValidateTrait,
    NO_COMPARE,
    OBJECT_IDENTITY_COMPARE,
    RICH_COMPARE,
)

from .trait_base import Uninitialized, Undefined, Missing, Self
from .trait_converters import as_ctrait

from .trait_errors import (
    TraitError,
    TraitNotificationError,
    DelegationError,
)

from .trait_notifiers import (
    push_exception_handler,
    pop_exception_handler,
    TraitChangeNotifyWrapper,
)

from .ctrait import CTrait
from .trait_factory import TraitFactory
from .traits import (
    Trait,
    Property,
    Default,
    Color,
    RGBColor,
    Font,
)

from .trait_types import (
    Any,
    Int,
    Float,
    Complex,
    Str,
    Title,
    Bytes,
    Bool,
    CInt,
    CFloat,
    CComplex,
    CStr,
    CBytes,
    CBool,
    String,
    Regex,
    Code,
    HTML,
    Password,
    Callable,
    This,
    self,
    Function,
    Method,
    Module,
    Python,
    ReadOnly,
    Disallow,
    Constant,
    Delegate,
    DelegatesTo,
    PrototypedFrom,
    Expression,
    PythonValue,
    File,
    Directory,
    Range,
    Enum,
    Tuple,
    List,
    CList,
    PrefixList,
    Set,
    CSet,
    Dict,
    Map,
    PrefixMap,
    Instance,
    AdaptedTo,
    AdaptsTo,
    Event,
    Button,
    ToolbarButton,
    Either,
    Union,
    Type,
    Subclass,
    Symbol,
    WeakRef,
    Date,
    Datetime,
    Time,
    Supports,
)

# Deprecated TraitType subclasses and instances.

from .trait_types import (
    BaseUnicode,
    Unicode,
    BaseCUnicode,
    CUnicode,
    BaseLong,
    Long,
    BaseCLong,
    CLong,
    false,
    true,
    undefined,
    ListInt,
    ListFloat,
    ListStr,
    ListUnicode,
    ListComplex,
    ListBool,
    ListFunction,
    ListMethod,
    ListThis,
    DictStrAny,
    DictStrStr,
    DictStrInt,
    DictStrFloat,
    DictStrBool,
    DictStrList,
)

from .trait_types import (
    BaseCallable,
    BaseInt,
    BaseFloat,
    BaseComplex,
    BaseStr,
    BaseBytes,
    BaseBool,
    BaseCInt,
    BaseCFloat,
    BaseCComplex,
    BaseCStr,
    BaseCBool,
    BaseFile,
    BaseDirectory,
    BaseRange,
    BaseEnum,
    BaseTuple,
    BaseInstance,
)

from .trait_types import UUID, ValidatedTuple

from .has_traits import (
    ABCHasStrictTraits,
    ABCHasTraits,
    ABCMetaHasTraits,
    AbstractViewElement,
    HasTraits,
    HasStrictTraits,
    HasPrivateTraits,
    HasRequiredTraits,
    Interface,
    SingletonHasTraits,
    SingletonHasStrictTraits,
    SingletonHasPrivateTraits,
    MetaHasTraits,
    Vetoable,
    VetoableEvent,
    observe,
    on_trait_change,
    cached_property,
    property_depends_on,
    provides,
    isinterface,
)

from .base_trait_handler import BaseTraitHandler
from .trait_handler import TraitHandler
from .trait_type import TraitType, NoDefaultSpecified
from .trait_handlers import (
    TraitCoerceType,
    TraitCastType,
    TraitInstance,
    TraitFunction,
    TraitEnum,
    TraitPrefixList,
    TraitMap,
    TraitPrefixMap,
    TraitCompound,
    TraitList,
    TraitDict,
    TraitTuple,
)


from .trait_dict_object import TraitDictEvent, TraitDictObject
from .trait_list_object import TraitListEvent, TraitListObject
from .trait_set_object import TraitSetEvent, TraitSetObject


from .adaptation.adapter import Adapter
from .adaptation.adaptation_error import AdaptationError
from .adaptation.adaptation_manager import (
    adapt,
    register_factory,
    register_provides,
)

from .trait_numeric import Array, ArrayOrNone, CArray
