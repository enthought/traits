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
# Date: 12/13/2004
#
#  Symbols defined: ToolkitEditorFactory
#
#------------------------------------------------------------------------------
""" Defines the tuple editor and the tuple editor factory, for the wxPython 
user interface toolkit.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.trait_base \
    import SequenceTypes, enumerate
    
from enthought.traits.api \
    import HasTraits, List, Tuple, Str, Int, Any
    
from enthought.traits.ui.api \
    import View, Group, Item
    
from editor \
    import Editor
    
from editor_factory \
    import EditorFactory

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython editor factory for tuple editors.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # Trait definitions for each tuple field
    traits = Any         
    # Labels for each of the tuple fields
    labels = List( Str ) 
    # Number of tuple fields or rows
    cols   = Int( 1 )    
    
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
                                      
#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------
                               
class SimpleEditor ( Editor ):
    """ Simple style of editor for tuples.
    
    The editor displays an editor for each of the fields in the tuple, based on
    the type of each field. 
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self._ts     = ts = TupleStructure( self )
        ui           = ts.view.ui( ts, parent, kind = 'subpanel' )
        self.control = ui.control
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes external to the 
            editor.
        """
        ts = self._ts
        for i, value in enumerate( self.value ):
            setattr( ts, 'f%d' % i, value ) 
            
#-------------------------------------------------------------------------------
#  'TupleStructure' class:
#-------------------------------------------------------------------------------
        
class TupleStructure ( HasTraits ):
    """ Creates a view containing items for each field in a tuple.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
    
    # Editor this structure is linked to
    editor = Any
    
    # The constructed View for the tuple
    view = Any
    
    # Number of tuple fields
    fields = Int
    
    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------
    
    def __init__ ( self, editor ):
        """ Initializes the object.
        """
        factory = editor.factory
        traits  = factory.traits
        labels  = factory.labels
        cols    = factory.cols
        
        # Save the reference to the editor:
        self.editor = editor
        
        # Get the tuple we are mirroring:
        object = editor.value
        
        # For each tuple field, add a trait with the appropriate trait 
        # definition and default value:
        content     = []
        self.fields = len( object )
        len_labels  = len( labels )
        
        if not isinstance( traits, SequenceTypes ):
            traits = [ traits ]
        len_traits = len( traits )
        if len_traits == 0:
            traits     = [ Any ]
            len_traits = 1
            
        for i, value in enumerate( object ):
            trait = traits[ i % len_traits ]
            if i < len_labels:
                label = labels[i]
            else:
                label = ''
            name = 'f%d' % i
            self.add_trait( name, trait( value, event = 'field' ) )
            item = Item( name = name, label = label )
            if cols <= 1:
                content.append( item )
            else:
                if (i % cols) == 0:
                    group = Group( orientation = 'horizontal' )
                    content.append( group )
                group.content.append( item )
        self.view = View( Group( show_labels = (len_labels != 0), *content ) )

    #---------------------------------------------------------------------------
    #  Updates the underlying tuple when any field changes value:
    #---------------------------------------------------------------------------
                
    def _field_changed ( self ):
        """ Updates the underlying tuple when any field changes value.
        """
        self.editor.value = tuple( [ getattr( self, 'f%d' % i ) 
                                     for i in range( self.fields ) ] )
