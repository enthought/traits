#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
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

from __future__ import absolute_import

from os import R_OK, W_OK, access, mkdir

from os.path import (basename, dirname, exists, getatime, getctime, getmtime,
    getsize, isdir, isfile, join, split, splitext)

from time import localtime, strftime

from ..api import (Bool, Button, CList, Event, File, HasPrivateTraits,
    Instance, Int, Interface, Property, Str, cached_property, implements)

from ..trait_base import user_name_for

from .api import (CodeEditor, FileEditor, HGroup, HSplit, Handler, HistoryEditor,
    ImageEditor, InstanceEditor, Item, UIInfo, VGroup, VSplit, View, spring)

from .ui_traits import AView

from ...pyface.api import ImageResource

from ...pyface.timer.api import do_later

from .helper import commatize

from .toolkit import toolkit

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
        if splitext( name )[1] in ( '.png', '.gif', '.jpg', '.jpeg' ):
            image = ImageResource( name, search_path = [ path ] )
        else:
            image = ImageResource( 'unknown' )
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
#  'CreateDirHandler' class:
#-------------------------------------------------------------------------------

class CreateDirHandler ( Handler ):
    """ Controller for the 'create new directory' popup.
    """

    # The name for the new directory to be created:
    dir_name = Str

    # The current status message:
    message = Str

    # The OK and Cancel buttons:
    ok     = Button( 'OK' )
    cancel = Button( 'Cancel' )

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        VGroup(
            HGroup(
                 Item( 'handler.dir_name',
                       label = 'Name'
                 ),
                 Item( 'handler.ok',
                       show_label   = False,
                       enabled_when = "handler.dir_name.strip() != ''"
                 ),
                 Item( 'handler.cancel',
                       show_label = False
                 ),
            ),
            HGroup(
                Item( 'handler.message',
                      show_label = False,
                      style      = 'readonly',
                      springy    = True
                ),
                show_border = True
            )
        ),
        kind = 'popup'
    )

    #-- Handler Event Handlers -------------------------------------------------

    def handler_ok_changed ( self, info ):
        """ Handles the user clicking the OK button.
        """
        dir = info.object.file_name
        if not isdir( dir ):
            dir = dirname( dir )

        path = join( dir, self.dir_name )
        try:
            # Try to create the requested directory:
            mkdir( path )

            # Force the file tree view to be refreshed:
            info.object.reload    = True

            # set the new directory as the currently selected file name:
            info.object.file_name = path

            # Close this view:
            info.ui.dispose( True )
        except:
            self.message = "Could not create the '%s' directory" % self.dir_name

    def handler_cancel_changed ( self, info ):
        """ Handles the user clicking the Cancel button.
        """
        info.ui.dispose( False )

#-------------------------------------------------------------------------------
#  'FileExistsHandler' class:
#-------------------------------------------------------------------------------

class FileExistsHandler ( Handler ):
    """ Controller for the 'file already exists' popup.
    """
    # The current status message:
    message = Str

    # The OK and Cancel buttons:
    ok     = Button( 'OK' )
    cancel = Button( 'Cancel' )

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        VGroup(
            HGroup(
                 Item( 'handler.message',
                       editor = ImageEditor( image = '@icons:dialog-warning' )
                 ),
                 Item( 'handler.message', style = 'readonly' ),
                 show_labels = False
            ),
            HGroup(
                 spring,
                 Item( 'handler.ok' ),
                 Item( 'handler.cancel' ),
                 show_labels = False
            )
        ),
        kind = 'popup'
    )

    #-- Handler Event Handlers -------------------------------------------------

    def handler_ok_changed ( self, info ):
        """ Handles the user clicking the OK button.
        """
        parent = info.ui.parent
        info.ui.dispose( True )
        parent.dispose( True )

    def handler_cancel_changed ( self, info ):
        """ Handles the user clicking the Cancel button.
        """
        info.ui.dispose( False )

#-------------------------------------------------------------------------------
#  'OpenFileDialog' class:
#-------------------------------------------------------------------------------

