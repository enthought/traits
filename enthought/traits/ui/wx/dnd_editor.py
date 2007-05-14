#------------------------------------------------------------------------------
# 
#  Written by: David C. Morrill
#
#  Date: 06/25/2006
#
#  (c) Copyright 2006 by Enthought, Inc.
#
#------------------------------------------------------------------------------
""" Defines the various editors and editor factory for a drag-and-drop editor,
for the wxPython user interface toolkit. A drag-and-drop editor represents its
value as a simple image which, depending upon the editor style, can be either
a drop target only, or both a drop target and a drag source.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from cPickle \
    import load

from enthought.traits.api \
    import Instance, true
    
from editor \
    import Editor
    
from editor_factory \
    import EditorFactory

from enthought.util.numerix \
    import array, fromstring, reshape, UnsignedInt8, ravel

from enthought.util.wx.drag_and_drop \
    import PythonDropSource, PythonDropTarget, clipboard
    
from enthought.io \
    import File
    
from enthought.naming.api \
    import Binding
           
from enthought.pyface.image_resource \
    import ImageResource
    
#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The image to use when the editor accepts files
file_image = ImageResource( 'file' ).create_image()

# The image to use when the editor accepts objects
object_image = ImageResource( 'object' ).create_image()

# String types
string_type = ( str, unicode )

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython editor factory for drag-and-drop editors.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # The image to use for the target
    image = Instance( ImageResource, allow_none = True )
    
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
        return ReadOnlyEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description ) 
                                      
#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------
                               
class SimpleEditor ( Editor ):
    """ Simply style of editor for a drag-and-drop editor, which is both a drag
    source and a drop target.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------

    # Is the editor a drop target?
    drop_target = true
    
    # Is the editor a drag source?
    drag_source = true
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Determine the drag/drop type:
        value         = self.value
        self._is_list = isinstance( value, list )
        self._is_file = (isinstance( value, string_type ) or
                         (self._is_list and (len( value ) > 0) and
                          isinstance( value[0], string_type )))
          
        # Get the right image to use:
        image = self.factory.image
        if image is not None:
            image = image.create_image()
        elif self._is_file:
            image = file_image
        else:
            image = object_image
        self._img    = image
        self._image  = image.ConvertToBitmap()
        
        # Create the control and set up the event handlers:
        self.control = control = wx.Window( parent, -1, 
                         size = wx.Size( image.GetWidth(), image.GetHeight() ) )
        self.set_tooltip()
        
        if self.drop_target:
            control.SetDropTarget( PythonDropTarget( self ) )
            
        wx.EVT_LEFT_DOWN( control, self._left_down )
        wx.EVT_LEFT_UP(   control, self._left_up )
        wx.EVT_MOTION(    control, self._mouse_move )
        wx.EVT_PAINT(     control, self._on_paint )
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        return
        
#-- Private Methods ------------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Returns the processed version of a drag request's data:  
    #---------------------------------------------------------------------------

    def _get_drag_data ( self, data ):
        """ Returns the processed version of a drag request's data.
        """
        if isinstance( data, list ):
            if isinstance( data[0], Binding ):
                data = [ item.obj for item in data ]
            if isinstance( data[0], File ):
                data = [ item.absolute_path for item in data ]
                if not self._is_file:
                    result = []
                    for file in data:
                        item = self._unpickle( file )
                        if item is not None:
                            result.append( item )
                    data = result
                            
        else:
            if isinstance( data, Binding ):
                data = data.obj
            if isinstance( data, File ):
                data = data.absolute_path
                if not self._is_file:
                    object = self._unpickle( data )
                    if object is not None:
                        data = object
                
        return data
        
    #---------------------------------------------------------------------------
    #  Returns the unpickled version of a specified file (if possible):    
    #---------------------------------------------------------------------------
                
    def _unpickle ( self, file_name ):
        """ Returns the unpickled version of a specified file (if possible).
        """
        fh = None
        try:
            fh     = file( file_name, 'rb' )
            object = load( fh )
        except:
            object = None
            
        if fh is not None:
            fh.close()
            
        return object
        
