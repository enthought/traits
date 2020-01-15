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

from .constants import (  # noqa: F401
    ComparisonMode,
    NO_COMPARE,
    OBJECT_IDENTITY_COMPARE,
    RICH_COMPARE,
)

from .trait_base import Uninitialized, Undefined, Missing, Self  # noqa: F401

from .trait_errors import (  # noqa: F401
    TraitError,
    TraitNotificationError,
    DelegationError,
)

from .trait_notifiers import (  # noqa: F401
    push_exception_handler,
    pop_exception_handler,
    TraitChangeNotifyWrapper,
)

from .ctrait import CTrait  # noqa: F401
from .trait_factory import TraitFactory  # noqa: F401
from .traits import (  # noqa: F401
    Trait,
    Property,
    Default,
    Color,
    RGBColor,
    Font,
)

from .trait_types import (  # noqa: F401
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

from .trait_types import (  # noqa: F401
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

from .trait_types import (  # noqa: F401
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

from .trait_types import UUID, ValidatedTuple  # noqa: F401

from .has_traits import (  # noqa: F401
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

from .base_trait_handler import BaseTraitHandler  # noqa: F401
from .trait_handler import TraitHandler  # noqa: F401
from .trait_type import TraitType  # noqa: F401
from .trait_handlers import (  # noqa: F401
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


from .trait_dict_object import TraitDictEvent, TraitDictObject  # noqa: F401
from .trait_list_object import TraitListEvent, TraitListObject  # noqa: F401
from .trait_set_object import TraitSetEvent, TraitSetObject  # noqa: F401


from .adaptation.adapter import Adapter  # noqa: F401
from .adaptation.adaptation_error import AdaptationError  # noqa: F401
from .adaptation.adaptation_manager import (  # noqa: F401
    adapt,
    register_factory,
    register_provides,
)

from .trait_numeric import Array, ArrayOrNone, CArray  # noqa: F401

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
