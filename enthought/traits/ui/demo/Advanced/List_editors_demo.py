"""
This shows the three different types of editor that can be applied to a list
of objects:
    
 - Table
 - List
 - Dockable notebook (a list variant)
 
Each editor style is editing the exact same list of objects. Note that any
changes made in one editor are automatically reflected in the others.
"""

# Imports:  
from enthought.traits.api \
    import HasStrictTraits, Str, Int, Regex, List, Instance
    
from enthought.traits.ui.api \
    import View, Item, VSplit, TableEditor, ListEditor
    
from enthought.traits.ui.table_column \
    import ObjectColumn
    
from enthought.traits.ui.table_filter \
    import TableFilter, RuleTableFilter, RuleFilterTemplate, \
           MenuFilterTemplate, EvalFilterTemplate
        
# 'Person' class:  
class Person ( HasStrictTraits ):
    
    # Trait definitions:  
    name  = Str
    age   = Int
    phone = Regex( value = '000-0000', regex = '\d\d\d[-]\d\d\d\d' )
    
    # Traits view definition:  
    traits_view = View( 'name', 'age', 'phone', 
                        width   = 0.18,
                        buttons = [ 'OK', 'Cancel' ] )
    
# Sample data:  
people = [
   Person( name = 'Dave',   age = 39, phone = '555-1212' ),
   Person( name = 'Mike',   age = 28, phone = '555-3526' ),
   Person( name = 'Joe',    age = 34, phone = '555-6943' ),
   Person( name = 'Tom',    age = 22, phone = '555-7586' ),
   Person( name = 'Dick',   age = 63, phone = '555-3895' ),
   Person( name = 'Harry',  age = 46, phone = '555-3285' ),
   Person( name = 'Sally',  age = 43, phone = '555-8797' ),
   Person( name = 'Fields', age = 31, phone = '555-3547' )
]

# Table editor definition:  
filters      = [ EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate ]

table_editor = TableEditor(
    columns     = [ ObjectColumn( name = 'name' ),
                    ObjectColumn( name = 'age' ),
                    ObjectColumn( name = 'phone' ) ],
    editable    = True,
    deletable   = True,
    sortable    = True,
    sort_model  = True,
    filters     = filters,
    search      = RuleTableFilter(),
    row_factory = Person
)

# 'ListTraitTest' class:  
class ListTraitTest ( HasStrictTraits ):
    
    # Trait definitions:  
    people = List( Person )
    
    # Traits view definitions:  
    traits_view = View(
        VSplit(
            Item( 'people',
                  id     = 'table',
                  editor = table_editor ),
            Item( 'people@',
                  id     = 'list',
                  editor = ListEditor( style = 'custom', 
                                       rows  = 5 ) ),
            Item( 'people@',
                  id     = 'notebook',
                  editor = ListEditor( use_notebook = True, 
                                       deletable    = True,
                                       export       = 'DockShellWindow',
                                       page_name    = '.name' ) ),
            id          = 'splitter',
            show_labels = False ),
        id   = 'enthought.traits.ui.demo.Traits UI Demo.Advanced.List_editors_demo',
        dock = 'horizontal' )

# Set up the demo:
demo = ListTraitTest( people = people )

if __name__ == "__main__":
    demo.configure_traits()        
    
