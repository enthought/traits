#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Implementation of a DirectoryEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the DirectoryEditor
"""

# Imports:
from traits.api \
    import HasTraits, Directory

from traitsui.api \
    import Item, Group, View

# Define the demo class:
class DirectoryEditorDemo ( HasTraits ):
    """ Define the main DirectoryEditor demo class. """

    # Define a Directory trait to view:
    dir_name = Directory


    # Display specification (one Item per editor style):
    dir_group = Group(
        Item( 'dir_name', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'dir_name', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'dir_name', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'dir_name', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view:
    view = View(
        dir_group,
        title     = 'DirectoryEditor',
        buttons   = ['OK'],
        resizable = True
    )

# Create the demo:
demo = DirectoryEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

