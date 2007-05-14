#-------------------------------------------------------------------------------
#
#  Written by: David C. Morrill
#
#  Date: 07/26/2006
#
#  (c) Copyright 2006 by Enthought, Inc.
#
#-------------------------------------------------------------------------------
""" Defines a completely empty editor, intended to be used as a spacer.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.ui.wx.editor \
    import Editor
    
from enthought.traits.ui.wx.basic_editor_factory \
    import BasicEditorFactory
                                      
#-------------------------------------------------------------------------------
#  'NullEditor' class:
#-------------------------------------------------------------------------------
                               
class NullEditor ( Editor ):
    """ A completely empty editor.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = wx.Panel( parent, -1 )
                        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        pass

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------
                
ToolkitEditorFactory = BasicEditorFactory( klass = NullEditor )
                 
