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
""" Defines the various image enumeration editors and the image enumeration 
editor factory for the wxPython user interface toolkit..
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys
import wx

from os \
    import getcwd
    
from os.path \
    import join, dirname, exists
    
from enum_editor \
    import ToolkitEditorFactory as EditorFactory
    
from editor \
    import Editor
    
from helper \
    import bitmap_cache, position_near
    
from image_control \
    import ImageControl
    
from enthought.traits.api \
    import Str, Type, Module, Any

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython editor factory for image enumeration editors.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # Suffix to add to values to form image names:
    suffix = Str
    
    # Path to use to locate image files:
    path = Str
    
    # Class used to derive the path to the image files:
    klass = Type
    
    # Module used to derive the path to the image files:
    module = Module 
    
    #---------------------------------------------------------------------------
    #  Performs any initialization needed after all constructor traits have 
    #  been set:
    #---------------------------------------------------------------------------
     
    def init ( self ):
        """ Performs any initialization needed after all constructor traits 
            have been set.
        """
        super( ToolkitEditorFactory, self ).init()
        self._update_path()
        
    #---------------------------------------------------------------------------
    #  Handles one of the items defining the path being updated:
    #---------------------------------------------------------------------------
        
    def _update_path ( self ):
        """ Handles one of the items defining the path being updated.
        """
        if self.path != '':
            self._image_path = self.path
        elif self.klass is not None:
            module = self.klass.__module__
            if module == '___main___':
                module = '__main__'
            try:
                self._image_path = join( dirname( sys.modules[ module
                                                        ].__file__ ), 'images' )
            except:                    
                self._image_path = self.path
                dirs = [ join( dirname( sys.argv[0] ), 'images' ),
                         join( getcwd(), 'images' ) ]
                for d in dirs:
                    if exists( d ):
                        self._image_path = d
                        break
        elif self.module is not None:
            self._image_path = join( dirname( self.module.__file__ ), 'images' )
           
    def _path_changed ( self ):            
        self._update_path()
        
    def _klass_changed ( self ):        
        self._update_path()
        
    def _module_changed ( self ):        
        self._update_path()
    
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
    
    def readonly_editor ( self, ui, object, name, description, parent ):
        return ReadonlyEditor( parent,
                               factory     = self, 
                               ui          = ui, 
                               object      = object, 
                               name        = name, 
                               description = description ) 
                                      
#-------------------------------------------------------------------------------
#  'ReadonlyEditor' class:
#-------------------------------------------------------------------------------
                               
class ReadonlyEditor ( Editor ):
    """ Read-only style of image enumeration editor, which displays a single 
    ImageControl, representing the object trait's value.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = ImageControl( parent,  
                             bitmap_cache( self.str_value + self.factory.suffix, 
                                           False, self.factory._image_path ) )                                   
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        self.control.Bitmap( bitmap_cache( self.str_value + self.factory.suffix, 
                                           False, self.factory._image_path ) )
                                      
#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------
                               
class SimpleEditor ( ReadonlyEditor ):
    """ Simple style of image enumeration editor, which displays an 
    ImageControl, representing the object trait's value. Clicking an image 
    displays a dialog box for selecting an image corresponding to a different
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
        super( SimpleEditor, self ).init( parent )
        self.control.Selected( True )
        self.control.Handler( self.popup_editor )
        
    #---------------------------------------------------------------------------
    #  Handles the user clicking the ImageControl to display the pop-up dialog:
    #---------------------------------------------------------------------------
        
    def popup_editor ( self, control ):
        """ Handles the user clicking the ImageControl to display the pop-up 
            dialog.
        """
        ImageEnumDialog( self )
                                      
#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------
                               
class CustomEditor ( Editor ):
    """ Custom style of image enumeration editor, which displays a grid of 
    ImageControls. The user can click an image to select the corresponding
    value.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    update_handler = Any  # Callback to call when any button clicked
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self._create_image_grid( parent )

    #---------------------------------------------------------------------------
    #  Populates a specified window with a grid of image buttons:
    #---------------------------------------------------------------------------
    
    def _create_image_grid ( self, parent ):
        """ Populates a specified window with a grid of image buttons.
        """
        # Create the panel to hold the ImageControl buttons:
        self.control = panel = wx.Panel( parent, -1 )
        
        # Create the main sizer:
        if self.factory.cols > 1:
           sizer = wx.GridSizer( 0, self.factory.cols, 0, 0 )
        else:
           sizer = wx.BoxSizer( wx.VERTICAL )
        
        # Add the set of all possible choices:
        mapping   = self.factory._mapping
        cur_value = self.value
        for name in self.factory._names:
            value   = mapping[ name ]
            control = ImageControl( panel, 
                          bitmap_cache( name + self.factory.suffix, False, 
                                        self.factory._image_path ),
                          value == cur_value, 
                          self.update_object )
            control.value = value
            sizer.Add( control, 0, wx.ALL, 2 )
            self.set_tooltip( control )
 
        # Finish setting up the control layout:
        panel.SetSizerAndFit( sizer )

    #---------------------------------------------------------------------------
    #  Handles the user clicking on an ImageControl to set an object value:
    #---------------------------------------------------------------------------
  
    def update_object ( self, control ):
        """ Handles the user clicking on an ImageControl to set an object value.
        """
        self.value = control.value
        if self.update_handler is not None:
            self.update_handler()
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        value = self.value
        for control in self.control.GetChildren():
            control.Selected( value == control.value )

#-------------------------------------------------------------------------------
#  'ImageEnumDialog' class:  
#-------------------------------------------------------------------------------

class ImageEnumDialog ( wx.Frame ):
    """ Dialog box for selecting an ImageControl
    """
    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------
 
    def __init__ ( self, editor ):
        """ Initializes the object.
        """
        wx.Frame.__init__( self, editor.control, -1, '',
                           style = wx.SIMPLE_BORDER )
        wx.EVT_ACTIVATE( self, self._on_close_dialog )
        self._closed = False
        
        dlg_editor = CustomEditor( self,
                                   factory        = editor.factory, 
                                   ui             = editor.ui, 
                                   object         = editor.object, 
                                   name           = editor.name, 
                                   description    = editor.description,
                                   update_handler = self._close_dialog )

        dlg_editor.init( self )
        
        # Wrap the dialog around the image button panel:
        sizer = wx.BoxSizer( wx.VERTICAL )
        sizer.Add( dlg_editor.control )
        sizer.Fit( self )
 
        # Position the dialog:
        position_near( editor.control, self )
        self.Show()
        
    #---------------------------------------------------------------------------
    #  Closes the dialog:
    #---------------------------------------------------------------------------
 
    def _on_close_dialog ( self, event ):
        """ Closes the dialog.
        """
        if not event.GetActive():
            self._close_dialog()
 
    #---------------------------------------------------------------------------
    #  Closes the dialog:
    #---------------------------------------------------------------------------
 
    def _close_dialog ( self ):
        """ Closes the dialog.
        """
        if not self._closed:
            self._closed = True
            self.Destroy()
            
