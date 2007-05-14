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
#  Symbols defined: ToolkitEditorFactory
#
#------------------------------------------------------------------------------
""" Defines the various Boolean editors and the Boolean editor factory for the
wxPython user interface toolkit.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api    import Dict, Str, Any, true
from enthought.traits.ui.api import View
from editor              import Editor
from text_editor         import SimpleEditor         as TextEditor
from text_editor         import ToolkitEditorFactory as EditorFactory
from constants           import ReadonlyColor

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Mapping from user input text to Boolean values
mapping_trait = Dict( Str, Any, { 'True':  True,
                                  'true':  True,
                                  't':     True,
                                  'yes':   True,
                                  'y':     True,
                                  'False': False,
                                  'false': False,
                                  'f':     False,
                                  'no':    False,
                                  'n':     False,
                    } )

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython editor factory for Boolean editors.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # Dictionary mapping user input to other values. 
    # These definitions override definitions in the 'text_editor' version
    mapping = mapping_trait  
    
    #---------------------------------------------------------------------------
    #  Traits view definition:  
    #---------------------------------------------------------------------------
    
    traits_view = View()    
    
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
        return SimpleEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description ) 
    
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
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------
                               
class SimpleEditor ( Editor ):
    """ Simple style of editor for Boolean values, which displays a check box.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = wx.CheckBox( parent, -1, '' )
        wx.EVT_CHECKBOX( parent, self.control.GetId(), self.update_object )
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the user clicking on the checkbox:
    #---------------------------------------------------------------------------
 
    def update_object ( self, event ):
        """ Handles the user clicking the checkbox.
        """
        self.value = (self.control.GetValue() != 0)
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        self.control.SetValue( self.value )
                                      
#-------------------------------------------------------------------------------
#  'ReadonlyEditor' class:
#-------------------------------------------------------------------------------
                               
class ReadonlyEditor ( Editor ):
    """ Read-only style of editor for Boolean values, which displays static text
    of either "True" or "False".
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = wx.TextCtrl( parent, -1, '', style = wx.TE_READONLY )
        self.control.SetBackgroundColour( ReadonlyColor )
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #
    #  (Should normally be overridden in a subclass)
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        if self.value:
            self.control.SetLabel( 'True' )
        else:
            self.control.SetLabel( 'False' )

