#------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------

""" Pseudo-package for all of the core symbols from Traits and TraitsUI.
Use this module for importing Traits names into your namespace. For example::

    from enthought.traits.api import HasTraits
"""

from version import __version__

from trait_base \
    import Uninitialized, Undefined, Missing, Self, python_version

from trait_errors \
    import TraitError, TraitNotificationError, DelegationError

from trait_notifiers \
   import push_exception_handler, pop_exception_handler, \
          TraitChangeNotifyWrapper

from category \
    import Category

from traits \
    import Constant, CTrait, Trait, Delegate, DelegatesTo, \
           PrototypedFrom, Property, Button, ToolbarButton, Function, Method, \
           Class, Module, This, self, Either, Python, Disallow, ReadOnly, \
           missing, TraitFactory, Callable, Default, Color, RGBColor, Font, \
           TraitFactory

from trait_types \
    import Any, Int, Long, Float, Complex, Str, Title, Unicode, Bool, CInt, \
           CLong, CFloat, CComplex, CStr, CUnicode, CBool, String, Regex, \
           Code, HTML, Password, Expression, PythonValue, File, Directory, \
           Range, Enum, Tuple, List, CList, Dict, Instance, AdaptedTo, \
           AdaptsTo, Event, Type, WeakRef, false, true, undefined
               
from trait_types \
    import ListInt, ListFloat, ListStr, ListUnicode, ListComplex, ListBool, \
           ListFunction, ListMethod, ListClass, ListInstance, ListThis, \
           DictStrAny, DictStrStr, DictStrInt, DictStrLong, DictStrFloat, \
           DictStrBool, DictStrList
           
from trait_types \
    import BaseInt, BaseLong, BaseFloat, BaseComplex, BaseStr, BaseUnicode, \
           BaseBool, BaseCInt, BaseCLong, BaseCFloat, BaseCComplex, BaseCStr, \
           BaseCUnicode, BaseCBool, BaseFile, BaseDirectory, BaseRange, \
           BaseEnum, BaseTuple, BaseInstance

if python_version >= 2.5:
    from trait_types \
        import UUID

from has_traits \
    import method, HasTraits, HasStrictTraits, HasPrivateTraits, \
           SingletonHasTraits, SingletonHasStrictTraits, \
           SingletonHasPrivateTraits, MetaHasTraits, Vetoable, VetoableEvent, \
           implements, traits_super, on_trait_change, cached_property

from trait_handlers \
    import BaseTraitHandler, TraitType, TraitHandler, TraitRange, TraitString, \
           TraitCoerceType, TraitCastType, TraitInstance, ThisClass, \
           TraitClass, TraitFunction, TraitEnum, TraitPrefixList, TraitMap, \
           TraitPrefixMap, TraitCompound, TraitList, TraitListObject, \
           TraitListEvent, TraitDict, TraitDictObject, TraitDictEvent, \
           TraitTuple

from adapter \
    import Adapter, adapts

from trait_numeric \
    import Array, CArray

from protocols.interfaces \
    import Interface

import ui.view_elements

#-------------------------------------------------------------------------------
#  Patch the main traits module with the correct definition for the ViewElements
#  class:
#-------------------------------------------------------------------------------

import has_traits as has_traits
has_traits.ViewElements = ui.view_elements.ViewElements

#-------------------------------------------------------------------------------
#  Patch the main traits module with the correct definition for the ViewElement
#  and ViewSubElement class:
#-------------------------------------------------------------------------------

has_traits.ViewElement = ui.view_element.ViewElement

