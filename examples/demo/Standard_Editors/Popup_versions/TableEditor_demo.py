"""
Implementation of a TableEditor demo plugin for Traits UI demo program

This demo shows the full behavior of a straightforward TableEditor.  Only
one style of TableEditor is implemented, so that is the one shown.
"""

# Imports:
from traits.api \
    import HasTraits, HasStrictTraits, Str, Int, Regex, List, Enum

from traitsui.api \
    import View, Group, Item, TableEditor

from traitsui.table_column \
    import ObjectColumn

from traitsui.table_filter \
    import EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate, \
           RuleTableFilter

# A helper class for 'Department' below:
class Employee ( HasTraits ):
    name  = Str
    age     = Int
    gender  = Enum( 'Male', 'Female' )
    phone   = Regex( value = '000-0000', regex = '\d\d\d[-]\d\d\d\d')

    traits_view = View(
        'name', 'age', 'phone',
        title = 'Create new employee',
        width = 0.18,
        buttons = [ 'OK', 'Cancel' ]
    )

# For readability, the parameters of the demo TableEditor are set here, rather
# than in the View:
table_editor = TableEditor(
    columns     = [ ObjectColumn( name = 'name',   width = 0.30 ),
                    ObjectColumn( name = 'age',    width = 0.20 ),
                    ObjectColumn( name = 'gender', width = 0.25 ),
                    ObjectColumn( name = 'phone',  width = 0.25 ) ],
    auto_size   = False,
    deletable   = True,
    sort_model  = True,
    orientation = 'vertical',
    edit_view   = View( Group( 'name', 'age', 'phone', show_border=True),
                          resizable = True ),
    filters     = [ EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate ],
    search      = RuleTableFilter(),
    row_factory = Employee )

# The class to be edited with the TableEditor:
class Department ( HasStrictTraits ):
    employees = List( Employee )
    traits_view = View( Group( Item( 'employees',
                                     editor = table_editor),
                               show_border=True,
                               show_labels=False),
                        title = 'Department Personnel',
                        width = .4,
                        height = .4,
                        resizable = True,
                        buttons  = [ 'OK', 'Cancel', 'Undo' ],
                        kind = 'live' )



# Create some employees:
jas  = Employee( name = 'Jason', age = 32, phone = '555-1111' )
mike = Employee( name = 'Mike',  age = 34, phone = '555-2222' )
dave = Employee( name = 'Dave',  age = 42, phone = '555-3333' )
lyn  = Employee( name = 'Lyn',   age = 40, phone = '555-4444' )
greg = Employee( name = 'Greg',  age = 45, phone = '555-5555' )

# Create the demo:
popup = Department( employees = [ jas, mike, dave, lyn, greg ] )

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

