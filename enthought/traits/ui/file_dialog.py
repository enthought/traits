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
#  Date:   10/07/2004
#
#------------------------------------------------------------------------------

""" Defines functions and classes used to create pop-up file dialogs for
    opening and saving files.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------
    
from os.path \
    import split, isfile, getsize, getatime, getmtime, getctime

from time \
    import localtime, strftime
    
from enthought.traits.api \
    import HasPrivateTraits, File, List, Str, Int, Instance, Property, Button, \
           Bool, Interface, implements, cached_property
    
from enthought.traits.ui.api \
    import View, VGroup, HGroup, HSplit, Item, Handler, FileEditor, \
           InstanceEditor, CodeEditor
    
from enthought.traits.ui.ui_traits \
    import AView
    
# fixme: The HistoryEditor needs to be added to the toolkit...    
from enthought.traits.ui.wx.history_editor \
    import HistoryEditor
    
# fixme: The ImageEditor needs to be added to the toolkit...    
from enthought.traits.ui.wx.extra.image_editor \
    import ImageEditor
    
from enthought.pyface.api \
    import ImageResource
    
from helper \
    import commatize
    
from toolkit \
    import toolkit
    
#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Maximum text file size to process:
MAX_SIZE = 16 * 1024 * 1024
    
#-------------------------------------------------------------------------------
#  'IFileDialogModel' interface:
#-------------------------------------------------------------------------------

class IFileDialogModel ( Interface ):
    """ Defines a model extension to a file dialog.
    """
    
    # The name of the currently selected file:
    file_name = File
    
#-------------------------------------------------------------------------------
#  'IFileDialogView' interface:  
#-------------------------------------------------------------------------------
        
class IFileDialogView ( Interface ):
    """ Defines a visual extension to a file dialog.
    """
    
    # The view to display:
    view = AView
    
    # Is the view fixed or variable width?
    is_fixed = Bool
    
#-------------------------------------------------------------------------------
#  'IFileDialogExtension' interface:
#-------------------------------------------------------------------------------

class IFileDialogExtension ( IFileDialogModel, IFileDialogView ):
    """ Defines a (convenience) union of the IFileDialogModel and
        IFileDialogView interfaces.
    """
    
#-------------------------------------------------------------------------------
#  'MFileDialogModel' mix-in class:  
#-------------------------------------------------------------------------------
        
class MFileDialogModel ( HasPrivateTraits ):
    
    implements( IFileDialogModel )
    
    # The name of the currently selected file:
    file_name = File
    
#-------------------------------------------------------------------------------
#  'MFileDialogView' mix-in class:
#-------------------------------------------------------------------------------
        
class MFileDialogView ( HasPrivateTraits ):
    """ Defines a visual extension to a file dialog.
    """
    
    # The view to display:
    view = AView
    
    # Is the view fixed or variable width?
    is_fixed = Bool( False )
    
# Create a default implementation:
default_view = MFileDialogView()
    
#-------------------------------------------------------------------------------
#  'MFileDialogExtension' mix-in class:
#-------------------------------------------------------------------------------

class MFileDialogExtension ( MFileDialogModel, MFileDialogView ):
    """ Defines a (convenience) union of the MFileDialogModel and
        MFileDialogView mix-in classes.
    """
    
#-------------------------------------------------------------------------------
#  'FileInfo' class:
#-------------------------------------------------------------------------------

class FileInfo ( MFileDialogModel ):
    """ Defines a file dialog extension that display various file information.
    """
    
    # The size of the file:
    size = Property( depends_on = 'file_name' )
    
    # Last file access time:
    atime = Property( depends_on = 'file_name' )
    
    # List file modification time:
    mtime = Property( depends_on = 'file_name' )
    
    # File creation time (or last metadata change time):
    ctime = Property( depends_on = 'file_name' )
    
    #-- Traits View Definitions ------------------------------------------------
    
    view = View(
        VGroup( 
            Item( 'size',  label = 'File size',     style = 'readonly' ), 
            Item( 'atime', label = 'Last access',   style = 'readonly' ),
            Item( 'mtime', label = 'Last modified', style = 'readonly' ),
            Item( 'ctime', label = 'Created at',    style = 'readonly' ),
            label       = 'File Information',
            show_border = True
        )
    )
    
    #-- Property Implementations -----------------------------------------------
    
    @cached_property
    def _get_size ( self ):
        try:
            return commatize( getsize( self.file_name ) ) + ' bytes'
        except:
            return ''
    
    @cached_property
    def _get_atime ( self ):
        try:
            return strftime( '%m/%d/%Y %I:%M:%S %p', 
                             localtime( getatime( self.file_name ) ) )
        except:
            return ''
        
    @cached_property
    def _get_mtime ( self ):
        try:
            return strftime( '%m/%d/%Y %I:%M:%S %p', 
                             localtime( getmtime( self.file_name ) ) )
        except:
            return ''
        
    @cached_property
    def _get_ctime ( self ):
        try:
            return strftime( '%m/%d/%Y %I:%M:%S %p', 
                             localtime( getctime( self.file_name ) ) )
        except:
            return ''
            
#-------------------------------------------------------------------------------
#  'TextInfo' class:
#-------------------------------------------------------------------------------

class TextInfo ( MFileDialogModel ):
    """ Defines a file dialog extension that displays a file's contents as text.
    """
    
    # The file's text content:
    text = Property( depends_on = 'file_name' )
    
    #-- Traits View Definitions ------------------------------------------------
    
    view = View(
        Item( 'text',
              style      = 'readonly',
              show_label = False,
              editor     = CodeEditor()
        )
    )
    
    #-- Property Implementations -----------------------------------------------
    
    @cached_property
    def _get_text ( self ):
        try:
            if getsize( self.file_name ) > MAX_SIZE:
                return 'File too big...'
                
            fh   = file( self.file_name, 'rb' )
            data = fh.read()
            fh.close()
        except:
            return ''
            
        if (data.find( '\x00' ) >= 0) or (data.find( '\xFF' ) >= 0):
            return 'File contains binary data...'
            
        return data
        
#-------------------------------------------------------------------------------
#  'ImageInfo' class:
#-------------------------------------------------------------------------------

class ImageInfo ( MFileDialogModel ):
    """ Defines a file dialog extension that display an image file's dimensions
        and content.
    """
    
    # The ImageResource object for the current file:
    image = Property( depends_on = 'file_name' )
    
    # The width of the current image:
    width = Property( depends_on = 'image' )
    
    # The height of the current image:
    height = Property( depends_on = 'image' )
    
    #-- Traits View Definitions ------------------------------------------------
    
    view = View(
        VGroup(
            VGroup(
                Item( 'width',  style = 'readonly' ),
                Item( 'height', style = 'readonly' ),
                label       = 'Image Dimensions',
                show_border = True
            ),
            VGroup(
                Item( 'image', 
                      show_label = False,
                      editor     = ImageEditor()
                ),
                label       = 'Image',
                show_border = True,
                springy     = True
            )
        )
    )
    
    #-- Property Implementations -----------------------------------------------
    
    @cached_property
    def _get_image ( self ):
        path, name = split( self.file_name )
        if path == '':
            image = ImageResource( 'unknown' )
        else:
            image = ImageResource( name, search_path = [ path ] )
        self._cur_image = image.create_image()
        return image
        
    @cached_property
    def _get_width ( self ):
        try:
            return str( toolkit().image_size( self._cur_image )[0] ) + ' pixels'
        except:
            return '---'
        
    @cached_property
    def _get_height ( self ):
        try:
            return str( toolkit().image_size( self._cur_image )[1] ) + ' pixels'
        except:
            return '---'
        
#-------------------------------------------------------------------------------
#  'OpenFileDialog' class:
#-------------------------------------------------------------------------------

class OpenFileDialog ( Handler ):
    
    # The starting and current file path:
    file_name = File
    
    # The list of file filters to apply:
    filter = List( Str )
    
    # Number of history entries to allow:
    entries = Int( 10 )
    
    # The file dialog title:
    title = Str( 'Open File' )
    
    # The Traits UI persistence id to use:
    id = Str( 'enthought.traits.ui.file_dialog.OpenFileDialog' )
    
    # An optional file dialog extension:
    extension = Instance( IFileDialogModel )
    
    #-- Private Traits ---------------------------------------------------------
    
    # Is the currently specified file name valid?
    is_valid_file = Property( depends_on = 'file_name' )
    
    # The OK and Cancel buttons:
    ok     = Button( 'OK' )
    cancel = Button( 'Cancel' )
        
    #-- Property Implementations -----------------------------------------------
    
    def _get_is_valid_file ( self ):
        return isfile( self.file_name )
        
    #-- Handler Event Handlers -------------------------------------------------
    
    def object_ok_changed ( self, info ):
        """ Handles the user clicking the OK button.
        """
        info.ui.dispose( True )
        
    def object_cancel_changed ( self, info ):
        """ Handles the user clicking the Cancel button.
        """
        info.ui.dispose( False )
        
    #-- Private Methods --------------------------------------------------------
    
    def trait_view ( self, name = None, view_element = None ):
        """ Returns the file dialog view to use.
        """
        # Set up the default file dialog view and size information:
        item = Item( 'file_name', 
                     style      = 'custom',
                     show_label = False,
                     width      = 0.5,
                     editor     = FileEditor( filter = self.filter ) )
        width = height = 0.20             

        # Check to see if we have an extension being added:
        extension = extension_view = self.extension
        if extension is not None:
            # If there is, sync up the 'file_name' trait with the extension:
            self.sync_trait( 'file_name', extension, mutual = True )
            
            # Check to see if it also defines the optional IFileDialogView
            # interface, and if not, use the default view information:
            if not extension.has_traits_interface( IFileDialogView ):
                extension_view = default_view
            
            # Get the view that the extension wants to use:
            view = extension.trait_view( extension_view.view )

            # fixme: We should use the actual values of the view's Width and            
            # height traits here to adjust the overall width and height...
            width *= 2.0

            # Determine whether to use a splitter or fixed width for the dialog:            
            klass = HSplit
            if extension_view.is_fixed:
                klass = HGroup
            
            # Finally, combine the normal view elements with the extension in
            # a new horizontal group:
            item = klass( item, 
                          Item( 'extension',
                                style      = 'custom',
                                show_label = False,
                                width      = 0.5,
                                editor     = InstanceEditor( view = view,
                                                             id = 'extension' )
                          ),
                          id = 'splitter' )
            
        # Return the resulting view:
        return View(
            VGroup(
                VGroup( item ),
                HGroup(
                    Item( 'file_name',
                          id      = 'history',
                          editor  = HistoryEditor( entries  = self.entries,
                                                   auto_set = True ),
                          springy = True
                    ),
                    Item( 'ok',
                          show_label   = False,
                          enabled_when = 'is_valid_file'
                    ),
                    Item( 'cancel',
                          show_label = False
                    )
                )
            ),
            title     = self.title,
            id        = self.id,
            kind      = 'livemodal',
            width     = width,
            height    = height,
            resizable = True
        )
        
#-------------------------------------------------------------------------------
#  Returns a file name to open or None if the user cancelled the operation:  
#-------------------------------------------------------------------------------

def open_file ( **traits ):
    fd = OpenFileDialog( **traits )
    if fd.edit_traits().result:
        return fd.file_name
        
    return None
    
#-- Test Case ------------------------------------------------------------------

if __name__ == '__main__':
    print open_file( extension = ImageInfo() )

