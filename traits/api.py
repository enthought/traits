# ------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   12/06/2005
#
# ------------------------------------------------------------------------------

""" Pseudo-package for all of the core symbols from Traits and TraitsUI.
Use this module for importing Traits names into your namespace. For example::

    from traits.api import HasTraits
"""

from .constants import (
    ComparisonMode,
    NO_COMPARE,
    OBJECT_IDENTITY_COMPARE,
    RICH_COMPARE,
)

from .trait_base import Uninitialized, Undefined, Missing, Self

from .trait_errors import TraitError, TraitNotificationError, DelegationError

from .trait_notifiers import (
    push_exception_handler,
    pop_exception_handler,
    TraitChangeNotifyWrapper,
)

from .traits import (
    CTrait,
    Trait,
    Property,
    TraitFactory,
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
    Set,
    CSet,
    Dict,
    Instance,
    AdaptedTo,
    AdaptsTo,
    Event,
    Button,
    ToolbarButton,
    Either,
    Type,
    Symbol,
    WeakRef,
    Date,
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
    traits_super,
    on_trait_change,
    cached_property,
    property_depends_on,
    provides,
    isinterface,
)

from .trait_handlers import (
    BaseTraitHandler,
    TraitType,
    TraitHandler,
    TraitCoerceType,
    TraitCastType,
    TraitInstance,
    ThisClass,
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

try:
    # -------------------------------------------------------------------------------
    #  Patch the main traits module with the correct definition for the
    #  ViewElement class:
    # -------------------------------------------------------------------------------

    from traitsui.view_element import ViewElement

    if not isinstance(ViewElement, AbstractViewElement):
        AbstractViewElement.register(ViewElement)
except ImportError:
    pass
