#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# 
# Author: David C. Morrill
# Date: 10/21/2004
#
#  Symbols defined: EditorFactory
#
#------------------------------------------------------------------------------
""" Defines the base wxPython EditorFactory class and classes the various 
styles of editors used in a Traits-based user interface.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx
    
from enthought.traits.api \
    import TraitError, Any, Str

from enthought.traits.ui.editor_factory \
    import EditorFactory as UIEditorFactory
    
from editor \
    import Editor
    
from constants \
    import ReadonlyColor, WindowColor

#-------------------------------------------------------------------------------
#  'EditorFactory' base class:
#-------------------------------------------------------------------------------

class EditorFactory ( UIEditorFactory ):
    """ Base class for wxPython editor factories.
    """
    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------
    
    def simple_editor ( self, ui, object, name, description, parent ):
        return SimpleEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description ) 
    
    def custom_editor ( self, ui, object, name, description, parent ):
        return self.simple_editor( ui, object, name, description, parent )
    
    def text_editor ( self, ui, object, name, description, parent ):
        return TextEditor( parent,
                           factory     = self, 
                           ui          = ui, 
                           object      = object, 
                           name        = name, 
                           description = description ) 
    
    def readonly_editor ( self, ui, object, name, description, parent ):
        return ReadonlyEditor( parent,
                               factory     = self, 
                               ui          = ui, 
                               object      = object, 
                               name        = name, 
                               description = description )
                               
#-------------------------------------------------------------------------------
#  'EditorWithListFactory' base class:
#-------------------------------------------------------------------------------

class EditorWithListFactory ( EditorFactory ):
    """ Base class for factories of editors for objects that contain lists.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    # Values to enumerate
    values = Any 
    
    # Name of the context object containing the enumeration data
    object = Str( 'object' )
    
    # Name of the trait on 'object' containing the enumeration data
    name = Str  

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------
                        
class SimpleEditor ( Editor ):
    """ Base class for simple style editors, which displays a text field
    containing the text representation of the object trait value. Clicking in
    the text field displays an editor-specific dialog box for changing the
    value.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = wx.TextCtrl( parent, -1, self.str_value,
                                    style = wx.TE_READONLY )
        wx.EVT_LEFT_UP( self.control, self.popup_editor )
        self.set_tooltip()
       
    #---------------------------------------------------------------------------
    #  Invokes the pop-up editor for an object trait:
    #  
    #  (Normally overridden in a subclass)
    #---------------------------------------------------------------------------
 
    def popup_editor ( self, event ):
        """ Invokes the pop-up editor for an object trait.
        """
        pass

#-------------------------------------------------------------------------------
#  'TextEditor' class:
#-------------------------------------------------------------------------------

class TextEditor ( Editor ):
    """ Base class for text style editors, which displays an editable text 
    field, containing a text representation of the object trait value.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = wx.TextCtrl( parent, -1, self.str_value )
        wx.EVT_KILL_FOCUS( self.control, self.update_object )
        wx.EVT_TEXT_ENTER( parent, self.control.GetId(), self.update_object )
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the user changing the contents of the edit control:
    #---------------------------------------------------------------------------
  
    def update_object ( self, event ):
        """ Handles the user changing the contents of the edit control.
        """
        try:
            self.value = self.control.GetValue()
        except TraitError, excp:
            pass
                               
#-------------------------------------------------------------------------------
#  'ReadonlyEditor' class:
#-------------------------------------------------------------------------------

class ReadonlyEditor ( Editor ):
    """ Base class for read-only style editors, which displays a read-only text
    field, containing a text representation of the object trait value.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    # layout_style = 0  # Style for imbedding control in a sizer (override)
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        if self.item.resizable or (self.item.height != -1):
            self.control = wx.TextCtrl( parent, -1, self.str_value,
                       style = wx.NO_BORDER | wx.TE_MULTILINE | wx.TE_READONLY )
            self.control.SetBackgroundColour( WindowColor )                                      
        else:
            self.control = wx.StaticText( parent, -1, self.str_value,
                                          style = wx.ALIGN_LEFT )
            self.layout_style = 0
        self.set_tooltip()
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        new_value = self.str_value
        if self.item.resizable or (self.item.height!= -1):
            if self.control.GetValue() != new_value:
                self.control.SetValue( new_value )
        elif self.control.GetLabel() != new_value:
            self.control.SetLabel( new_value )
                               
