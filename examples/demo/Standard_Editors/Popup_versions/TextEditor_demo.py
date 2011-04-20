"""
Implementation of a TextEditor demo plugin for the Traits UI demo program.

For each of three data types for which TextEditor is used, this demo shows
each of the four styles of the TextEditor.
"""

from traits.api import HasTraits, Str, Int, Password
from traitsui.api import Item, Group, View

#-------------------------------------------------------------------------------
#  Demo Class
#-------------------------------------------------------------------------------

class TextEditorDemo ( HasTraits ):
    """ This class specifies the details of the TextEditor demo.
    """

    # Define a trait for each of three variants
    string_trait     = Str( "sample string" )
    int_trait        = Int( 1 )
    password         = Password


    # TextEditor display without multi-line capability (for various traits):
    text_int_group = Group( Item('int_trait', style='simple', label='Simple'),
                            Item('_'),
                            Item('int_trait', style='custom', label='Custom'),
                            Item('_'),
                            Item('int_trait', style='text', label='Text'),
                            Item('_'),
                            Item('int_trait', style='readonly', label='ReadOnly'),
                            label='Integer' )

    # TextEditor display with multi-line capability (for various traits):
    text_str_group = Group( Item('string_trait',
                                  style='simple',
                                  label='Simple'),
                            Item('_'),
                            Item('string_trait',
                                  style='custom',
                                  label='Custom'),
                            Item('_'),
                            Item('string_trait',
                                  style='text',
                                  label='Text'),
                            Item('_'),
                            Item('string_trait',
                                  style='readonly',
                                  label='ReadOnly'),
                            label='String' )

    # TextEditor display with secret typing capability (for Password traits):
    text_pass_group = Group( Item('password', style='simple', label='Simple'),
                             Item('_'),
                             Item('password', style='custom', label='Custom'),
                             Item('_'),
                             Item('password', style='text', label='Text'),
                             Item('_'),
                             Item('password', style='readonly', label='ReadOnly'),
                             label='Password' )


    # The view includes one group per data type.  These will be displayed
    # on separate tabbed panels.
    view1 = View(text_int_group,
                 text_str_group,
                 text_pass_group,
                 title = 'TextEditor',
                 buttons = ['OK'])


# Create the demo:
popup = TextEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

