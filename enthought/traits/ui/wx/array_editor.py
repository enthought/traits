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
#
#  Date:   01/10/2006
#
# 
#   Symbols defined: ToolkitEditorFactory
# 
#------------------------------------------------------------------------------
""" Defines array editors and the array editor factory for the wxPython
user interface toolkit.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx
    
from enthought.util.numerix \
    import zeros, typecode
    
from enthought.traits.api \
    import HasTraits, Int, Float, Instance, false
    
from enthought.traits.ui.api \
    import View, Group, Item
    
from enthought.traits.ui.wx.editor \
    import Editor
    
from enthought.traits.ui.wx.editor_factory \
    import EditorFactory

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython editor factory for array editors.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    # Width of the individual fields
    width = Int( -80 )
    
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
    
    def readonly_editor ( self, ui, object, name, description, parent ):
        return SimpleEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description,
                             readonly    = True ) 
                                      
#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------
                               
class SimpleEditor ( Editor ):
    """ Simple style of editor for arrays.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    # Is the editor read-only?
    readonly = false
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self._as     = _as = ArrayStructure( self )
        ui           = _as.view.ui( _as, parent, kind = 'subpanel' )
        self.control = ui.control
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        if not self._busy:
            object = self.value
            shape  = object.shape
            _as    = self._as
            for i in range( shape[0] ):
                for j in range( shape[1] ):
                    setattr( _as, 'f%d_%d' % ( i, j ), object[i,j] )
                
    #---------------------------------------------------------------------------
    #  Updates the array value associated with the editor:  
    #---------------------------------------------------------------------------
                                
    def update_array ( self, value ):
        """ Updates the array value associated with the editor.
        """
        self._busy = True
        self.value = value
        self._busy = False
            
#-------------------------------------------------------------------------------
#  'ArrayStructure' class:
#-------------------------------------------------------------------------------
        
class ArrayStructure ( HasTraits ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
    
    # Editor that this structure is linked to
    editor = Instance( Editor )
    
    # The constructed View for the array
    view = Instance( View )
    
    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------
    
    def __init__ ( self, editor ):
        """ Initializes the object.
        """
        # Save the reference to the editor:
        self.editor = editor
        
        # Set up the field width for each item:
        width = editor.factory.width
        
        # Set up the correct style for each filed:
        style = 'simple'
        if editor.readonly:
            style = 'readonly'
        
        # Get the array we are mirroring:
        object = editor.value
        
        # Determine the correct trait type to use for each element:
        trait = Float
        if isinstance( object[0,0], int ):
            trait = Int
            
        content = []
        shape   = object.shape
        for i in range( shape[0] ):
            items = []
            for j in range( shape[1] ):
                name = 'f%d_%d' % ( i, j )
                self.add_trait( name, trait( object[i,j], event = 'field' ) )
                items.append( Item( name  = name, 
                                    style = style,
                                    width = width ) )
            group = Group( orientation = 'horizontal', 
                           show_labels = False,
                           *items )
            content.append( group )
        self.view = View( Group( show_labels = False, *content ) )

    #---------------------------------------------------------------------------
    #  Updates the underlying tuple when any field changes value:
    #---------------------------------------------------------------------------
                
    def _field_changed ( self ):
        """ Updates the underlying array when any field changes value.
        """
        # Get the array we are mirroring:
        object = self.editor.value
        shape  = object.shape
        value  = zeros( shape, typecode( object ) )
        for i in range( shape[0] ):
            for j in range( shape[1] ):
                value[i,j] = getattr( self, 'f%d_%d' % ( i, j ) )
                     
        self.editor.update_array( value )
        
