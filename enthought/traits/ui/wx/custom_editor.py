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
# Date: 07/19/2005
#
#  Symbols defined: ToolkitEditorFactory
#
#------------------------------------------------------------------------------
""" Defines the wxPython implementation of the editor and editor factory used
to wrap a non-Traits based custom control.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import Callable, Tuple
    
from editor \
    import Editor
    
from editor_factory \
    import EditorFactory

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython editor factory for custom editors.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # Factory function used to create the custom control
    factory = Callable
    
    # Arguments to be passed to the user's custom editor factory
    args    = Tuple
    
    #---------------------------------------------------------------------------
    #  Initializes the object:  
    #---------------------------------------------------------------------------
        
    def __init__ ( self, *args, **traits ):
        if len( args ) >= 1:
            self.factory = args[0]
            self.args    = args[1:]
        super( ToolkitEditorFactory, self ).__init__( **traits )
    
    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------
    
    def simple_editor ( self, ui, object, name, description, parent ):
        return CustomEditor( parent,
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
        return CustomEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description ) 
    
    def readonly_editor ( self, ui, object, name, description, parent ):
        return CustomEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description ) 
              
#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------
                               
class CustomEditor ( Editor ):
    """ Wrapper for a custom editor control
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory.factory
        if factory is not None:
            try:
                self.control = factory( *(( parent, self ) + self.factory.args ) )
            except:
                from enthought.debug.fbi import if_fbi
                if not if_fbi():
                    import traceback
                    traceback.print_exc()
        if self.control is None:
            self.control = control = wx.StaticText( parent, -1, 
                'An error occurred creating a custom editor.\n'
                'Please contact the developer.' )
            control.SetBackgroundColour( wx.RED )
            control.SetForegroundColour( wx.WHITE )
        self.set_tooltip()
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        pass
    
