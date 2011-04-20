#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
This demo shows a combination of the <b>DirectoryEditor</b>, the
<b>TabularEditor</b> and the <b>CodeEditor</b> used to create a simple Python
source browser:

 - Use the <b>DirectoryEditor</b> on the left to navigate to and select
   directories containing Python source files.
 - Use the <b>TabularEditor</b> on the top-right to view information about and
   to select Python source files in the currently selected directory.
 - View the currently selected Python source file's contents in the
   <b>CodeEditor</b> in the bottom-right.

As an extra <i>feature</i>, the <b>TabularEditor</b> also displays a:

 - Red ball if the file size > 64KB.
 - Blue ball if the file size > 16KB.
"""

import traits
import traitsui

from time \
    import localtime, strftime

from os \
    import listdir

from os.path \
    import getsize, getmtime, isfile, join, splitext, basename, dirname

from traits.api \
    import HasPrivateTraits, Str, Float, List, Directory, File, Code, \
           Instance, Property, cached_property

from traitsui.api \
    import View, Item, HSplit, VSplit, TabularEditor

from traitsui.tabular_adapter \
    import TabularAdapter

from pyface.image_resource \
    import ImageResource

#-- Constants ------------------------------------------------------------------

# Necessary because of the dynamic way in which the demos are loaded:
search_path = [ join( dirname( traits.api.__file__ ),
                      '..', '..', 'examples', 'demo', 'Applications' ) ]

#-- FileInfo Class Definition --------------------------------------------------

class FileInfo ( HasPrivateTraits ):

    file_name = File
    name      = Property
    size      = Property
    time      = Property
    date      = Property

    @cached_property
    def _get_name ( self ):
        return basename( self.file_name )

    @cached_property
    def _get_size ( self ):
        return getsize( self.file_name )

    @cached_property
    def _get_time ( self ):
        return strftime( '%I:%M:%S %p',
                         localtime( getmtime( self.file_name ) ) )

    @cached_property
    def _get_date ( self ):
        return strftime( '%m/%d/%Y',
                         localtime( getmtime( self.file_name ) ) )

#-- Tabular Adapter Definition -------------------------------------------------

class FileInfoAdapter ( TabularAdapter ):

    columns = [ ( 'File Name', 'name' ),
                ( 'Size',      'size' ),
                ( '',          'big'  ),
                ( 'Time',      'time' ),
                ( 'Date',      'date' ) ]

    even_bg_color  = ( 201, 223, 241 )
    font           = 'Courier 10'
    size_alignment = Str( 'right' )
    time_alignment = Str( 'right' )
    date_alignment = Str( 'right' )
    big_text       = Str
    big_width      = Float( 18 )
    big_image      = Property

    def _get_big_image ( self ):
        size = self.item.size
        if size > 65536:
            return 'red_ball'

        return ( None, 'blue_ball' )[ size > 16384 ]

#-- Tabular Editor Definition --------------------------------------------------

tabular_editor = TabularEditor(
    editable   = False,
    selected   = 'file_info',
    adapter    = FileInfoAdapter(),
    operations = [],
    images     = [ ImageResource( 'blue_ball', search_path = search_path ),
                   ImageResource( 'red_ball',  search_path = search_path ) ]
)

#-- PythonBrowser Class Definition ---------------------------------------------

class PythonBrowser ( HasPrivateTraits ):

    #-- Trait Definitions ------------------------------------------------------

    dir       = Directory
    files     = List( FileInfo )
    file_info = Instance( FileInfo )
    code      = Code

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        HSplit(
            Item( 'dir', style = 'custom' ),
            VSplit(
                Item( 'files', editor = tabular_editor ),
                Item( 'code',  style = 'readonly' ),
                show_labels = False ),
            show_labels = False
        ),
        resizable = True,
        width     = 0.75,
        height    = 0.75
    )

    #-- Event Handlers ---------------------------------------------------------

    def _dir_changed ( self, dir ):
        self.files = [ FileInfo( file_name = join( dir, name ) )
                       for name in listdir( dir )
                       if ((splitext( name )[1] == '.py') and
                           isfile( join( dir, name ) )) ]

    def _file_info_changed ( self, file_info ):
        fh = None
        try:
            fh = open( file_info.file_name, 'rb' )
            self.code = fh.read()
        except:
            pass

        if fh is not None:
            fh.close()

# Create the demo:
demo = PythonBrowser( dir = dirname( traits.api.__file__ ) )

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
