#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#  
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#  Thanks for using Enthought open source!
#  
#  Author: David C. Morrill
#  Date:   10/21/2004
#
#------------------------------------------------------------------------------

""" Defines the various text editors and the text editor factory, for the 
wxPython user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import Dict, Str, Any, true, false, TraitError
    
from enthought.traits.ui.api \
    import View, Group
    
from editor \
    import Editor
    
from editor_factory \
    import EditorFactory, ReadonlyEditor
    
from constants \
    import OKColor, ErrorColor

#-------------------------------------------------------------------------------
#  Define a simple identity mapping:
#-------------------------------------------------------------------------------

class _Identity ( object ):
    """ A simple indentity mapping.
    """
    def __call__ ( self, value ):    
        return value

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Mapping from user input text to other value
mapping_trait = Dict( Str, Any )

# Function used to evaluate textual user input
evaluate_trait = Any( _Identity() )

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython editor factory for text editors.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # Dictionary that maps user input to other values
    mapping = mapping_trait
    
    # Is user input set on every keystroke?
    auto_set = true
    
    # Is user input set when the Enter key is pressed?
    enter_set = false
    
    # Is multi-line text allowed?
    multi_line = true
    
    # Is user input unreadable? (e.g., for a password)
    password = false
    
    # Function to evaluate textual user input
    evaluate = evaluate_trait
    
    # The object trait containing the function used to evaluate user input
    evaluate_name = Str
    
    #---------------------------------------------------------------------------
    #  Traits view definition:    
    #---------------------------------------------------------------------------
        
    traits_view = View( [ 'auto_set{Set value when text is typed}',
                          'enter_set{Set value when enter is pressed}',
                          'multi_line{Allow multiple lines of text}',
                          '<extras>',
                          '|options:[Options]>' ] )
    
    extras = Group( 'password{Is this a password field?}' )
    
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
        return CustomEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description ) 
    
    def text_editor ( self, ui, object, name, description, parent ):
        return SimpleEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description ) 
    
    def readonly_editor ( self, ui, object, name, description, parent ):
        return ReadonlyTextEditor( parent,
                                   factory     = self, 
                                   ui          = ui, 
                                   object      = object, 
                                   name        = name, 
                                   description = description ) 
                                      
#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------
                               
class SimpleEditor ( Editor ):
    """ Simple style text editor, which displays a text field.
    """
    
    # Flag for window styles:
    base_style = 0
    
    # Background color when input is OK:
    ok_color = OKColor

    #---------------------------------------------------------------------------
    #  Trait definitions: 
    #---------------------------------------------------------------------------
        
    # Function used to evaluate textual user input:
    evaluate = evaluate_trait
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory       = self.factory
        style         = self.base_style
        self.evaluate = factory.evaluate
        self.sync_value( factory.evaluate_name, 'evaluate', 'from' )
            
        if (not factory.multi_line) or factory.is_grid_cell or factory.password:
            style &= ~wx.TE_MULTILINE
        
        if factory.password:
            style |= wx.TE_PASSWORD
            
        multi_line = ((style & wx.TE_MULTILINE) != 0)
        if multi_line:
            self.scrollable = True
            
        if factory.enter_set and (not multi_line):
            control = wx.TextCtrl( parent, -1, self.str_value,
                                   style = style | wx.TE_PROCESS_ENTER )
            wx.EVT_TEXT_ENTER( parent, control.GetId(), self.update_object )
        else:
            control = wx.TextCtrl( parent, -1, self.str_value, style = style )
            
        wx.EVT_KILL_FOCUS( control, self.update_object )
        
        if factory.auto_set and (not factory.is_grid_cell):
           wx.EVT_TEXT( parent, control.GetId(), self.update_object )
           
        self.control = control
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #---------------------------------------------------------------------------
  
    def update_object ( self, event ):
        """ Handles the user entering input data in the edit control.
        """
        if not self._no_update:
            try:
                self.value = self._get_user_value()
                self.control.SetBackgroundColour( self.ok_color )
                self.control.Refresh()
                
                if self._error is not None:
                    self._error     = None
                    self.ui.errors -= 1
                    
            except TraitError, excp:
                pass
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if self._get_user_value() != self.value:
            self._no_update = True
            self.control.SetValue( self.str_value )
            self._no_update = False
            
        if self._error is not None:
            self._error     = None
            self.ui.errors -= 1
            self.control.SetBackgroundColour( self.ok_color )
            self.control.Refresh()

    #---------------------------------------------------------------------------
    #  Gets the actual value corresponding to what the user typed:
    #---------------------------------------------------------------------------
 
    def _get_user_value ( self ):
        """ Gets the actual value corresponding to what the user typed.
        """
        value = self.control.GetValue()
        try:
            value = self.evaluate( value )
        except:
            pass
            
        return self.factory.mapping.get( value, value )
        
    #---------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #---------------------------------------------------------------------------
        
    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's trait value.
        """
        self.control.SetBackgroundColour( ErrorColor )
        self.control.Refresh()
        
        if self._error is None:
            self._error     = True
            self.ui.errors += 1
        
#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------
                               
class CustomEditor ( SimpleEditor ):
    """ Custom style of text editor, which displays a multi-line text field.
    """
    
    # Flag for window style. This value overrides the default.
    base_style = wx.TE_MULTILINE
                                     
#-------------------------------------------------------------------------------
#  'ReadonlyTextEditor' class:
#-------------------------------------------------------------------------------

class ReadonlyTextEditor ( ReadonlyEditor ):
    """ Read-only style of text editor, which displays a read-only text field.
    """
    
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        control   = self.control
        new_value = self.str_value
        
        if self.factory.password:
            new_value = '*' * len( new_value )
            
        if self.item.resizable or (self.item.height != -1):
            if control.GetValue() != new_value:
                control.SetValue( new_value )
                control.SetInsertionPointEnd()
                
        elif control.GetLabel() != new_value:
            control.SetLabel( new_value )
    
