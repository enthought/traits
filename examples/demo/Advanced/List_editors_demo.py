#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

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
from traits.api \
    import HasStrictTraits, Str, Int, Regex, List, Instance

from traitsui.api \
    import View, Item, Tabbed, TableEditor, ListEditor

from traitsui.table_column \
    import ObjectColumn

from traitsui.table_filter \
    import RuleTableFilter, RuleFilterTemplate, \
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
    columns     = [ ObjectColumn( name = 'name',  width = 0.4 ),
                    ObjectColumn( name = 'age',   width = 0.2 ),
                    ObjectColumn( name = 'phone', width = 0.4 ) ],
    editable    = True,
    deletable   = True,
    sortable    = True,
    sort_model  = True,
    auto_size   = False,
    filters     = filters,
    search      = RuleTableFilter(),
    row_factory = Person
)

# 'ListTraitTest' class:
class ListTraitTest ( HasStrictTraits ):

    # Trait definitions:
    people = List( Instance( Person, () ) )

    # Traits view definitions:
    traits_view = View(
        Tabbed(
            Item( 'people',
                  label  = 'Table',
                  id     = 'table',
                  editor = table_editor ),
            Item( 'people@',
                  label  = 'List',
                  id     = 'list',
                  editor = ListEditor( style = 'custom',
                                       rows  = 5 ) ),
            Item( 'people@',
                  label  = 'Notebook',
                  id     = 'notebook',
                  editor = ListEditor( use_notebook = True,
                                       deletable    = True,
                                       export       = 'DockShellWindow',
                                       page_name    = '.name' ) ),
            id          = 'splitter',
            show_labels = False ),
        id   = 'traitsui.demo.Traits UI Demo.Advanced.List_editors_demo',
        dock = 'horizontal' )

# Create the demo:
demo = ListTraitTest( people = people )

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

