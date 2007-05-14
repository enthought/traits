#------------------------------------------------------------------------------
#
#  Copyright (c) 2006, Enthought, Inc.
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
#  Date: 01/05/2006
#
# 
#   Symbols defined: ToolkitEditorFactory
# 
#------------------------------------------------------------------------------
""" Defines the tree-based Python value editor and the value editor factory, 
for the wxPython user interface toolkit.
# 
.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------
    
from enthought.traits.api \
    import Instance, Int, false
    
from enthought.traits.ui.api \
    import View, Item, TreeEditor
    
from enthought.traits.ui.value_tree \
    import RootNode, value_tree_nodes
    
from editor_factory \
    import EditorFactory
    
from editor \
    import Editor

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython editor factory for tree-based value editors.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------

    # Number of tree levels to automatically open
    auto_open = Int( 2 )
    
    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------
    
    def simple_editor ( self, ui, object, name, description, parent ):
        return SimpleEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description,
                             readonly    = False )
    
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
    """ Simple style of editor for values, which displays a tree.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    # Is the editor read only?
    readonly = false
    
    # The root node of the value tree
    root = Instance( RootNode )
    
    # Is the value editor scrollable? This values overrides the default.
    scrollable = True 
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.update_editor()
        editor = TreeEditor(
            auto_open = self.factory.auto_open,
            hide_root = True,
            editable  = False,
            nodes     = value_tree_nodes
        )
        self._ui = self.edit_traits( parent = parent, view = 
                       View(
                           Item( 'root', 
                                 show_label = False,
                                 editor     = editor
                           ),
                           kind = 'subpanel'
                       )
                   )
        self.control = self._ui.control

        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes external to the 
            editor.
        """
        self.root = RootNode( name     = '', 
                              value    = self.value, 
                              readonly = self.readonly )
        
    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:    
    #---------------------------------------------------------------------------
                
    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self._ui.dispose()
        super( SimpleEditor, self ).dispose()
       
