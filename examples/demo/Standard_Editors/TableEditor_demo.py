#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Implementation of a TableEditor demo plugin for Traits UI demo program

This demo shows the full behavior of a straightforward TableEditor.  Only
one style of TableEditor is implemented, so that is the one shown.
"""

# Import statements:
from traits.api \
    import HasTraits, HasStrictTraits, Str, Int, Regex, List

from traitsui.api \
    import View, Group, Item, TableEditor

from traitsui.table_column \
    import ObjectColumn, ExpressionColumn

from traitsui.table_filter \
    import EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate, \
           EvalTableFilter

# A helper class for the 'Department' class below:
class Employee ( HasTraits ):
    first_name = Str
    last_name  = Str
    age        = Int
    phone      = Regex( value = '000-0000', regex = '\d\d\d[-]\d\d\d\d' )

    traits_view = View(
        'first_name', 'last_name', 'age', 'phone',
        title   = 'Create new employee',
        width   = 0.18,
        buttons = [ 'OK', 'Cancel' ]
    )

# The definition of the demo TableEditor:
table_editor = TableEditor(
    columns = [ ObjectColumn( name = 'first_name', width = 0.20 ),
                ObjectColumn( name = 'last_name',  width = 0.20 ),
                ExpressionColumn(
                    label = 'Full Name',
                    width = 0.30,
                    expression = "'%s %s' % (object.first_name, "
                                 "object.last_name )" ),
                ObjectColumn( name = 'age',   width = 0.10,
                              horizontal_alignment = 'center' ),
                ObjectColumn( name = 'phone', width = 0.20 ) ],
    deletable   = True,
    sort_model  = True,
    auto_size   = False,
    orientation = 'vertical',
    edit_view   = View(
                      Group( 'first_name', 'last_name', 'age', 'phone',
                             show_border = True
                      ),
                      resizable = True
                  ),
    filters     = [ EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate ],
    search      = EvalTableFilter(),
    show_toolbar = True,
    row_factory = Employee )

# The class to be edited with the TableEditor:
class Department ( HasStrictTraits ):

    employees = List( Employee )

    traits_view = View(
        Group(
            Item( 'employees',
                  show_label  = False,
                  editor      = table_editor
            ),
            show_border = True,
        ),
        title     = 'TableEditor',
        width     = .4,
        height    = .4,
        resizable = True,
        buttons   = [ 'OK' ],
        kind      = 'live'
    )

# Create some employees:
employees = [
    Employee( first_name = 'Jason', last_name = 'Smith',
              age = 32, phone = '555-1111' ),
    Employee( first_name = 'Mike',  last_name = 'Tollan',
              age = 34, phone = '555-2222' ),
    Employee( first_name = 'Dave',  last_name = 'Richards',
              age = 42, phone = '555-3333' ),
    Employee( first_name = 'Lyn',   last_name = 'Spitz',
              age = 40, phone = '555-4444' ),
    Employee( first_name = 'Greg',  last_name = 'Andrews',
              age = 45, phone = '555-5555' )
]

# Create the demo:
demo = Department( employees = employees )

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
