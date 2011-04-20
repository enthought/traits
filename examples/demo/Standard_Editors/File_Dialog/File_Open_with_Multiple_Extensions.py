"""
This demonstrates using the Traits file dialog with multiple file dialog
extensions, in this case, the <b>FileInfo</b>, <b>TextInfo</b> and
<b>ImageInfo</b> extensions.

For more information about why you would want to use the Traits file dialog
over the standard OS file dialog, select the <b>File Open</b> demo. For a
demonstration of writing a custom file dialog extension, select the
<b>File Open with Custom Extension</b> demo.

Suggestion: Try resizing the dialog and dragging the various file dialog
extensions around to create a better arrangement than the rather cramped
default vertical arrangement. Close the dialog, then re-open it to see that
your new arrangement has been correctly restored. Try a different file dialog
demo to verify that the customizations are not affected by any of the other
demos because this demo specifies a custom id when invoking the file dialog.
"""

#-- Imports --------------------------------------------------------------------

from traits.api \
    import HasTraits, File, Button

from traitsui.api \
    import View, HGroup, Item

from traitsui.file_dialog  \
    import open_file, FileInfo, TextInfo, ImageInfo

#-- FileDialogDemo Class -------------------------------------------------------

# Demo specific file dialig id:
demo_id = 'traitsui.demo.standard_editors.file_dialog.multiple_info'

# The list of file dialog extensions to use:
extensions = [ FileInfo(), TextInfo(), ImageInfo() ]

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
        file_name = open_file( extensions = extensions, id = demo_id )
        if file_name != '':
            self.file_name = file_name

# Create the demo:
demo = FileDialogDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

