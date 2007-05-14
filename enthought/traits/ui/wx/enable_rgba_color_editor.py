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
#  Date:   01/16/2005
#
#------------------------------------------------------------------------------

""" Defines the Enable-based implementation of the various RGBA color editors
    and the color editor factory.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import Enum, Str, KivaFont, true
    
from enthought.traits.ui.api \
    import View
                        
from rgba_color_editor \
    import ToolkitEditorFactory as EditorFactory
    
from editor \
    import Editor
    
from helper \
    import position_near

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Color used for background of color picker
WindowColor = ( 236 / 255.0, 233 / 255.0, 216 / 255.0, 1.0 )

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Possible styles of color editors
EditorStyle = Enum( 'simple', 'custom' ) 
    
#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython editor factory for Enable RGBA color editors.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
    
    # Should the color be updated automatically? 
    auto_set = true
    
    # Initial color space mode: 
    mode = Enum( 'rgb', 'hsv', 'hsv2', 'hsv3', cols = 2 )
    
    # Should the alpha channel be edited?
    edit_alpha = true
    
    # Text to display in the color well:
    text = Str( '%R' )
    
    # Font to use when displaying text:
    font = KivaFont( 'modern 10' )  
    
    #---------------------------------------------------------------------------
    #  Traits view definition:  
    #---------------------------------------------------------------------------
    
    traits_view = View(
        [ [ 'mapped{Is the value mapped?}', 
            'auto_set{Should the value be set while dragging a slider?}',
            'edit_alpha{Should the alpha channel be edited?}',
            '|[Options]>' ],
          [ 'mode{Inital mode}@',
            '|[Color Space]' ],
          [ 'text', 'font@',
            '|[Color well]' ] ] )
    
    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------
    
    def simple_editor ( self, ui, object, name, description, parent ):
        return ColorEditor( parent,
                            factory     = self, 
                            ui          = ui, 
                            object      = object, 
                            name        = name, 
                            description = description,
                            style       = 'simple' )
    
    def custom_editor ( self, ui, object, name, description, parent ):
        return ColorEditor( parent,
                            factory     = self, 
                            ui          = ui, 
                            object      = object, 
                            name        = name, 
                            description = description,
                            style       = 'custom' )
                                      
#-------------------------------------------------------------------------------
#  'ColorEditor' class:
#-------------------------------------------------------------------------------
                               
class ColorEditor ( Editor ):
    """ Editor for RGBA colors, which displays an Enable color picker.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:    
    #---------------------------------------------------------------------------
    
    # Style of editor
    style = Enum( 'simple', 'custom' )  
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        from enthought.enable.wx import Window
        from enthought.enable    import ColorPicker
        
        factory = self.factory
        picker  = ColorPicker( color      = factory.get_color( self ),
                               bg_color   = WindowColor,
                               style      = self.style,
                               auto_set   = factory.auto_set,
                               mode       = factory.mode,
                               edit_alpha = factory.edit_alpha,
                               text       = factory.text,
                               font       = factory.font )
        window       = Window( parent, component = picker )
        self.control = window.control
        self._picker = picker
        self.control.SetSize( ( picker.min_width, picker.min_height ) )
        picker.on_trait_change( self.popup_editor,  'clicked', dispatch = 'ui' )
        picker.on_trait_change( self.update_object, 'color',   dispatch = 'ui' )
       
    #---------------------------------------------------------------------------
    #  Invokes the pop-up editor for an object trait:
    #---------------------------------------------------------------------------
 
    def popup_editor ( self, event ):
        """ Invokes the pop-up editor for an object trait.
        """
        color_data = wx.ColourData()
        color_data.SetColour( self.factory.to_wx_color( self ) )
        color_data.SetChooseFull( True )
        dialog = wx.ColourDialog( self.control, color_data )
        position_near( self.control, dialog )
        
        if dialog.ShowModal() == wx.ID_OK:
            self.value = self.factory.from_wx_color( 
                              dialog.GetColourData().GetColour() )
                              
        dialog.Destroy()                      
        
    #---------------------------------------------------------------------------
    #  Updates the object trait when a color swatch is clicked:
    #---------------------------------------------------------------------------
        
    def update_object ( self, event ):
        """ Updates the object trait when a color swatch is clicked.
        """
        self.value = self._picker.color
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        self._picker.color = self.value