#-- wxPython Event Handlers ----------------------------------------------------

    def _on_paint ( self, event ):
        """ Called when the control needs repainting. 
        """
        image   = self._image
        control = self.control
        if not control.IsEnabled():
            if self._mono_image is None:
                img  = self._img
                data = reshape( fromstring( img.GetData(), UnsignedInt8 ), 
                          ( -1, 3 ) ) * array( [ [ 0.297, 0.589, 0.114 ] ] )
                g = data[ :, 0 ] + data[ :, 1 ] + data[ :, 2 ]
                data[ :, 0 ] = data[ :, 1 ] = data[ :, 2 ] = g
                img.SetData( ravel( data.astype( UnsignedInt8 ) ).tostring() )
                img.SetMaskColour( 0, 0, 0 )
                self._mono_image = img.ConvertToBitmap()
                self._img        = None
            image = self._mono_image
            
        wdx, wdy = control.GetClientSizeTuple()
        wx.PaintDC( control ).DrawBitmap( image,
            (wdx - image.GetWidth())  / 2, (wdy - image.GetHeight()) / 2, True )
           
    def _left_down ( self, event ):
        """ Handles the left mouse button being pressed.
        """
        if self.control.IsEnabled() and self.drag_source:
            self._x, self._y = event.GetX(), event.GetY()
            self.control.CaptureMouse()
            
        event.Skip()
    
    def _left_up ( self, event ):
        """ Handles the left mouse button being released.
        """
        if self._x is not None:
            self._x = None
            self.control.ReleaseMouse()
            
        event.Skip()
            
    def _mouse_move ( self, event ):
        """ Handles the mouse being moved.
        """
        if self._x is not None:
            if ((abs( self._x - event.GetX() ) + 
                 abs( self._y - event.GetY() )) >= 3):
                self.control.ReleaseMouse()
                self._x = None
                if self._is_file:
                    FileDropSource(   self.control, self.value )
                else:
                    PythonDropSource( self.control, self.value )
                
        event.Skip()

#----- Drag and drop event handlers: -------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles a Python object being dropped on the control:    
    #---------------------------------------------------------------------------

    def wx_dropped_on ( self, x, y, data, drag_result ):
        """ Handles a Python object being dropped on the tree.
        """
        try:
            self.value = self._get_drag_data( data )
            return drag_result
        except:
            return wx.DragNone

    #---------------------------------------------------------------------------
    #  Handles a Python object being dragged over the control:    
    #---------------------------------------------------------------------------
                
    def wx_drag_over ( self, x, y, data, drag_result ):
        """ Handles a Python object being dragged over the tree.
        """
        try:
            self.object.base_trait( self.name ).validate( self.object,
                                        self.name, self._get_drag_data( data ) )
            return drag_result
        except:
            return wx.DragNone
                                      
#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------
                               
class CustomEditor ( SimpleEditor ):
    """ Custom style of drag-and-drop editor, which is not a drag source.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
    
    # Is the editor a drag source? This value overrides the default.
    drag_source = False
    
#-------------------------------------------------------------------------------
#  'ReadOnlyEditor' class:
#-------------------------------------------------------------------------------

class ReadOnlyEditor ( SimpleEditor ):
    """ Read-only style of drag-and-drop editor, which is not a drop target.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------

    # Is the editor a drop target? This value overrides the default.
    drop_target = False
    
#-------------------------------------------------------------------------------
#  'FileDropSource' class:
#-------------------------------------------------------------------------------

class FileDropSource ( wx.DropSource ):
    """ Represents a draggable file.
    """
    #---------------------------------------------------------------------------
    #  Initializes the object:  
    #---------------------------------------------------------------------------
        
    def __init__ ( self, source, files ):
        """ Initializes the object.
        """
        self.handler    = None
        self.allow_move = True
        
        # Put the data to be dragged on the clipboard:
        clipboard.data        = files
        clipboard.source      = source
        clipboard.drop_source = self
        
        data_object = wx.FileDataObject()
        if isinstance( files, string_type ):
            files = [ files ]
        for file in files:
            data_object.AddFile( file )

        # Create the drop source and begin the drag and drop operation:
        super( FileDropSource, self ).__init__( source )
        self.SetData( data_object )
        self.result = self.DoDragDrop( True )

    #---------------------------------------------------------------------------
    #  Called when the data has been dropped:
    #---------------------------------------------------------------------------

    def on_dropped ( self, drag_result ):
        """ Called when the data has been dropped. """
        return
    
