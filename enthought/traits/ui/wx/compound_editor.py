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
""" Defines the compound editor and the compound editor factory for the 
wxPython user interface toolkit.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from editor_factory   import EditorFactory
from editor           import Editor
from enthought.traits.api import List, Str, true

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# List of component editor factories used to build a compound editor
editors_trait = List( EditorFactory )

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython editor factory for compound editors.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # Component editor factories used to build the editor
    editors  = editors_trait 
    # Is user input set on every keystroke?
    auto_set = true          
    
    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------
    
    def simple_editor ( self, ui, object, name, description, parent ):
        return CompoundEditor( parent,
                               factory     = self, 
                               ui          = ui, 
                               object      = object, 
                               name        = name, 
                               description = description,
                               kind        = 'simple_editor' )
    
    def custom_editor ( self, ui, object, name, description, parent ):
        return CompoundEditor( parent,
                               factory     = self, 
                               ui          = ui, 
                               object      = object, 
                               name        = name, 
                               description = description,
                               kind        = 'custom_editor' )
                                      
#-------------------------------------------------------------------------------
#  'CompoundEditor' class:
#-------------------------------------------------------------------------------
                               
class CompoundEditor ( Editor ):
    """ Editor for compound traits, which displays editors for each of the
    combined traits, in the appropriate style.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # The kind of editor to create for each list item
    kind = Str  
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Create a panel to hold all of the component trait editors:
        self.control = panel = wx.Panel( parent, -1 )
        sizer        = wx.BoxSizer( wx.VERTICAL )
        
        # Add all of the component trait editors:
        self._editors = editors = []
        for factory in self.factory.editors:
            editor = getattr( factory, self.kind )( self.ui, self.object, 
                                       self.name, self.description, panel )
            editor.prepare( panel )
            sizer.Add( editor.control, 1, 
                       wx.TOP | wx.BOTTOM | editor.layout_style, 3 )
            editors.append( editor )
     
        # Set-up the layout:
        panel.SetSizerAndFit( sizer )
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        pass
        
    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:    
    #---------------------------------------------------------------------------
                
    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        super( CompoundEditor, self ).dispose()
        for editor in self._editors:
            editor.dispose()
        
