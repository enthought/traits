"""
Implementation of a FileEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the FileEditor.
"""

from traits.api import HasTraits, File
from traitsui.api import Item, Group, View

#-------------------------------------------------------------------------------
#  Demo Class
#-------------------------------------------------------------------------------

class FileEditorDemo ( HasTraits ):
    """ This class specifies the details of the FileEditor demo.
    """

    # To demonstrate any given Trait editor, an appropriate Trait is required.
    file_name = File


    # Display specification (one Item per editor style)
    file_group = Group( Item('file_name', style = 'simple', label = 'Simple'),
                        Item('_'),
                        Item('file_name', style = 'custom', label = 'Custom'),
                        Item('_'),
                        Item('file_name', style = 'text', label = 'Text'),
                        Item('_'),
                        Item('file_name', style = 'readonly', label = 'ReadOnly'))

    # Demo view
    view1 = View( file_group,
                  title = 'FileEditor',
                  width = 400,
                  buttons = ['OK'] )


# Create the demo:
popup = FileEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

