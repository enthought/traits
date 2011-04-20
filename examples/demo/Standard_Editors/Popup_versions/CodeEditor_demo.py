"""
Implementation of a CodeEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the CodeEditor.
"""

from traits.api import HasTraits, Code
from traitsui.api import Item, Group, View

#-------------------------------------------------------------------------------
#  Demo Class
#-------------------------------------------------------------------------------

class CodeEditorDemo ( HasTraits ):
    """ This class specifies the details of the CodeEditor demo.
    """

    # To demonstrate any given Trait editor, an appropriate Trait is required.
    code_sample = Code( 'import sys\n\nsys.print("hello world!")' )

    # Display specification
    code_group = Group( Item('code_sample', style='simple', label='Simple'),
                        Item('_'),
                        Item('code_sample', style='custom', label='Custom'),
                        Item('_'),
                        Item('code_sample', style='text', label='Text'),
                        Item('_'),
                        Item('code_sample', style='readonly', label='ReadOnly'))

    # Demo view
    view1 = View( code_group,
                  title = 'CodeEditor',
                  width = 350,
                  buttons = ['OK'] )


# Create the demo:
popup = CodeEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

