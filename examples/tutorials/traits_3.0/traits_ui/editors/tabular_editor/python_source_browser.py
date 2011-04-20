#--(Python Source Browser Example)----------------------------------------------
"""
This lesson shows a combination of the **DirectoryEditor**, the
**TabularEditor** and the **CodeEditor** used together to create a very simple
Python source browser. In the **Demo** tab you can:

- Use the **DirectoryEditor** on the left to navigate to and select
  directories containing Python source files.
- Use the **TabularEditor** on the top-right to view information about and
  to select Python source files in the currently selected directory.
- View the currently selected Python source file's contents in the
  **CodeEditor** in the bottom-right.

As an extra *feature*, the **TabularEditor** also displays a:

- Red ball if the file size > 64KB.
- Blue ball if the file size > 16KB.

As with the *Single and Married Person Example* tutorial, this example shows you
how to:

- Set up a **TabularEditor**.
- Define a **TabularAdapter** subclass that meets the display requirements of
  the application.

In this example, please note the use of the *even_bg_color* trait in the
**FileInfoAdapter** adapter class to set up alternating line colors in the table
for improved readability.

Also note that the *name*, *size*, *time* and *date* columns define *column_id*
values which correspond directly with traits defined in the **FileInfo** class,
but the *big* column id is an artifical column defined to display the file size
related *blue ball* and *red ball* images when the file size exceeds various
thresholds. The column id is used simply to provide a name reference for the
related trait and property definitions in the adapter class itself.
"""

#--<Imports>--------------------------------------------------------------------

import traits
import traitsui

import wx

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

#--<Constants>------------------------------------------------------------------

# Necessary because of the dynamic way in which the demos are loaded:
search_path = [ join( dirname( traitsui.api.__file__ ),
                      'demo', 'Applications' ) ]

#--[FileInfo Class]-------------------------------------------------------------

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

#--[FileInfoAdapter Class]------------------------------------------------------

class FileInfoAdapter ( TabularAdapter ):

    columns = [ ( 'File Name', 'name' ),
                ( 'Size',      'size' ),
                ( '',          'big'  ),
                ( 'Time',      'time' ),
                ( 'Date',      'date' ) ]

    even_bg_color  = wx.Colour( 201, 223, 241 )
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

#--[Tabular Editor Definition]--------------------------------------------------

tabular_editor = TabularEditor(
    editable   = False,
    selected   = 'file_info',
    adapter    = FileInfoAdapter(),
    operations = [],
    images     = [ ImageResource( 'blue_ball', search_path = search_path ),
                   ImageResource( 'red_ball',  search_path = search_path ) ]
)

#--[PythonBrowser Class]--------------------------------------------------------

class PythonBrowser ( HasPrivateTraits ):

    dir       = Directory
    files     = List( FileInfo )
    file_info = Instance( FileInfo )
    code      = Code

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

#--[Example*]-------------------------------------------------------------------

demo = PythonBrowser( dir = dirname( traits.api.__file__ ) )

