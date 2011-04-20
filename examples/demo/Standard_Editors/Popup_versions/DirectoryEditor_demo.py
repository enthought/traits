"""
Implementation of a DirectoryEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the DirectoryEditor.
"""

from traits.api import HasTraits, Directory
from traitsui.api import Item, Group, View


#-------------------------------------------------------------------------------
#  Demo Class
#-------------------------------------------------------------------------------

class DirectoryEditorDemo ( HasTraits ):
    """ This class specifies the details of the DirectoryEditor demo.
    """

    # To demonstrate any given Trait editor, an appropriate Trait is required.
    dir_name = Directory


    # Display specification (one Item per editor style)
    dir_group = Group( Item('dir_name', style = 'simple', label = 'Simple'),
                       Item('_'),
                       Item('dir_name', style = 'custom', label = 'Custom'),
                       Item('_'),
                       Item('dir_name', style = 'text', label = 'Text'),
                       Item('_'),
                       Item('dir_name', style = 'readonly', label = 'ReadOnly'))

    # Demo view
    view1 = View( dir_group,
                  title = 'DirectoryEditor',
                  width = 400,
                  buttons = ['OK'] )


# Create the demo:
popup = DirectoryEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

