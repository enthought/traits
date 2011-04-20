#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Implementation of a CodeEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the CodeEditor
"""

# Imports:
from traits.api \
    import HasTraits, Code

from traitsui.api \
    import Item, Group, View

# The main demo class:
class CodeEditorDemo ( HasTraits ):
    """ Defines the CodeEditor demo class.
    """

    # Define a trait to view:
    code_sample = Code( 'import sys\n\nsys.print("hello world!")' )

    # Display specification:
    code_group = Group(
        Item( 'code_sample', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'code_sample', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'code_sample', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'code_sample', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view:
    view = View(
        code_group,
        title   = 'CodeEditor',
        buttons = [ 'OK' ] )


# Create the demo:
demo = CodeEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == "__main__":
    demo.configure_traits()
