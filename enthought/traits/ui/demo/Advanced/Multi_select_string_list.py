"""
A demo showing how to use a TabularEditor to create a multi-select list box.
"""

from enthought.traits.api \
    import HasPrivateTraits, List, Str, Property
    
from enthought.traits.ui.api \
    import View, HGroup, Item
    
from enthought.traits.ui.wx.extra.tabular_editor \
    import TabularEditor, TabularAdapter

class MultiSelectAdapter ( TabularAdapter ):

    columns = [ ( 'Value', 'value' ) ]

    value_text = Property

    def _get_value_text ( self ):
        return self.item
        
class MultiSelect ( HasPrivateTraits ):
    
    choices  = List( Str )
    selected = List( Str )
    
    view = View(
        HGroup(
            Item( 'choices',
                  show_label = False,
                  editor     = TabularEditor(
                                   show_titles  = False,
                                   selected     = 'selected',
                                   editable     = False,
                                   multi_select = True,
                                   adapter      = MultiSelectAdapter() )
            ),
            Item( 'selected',
                  show_label = False,
                  editor     = TabularEditor(
                                   show_titles  = False,
                                   editable     = False,
                                   adapter      = MultiSelectAdapter() )
            )
        )
    )
    
# Create the demo:
demo = MultiSelect( choices = [ 'one', 'two', 'three', 'four', 'five', 'six', 
                                'seven', 'eight', 'nine', 'ten' ] )

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
    
