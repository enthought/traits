"""
This demonstrates one of the simplest cases of using the Traits file dialog to
select a file for opening (i.e. reading or editing).

The first question of course is why use the Traits file dialog at all, when the
standard OS file dialog is also available?

And the answer is that you can use either, but the advantages of using the
Traits file dialog are:

 - It supports history. That is, each time the user selects a file for opening,
   the file is added to a persistent history list, similar to many applications
   <i>Open recent...</i> function, but built directly into the file dialog.
   The amount of history remembered can be specified by the developer, with the
   default being the last 10 files opened.

 - It is resizable. Some standard OS file dialogs are not resizable, which can
   be very annoying to the user trying to select a file through a tiny
   peephole view of the file system. In addition, if the user resizes the
   dialog, the new size and position will be persisted, so that the file dialog
   will appear in the same location the next time the user wants to open a
   file.

 - There is a very nice synergy between the file system view and the history
   list. Quite often users shuttle between several <i>favorite</i> locations
   in the file system when opening files. The Traits file dialog automatically
   discovers these favorite locations just by the user opening files. When a
   user opens the file dialog, they can select a previously opened file from
   the history list, which then automatically causes the file system view to
   expand the selected file's containing folder, thus allowing them to select a
   different file in the same location. Since the history list is updated each
   time a user selects a file, It tends to automatically discover a <i>working
   set</i> of favorite directories just through simple use, without the user
   having to explicitly designate them as such.

 - It's customizable. The Traits file dialog accepts extension objects which
   can be used to display additional file information or even modify the
   selection behavior of the dialog. Several extensions are provided with
   Traits (and are demonstrated in some of the other examples), and you are
   free to write your own by implementing a very simple interface.

 - The history and user settings are customizable per application. Just by
   setting a unique id in the file dialog request, you can specify that the
   history and window size and position information are specific to your
   application. If you have file dialog extensions added, the user can
   reorder, resize and reconfigure the overall file dialog layout, including
   your extensions, and have their custom settings restored each time they use
   the file dialog. If you do not specify a unique id, then the history and
   user settings default to the system-wide settings for the file dialog. It's
   your choice.

 - It's easy to use. That's what this particular example is all about. So take
   a look at the source code for this example to see how easy it is...
"""

#-- Imports --------------------------------------------------------------------

from traits.api \
    import HasTraits, File, Button

from traitsui.api \
    import View, HGroup, Item

from traitsui.file_dialog  \
    import open_file

#-- FileDialogDemo Class -------------------------------------------------------

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
        file_name = open_file()
        if file_name != '':
            self.file_name = file_name

# Create the demo:
demo = FileDialogDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