class OpenFileDialog ( Handler ):
    """ Defines the model and handler for the open file dialog.
    """

    # The starting and current file path:
    file_name = File

    # The list of file filters to apply:
    filter = CList( Str )

    # Number of history entries to allow:
    entries = Int( 10 )

    # The file dialog title:
    title = Str( 'Open File' )

    # The Traits UI persistence id to use:
    id = Str( 'enthought.traits.ui.file_dialog.OpenFileDialog' )

    # A list of optional file dialog extensions:
    extensions = CList( IFileDialogModel )

    #-- Private Traits ---------------------------------------------------------

    # The UIInfo object for the view:
    info = Instance( UIInfo )

    # Event fired when the file tree view should be reloaded:
    reload = Event

    # Event fired when the user double-clicks on a file name:
    dclick = Event

    # Allow extension models to be added dynamically:
    extension__ = Instance( IFileDialogModel )

    # Is the file dialog for saving a file (or opening a file)?
    is_save_file = Bool( False )

    # Is the currently specified file name valid?
    is_valid_file = Property( depends_on = 'file_name' )

    # Can a directory be created now?
    can_create_dir = Property( depends_on = 'file_name' )

    # The OK, Cancel and create directory buttons:
    ok      = Button( 'OK' )
    cancel  = Button( 'Cancel' )
    create  = Button( image = '@icons:folder-new',
                      style = 'toolbar' )

    #-- Handler Class Method Overrides -----------------------------------------

    def init_info ( self, info ):
        """ Handles the UIInfo object being initialized during view start-up.
        """
        self.info = info

    #-- Property Implementations -----------------------------------------------

    def _get_is_valid_file ( self ):
        if self.is_save_file:
            return (isfile( self.file_name ) or (not exists( self.file_name )))

        return isfile( self.file_name )

    def _get_can_create_dir ( self ):
        dir = dirname( self.file_name )
        return (isdir( dir ) and access( dir, R_OK | W_OK ))

    #-- Handler Event Handlers -------------------------------------------------

    def object_ok_changed ( self, info ):
        """ Handles the user clicking the OK button.
        """
        if self.is_save_file and exists( self.file_name ):
            do_later( self._file_already_exists )
        else:
            info.ui.dispose( True )

    def object_cancel_changed ( self, info ):
        """ Handles the user clicking the Cancel button.
        """
        info.ui.dispose( False )

    def object_create_changed ( self, info ):
        """ Handles the user clicking the create directory button.
        """
        if not isdir( self.file_name ):
            self.file_name = dirname( self.file_name )

        CreateDirHandler().edit_traits( context = self,
                                        parent  = info.create.control )

    #-- Traits Event Handlers --------------------------------------------------

    def _dclick_changed ( self ):
        """ Handles the user double-clicking a file name in the file tree view.
        """
        if self.is_valid_file:
            self.object_ok_changed( self.info )

    #-- Private Methods --------------------------------------------------------

    def open_file_view ( self ):
        """ Returns the file dialog view to use.
        """
        # Set up the default file dialog view and size information:
        item = Item( 'file_name',
                     id         = 'file_tree',
                     style      = 'custom',
                     show_label = False,
                     width      = 0.5,
                     editor     = FileEditor( filter      = self.filter,
                                              allow_dir   = True,
                                              reload_name = 'reload',
                                              dclick_name = 'dclick' ) )
        width = height = 0.20

        # Check to see if we have any extensions being added:
        if len( self.extensions ) > 0:

            # fixme: We should use the actual values of the view's Width and
            # height traits here to adjust the overall width and height...
            width *= 2.0

            # Assume we can used a fixed width Group:
            klass = HGroup

            # Set up to build a list of view Item objects:
            items = []

            # Add each extension to the dialog:
            for i, extension in enumerate( self.extensions ):

                # Save the extension in a new trait (for use by the View):
                name = 'extension_%d' % i
                setattr( self, name, extension )

                extension_view = extension

                # Sync up the 'file_name' trait with the extension:
                self.sync_trait( 'file_name', extension, mutual = True )

                # Check to see if it also defines the optional IFileDialogView
                # interface, and if not, use the default view information:
                if not extension.has_traits_interface( IFileDialogView ):
                    extension_view = default_view

                # Get the view that the extension wants to use:
                view = extension.trait_view( extension_view.view )

                # Determine if we should use a splitter for the dialog:
                if not extension_view.is_fixed:
                    klass = HSplit

                # Add the extension as a new view item:
                items.append(
                    Item( name,
                          label = user_name_for( extension.__class__.__name__ ),
                          show_label = False,
                          style      = 'custom',
                          width      = 0.5,
                          height     = 0.5,
                          dock       = 'horizontal',
                          resizable  = True,
                          editor     = InstanceEditor( view = view, id = name )
                    ) )

            # Finally, combine the normal view element with the extensions:
            item = klass( item,
                          VSplit( id = 'splitter2', springy = True, *items ),
                          id = 'splitter' )
        # Return the resulting view:
        return View(
            VGroup(
                VGroup( item ),
                HGroup(
                    Item( 'create',
                          id           = 'create',
                          show_label   = False,
                          style        = 'custom',
                          defined_when = 'is_save_file',
                          enabled_when = 'can_create_dir',
                          tooltip      = 'Create a new directory'
                    ),
                    Item( 'file_name',
                          id      = 'history',
                          editor  = HistoryEditor( entries  = self.entries,
                                                   auto_set = True ),
                          springy = True
                    ),
                    Item( 'ok',
                          id           = 'ok',
                          show_label   = False,
                          enabled_when = 'is_valid_file'
                    ),
                    Item( 'cancel',
                          show_label = False
                    )
                )
            ),
            title        = self.title,
            id           = self.id,
            kind         = 'livemodal',
            width        = width,
            height       = height,
            close_result = False,
            resizable    = True
        )

    def _file_already_exists ( self ):
        """ Handles prompting the user when the selected file already exists,
            and the dialog is a 'save file' dialog.
        """
        FileExistsHandler( message = ("The file '%s' already exists.\nDo "
                                      "you wish to overwrite it?") %
                                      basename( self.file_name )
            ).edit_traits( context = self,
                           parent  = self.info.ok.control ).set(
                           parent  = self.info.ui )

#-------------------------------------------------------------------------------
#  Returns a file name to open or an empty string if the user cancels the
#  operation:
#-------------------------------------------------------------------------------

def open_file ( **traits ):
    """ Returns a file name to open or an empty string if the user cancels the
        operation.
    """
    fd = OpenFileDialog( **traits )
    if fd.edit_traits( view = 'open_file_view' ).result:
        return fd.file_name

    return ''

def save_file ( **traits ):
    """ Returns a file name to save to or an empty string if the user cancels
        the operation. In the case where the file selected already exists, the
        user will be prompted if they want to overwrite the file before the
        selected file name is returned.
    """
    traits.setdefault( 'title', 'Save File' )
    traits[ 'is_save_file' ] = True
    fd = OpenFileDialog( **traits )
    if fd.edit_traits( view = 'open_file_view' ).result:
        return fd.file_name

    return ''

#-- Test Case ------------------------------------------------------------------

if __name__ == '__main__':
    print save_file( extensions = [ FileInfo(), TextInfo(), ImageInfo() ],
                     filter = 'Python file (*.py)|*.py' )

