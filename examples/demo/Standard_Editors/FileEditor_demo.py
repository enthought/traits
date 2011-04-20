#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Implementation of a FileEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the FileEditor
"""

# Imports:
from traits.api \
    import HasTraits, File

from traitsui.api \
    import Item, Group, View

# Define the demo class:
class FileEditorDemo ( HasTraits ):
    """ Defines the main FileEditor demo class. """

    # Define a File trait to view:
    file_name = File

    # Display specification (one Item per editor style):
    file_group = Group(
        Item( 'file_name', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'file_name', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'file_name', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'file_name', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view:
    view = View(
        file_group,
        title     = 'FileEditor',
        buttons   = ['OK'],
        resizable = True
    )

# Create the demo:
demo = FileEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
