#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
# 
#  Written by: David C. Morrill
#
#  Date: 12/06/2005
# 
#------------------------------------------------------------------------------

""" Pseudo-package for all of the core symbols from Traits and TraitsUI. 
Use this module for importing Traits names into your namespace. For example::
    
    from enthought.traits.api import HasTraits
"""

__version__ = '2.1.0'

from trait_base \
    import Undefined, Missing, Self

from trait_errors \
    import TraitError, TraitNotificationError, DelegationError
    
from trait_notifiers \
   import push_exception_handler, pop_exception_handler, \
          TraitChangeNotifyWrapper

from category \
    import Category

from trait_db \
    import tdb
    
from traits \
    import Event, Constant, CTrait, Trait, Delegate, Property, Button, \
           ToolbarButton, Function, Method, Class, Module, Type, This, self, \
           Either, Python, Disallow, ReadOnly, missing, TraitFactory, \
           Callable, Default, Color, RGBColor, RGBAColor, Font, KivaFont, \
           TraitFactory, UIDebugger
           
from trait_types \
    import Any, Int, Long, Float, Complex, Str, Unicode, Bool, CInt, CLong, \
           CFloat, CComplex, CStr, CUnicode, CBool, String, Regex, Code, HTML, \
           Password, Expression, PythonValue, File, Directory, Range, Enum, \
           Tuple, List, Dict, Instance, WeakRef, false, true, undefined
           
from trait_types \
    import ListInt, ListFloat, ListStr, ListUnicode, ListComplex, ListBool, \
           ListFunction, ListMethod, ListClass, ListInstance, ListThis, \
           DictStrAny, DictStrStr, DictStrInt, DictStrLong, DictStrFloat, \
           DictStrBool, DictStrList
    
from has_traits \
    import method, HasTraits, HasStrictTraits, HasPrivateTraits, \
           SingletonHasTraits, SingletonHasStrictTraits, \
           SingletonHasPrivateTraits, MetaHasTraits, Adapter, Vetoable, \
           VetoableEvent, implements, adapts, traits_super, on_trait_change, \
           cached_property
           
from trait_handlers \
    import BaseTraitHandler, TraitType, TraitHandler, TraitRange, TraitString, \
           TraitCoerceType, TraitCastType, TraitInstance, ThisClass, \
           TraitClass, TraitFunction, TraitEnum, TraitPrefixList, TraitMap, \
           TraitPrefixMap, TraitCompound, TraitList, TraitListEvent, \
           TraitDict, TraitDictEvent, TraitTuple
  
from trait_numeric \
    import Array, CArray
    
from protocols.interfaces \
    import Interface

#-------------------------------------------------------------------------------
#  ui imports:
#-------------------------------------------------------------------------------

if True:
    
    from ui.handler \
        import Handler, ViewHandler, default_handler
        
    from ui.view \
        import View
        
    from ui.group \
        import Group, HGroup, VGroup, VGrid, HFlow, VFlow, HSplit, VSplit, Tabbed
        
    from ui.ui \
        import UI
        
    from ui.ui_info \
        import UIInfo
    
    from ui.help \
        import on_help_call
        
    from ui.include \
        import Include
        
    from ui.item \
        import Item, Label, Heading, Spring, spring
        
    from ui.editor_factory \
        import EditorFactory
        
    from ui.editor \
        import Editor
        
    from ui.toolkit \
        import toolkit
        
    from ui.undo \
        import UndoHistory, AbstractUndoItem, UndoItem, ListUndoItem, \
               UndoHistoryUndoItem
               
    from ui.view_element \
        import ViewElement, ViewSubElement
        
    from ui.help_template \
        import help_template
        
    from ui.message \
        import message, error
        
    from ui.tree_node \
        import TreeNode, ObjectTreeNode, TreeNodeObject, MultiTreeNode
        
    from ui.editors \
        import ArrayEditor, BooleanEditor, ButtonEditor, CheckListEditor, \
               CodeEditor, ColorEditor, RGBColorEditor, RGBAColorEditor, \
               CompoundEditor, DirectoryEditor, EnumEditor, FileEditor, \
               FontEditor, KivaFontEditor, ImageEnumEditor, InstanceEditor, \
               ListEditor, PlotEditor, RangeEditor, TextEditor, TreeEditor, \
               TableEditor, TupleEditor, DropEditor, DNDEditor, CustomEditor
               
    from ui.editors \
        import ColorTrait, RGBColorTrait, RGBAColorTrait, EnableRGBAColorEditor, \
               FontTrait, KivaFontTrait, SetEditor, HTMLEditor, KeyBindingEditor, \
               ShellEditor, TitleEditor, ValueEditor, NullEditor


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
