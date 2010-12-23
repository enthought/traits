#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Another demo showing how to use a TabularEditor to create a multi-select list 
box. This demo creates a reusable StringListEditor class and uses that instead 
of defining the editor as part of the demo class.

This approach greatly simplifies the actual demo class and shows how to 
construct a reusable Traits UI-based editor that can be used in other 
applications.
"""

#-- Imports ------------------------------------------------------------------

from enthought.traits.api \
    import HasPrivateTraits, List, Str, Property, on_trait_change
    
from enthought.traits.ui.api \
    import View, HGroup, Item, TabularEditor
    
from enthought.traits.ui.tabular_adapter \
    import TabularAdapter
 
from enthought.traits.ui.ui_editor \
    import UIEditor
    
from enthought.traits.ui.basic_editor_factory \
    import BasicEditorFactory
    
#-- Define the reusable StringListEditor class and its helper classes --------    
    
# Define the tabular adapter used by the Traits UI string list editor:
class MultiSelectAdapter ( TabularAdapter ):

    # The columns in the table (just the string value):
    columns = [ ( 'Value', 'value' ) ]

    # The text property used for the 'value' column:
    value_text = Property

    def _get_value_text ( self ):
        return self.item
    
# Define the actual Traits UI string list editor:        
class _StringListEditor ( UIEditor ):
    
    # Indicate that the editor is scrollable/resizable:
    scrollable = True
    
    # The list of available editor choices:
    choices = List( Str )
    
    # The list of currently selected items:
    selected = List( Str )
    
    # The traits UI view used by the editor:
    view = View(
        Item( 'choices',
              show_label = False,
              editor     = TabularEditor(
                               show_titles  = False,
                               selected     = 'selected',
                               editable     = False,
                               multi_select = True,
                               adapter      = MultiSelectAdapter() )
        ),
        id        = 'string_list_editor',
        resizable = True
    )
    
    def init_ui ( self, parent ):
        
        self.sync_value( self.factory.choices, 'choices', 'from', 
                         is_list = True )
        self.selected = self.value
        
        return self.edit_traits( parent = parent, kind = 'subpanel' )
        
    @on_trait_change( ' selected' )
    def _selected_modified ( self ):
        self.value = self.selected

# Define the StringListEditor class used by client code:        
class StringListEditor ( BasicEditorFactory ):

    # The editor implementation class:
    klass = _StringListEditor

    # The extended trait name containing the editor's set of choices: 
    choices = Str    
        
#-- Define the demo class ----------------------------------------------------

class MultiSelect ( HasPrivateTraits ):
    """ This class demonstrates using the StringListEditor to select a set
        of string values from a set of choices.
    """
    
    # The list of choices to select from:
    choices = List( Str )
    
    # The currently selected list of choices:
    selected = List( Str )
    
    # A dummy result so that we can display the selection using the same 
    # StringListEditor:
    result = List( Str )
    
    # A traits view showing the list of choices on the left-hand side, and
    # the currently selected choices on the right-hand side:
    view = View(
        HGroup(
            Item( 'selected',
                  show_label = False,
                  editor     = StringListEditor( choices = 'choices' )
            ),
            Item( 'result',
                  show_label = False,
                  editor     = StringListEditor( choices = 'selected' )
            )
        ),
        width  = 0.20,
        height = 0.25
    )
    
# Create the demo:
demo = MultiSelect( choices  = [ 'one', 'two', 'three', 'four', 'five', 'six', 
                                 'seven', 'eight', 'nine', 'ten' ],
                    selected = [ 'two', 'five', 'nine' ] )

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
    
