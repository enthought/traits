"""
This demonstrates using the Traits file dialog with a custom written file
dialog extension, in this case an extension called <b>LineCountInfo</b>, which
displays the number of text lines in the currently selected file.

For more information about why you would want to use the Traits file dialog
over the standard OS file dialog, select the <b>File Open</b> demo.
"""

#-- Imports --------------------------------------------------------------------

from os.path \
    import getsize

from traits.api \
    import HasTraits, File, Button, Property, cached_property

from traitsui.api \
    import View, VGroup, HGroup, Item

from traitsui.file_dialog  \
    import open_file, MFileDialogModel

from traitsui.helper \
    import commatize

#-- LineCountInfo Class --------------------------------------------------------

class LineCountInfo ( MFileDialogModel ):
    """ Defines a file dialog extension that displays the number of text lines
        in the currently selected file.
    """

    # The number of text lines in the currently selected file:
    lines = Property( depends_on = 'file_name' )

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        VGroup(
            Item( 'lines', style = 'readonly' ),
            label       = 'Line Count Info',
            show_border = True
        )
    )

    #-- Property Implementations -----------------------------------------------

    @cached_property
    def _get_lines ( self ):
        try:
            if getsize( self.file_name ) > 10000000:
                return 'File too big...'

            fh   = file( self.file_name, 'rb' )
            data = fh.read()
            fh.close()
        except:
            return ''

        if (data.find( '\x00' ) >= 0) or (data.find( '\xFF' ) >= 0):
            return 'File contains binary data...'

        return ('%s lines' % commatize( len( data.splitlines() ) ))

#-- FileDialogDemo Class -------------------------------------------------------

# Demo specific file dialig id:
demo_id = ('traitsui.demo.standard_editors.file_dialog.'
           'line_count_info')

class FileDialogDemo ( HasTraits ):

    # The name of the selected file:
    file_name = File

    # The button used to display the file dialog:
    open = Button( 'Open...' )

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        HGroup(
            Item( 'open', show_label = False ),
            '_',
            Item( 'file_name', style = 'readonly', springy = True )
        ),
        width = 0.5
    )

    #-- Traits Event Handlers --------------------------------------------------

    def _open_changed ( self ):
        """ Handles the user clicking the 'Open...' button.
        """
        file_name = open_file( extensions = LineCountInfo(), id = demo_id )
        if file_name != '':
            self.file_name = file_name

# Create the demo:
demo = FileDialogDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

