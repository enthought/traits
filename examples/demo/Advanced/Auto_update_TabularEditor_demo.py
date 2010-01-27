#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Demonstrates using a TabularEditor with the 'auto_update' feature enabled, which
allows the tabular editor to automatically update itself when the content of
any object in the list associated with the editor is modified.

To interact with the demo:
  - Select an employee from the list.
  - Adjust their salary increase.
  - Click the <b>Give raise</b> button.
  - Observe that the table automatically updates to reflect the employees new 
    salary.
"""

#-- Imports --------------------------------------------------------------------

from enthought.traits.api \
    import HasTraits, Str, Float, List, Instance, Button
    
from enthought.traits.ui.api \
    import View, HGroup, Item, TabularEditor, spring
    
from enthought.traits.ui.tabular_adapter \
    import TabularAdapter
    
#-- EmployeeAdapter Class ------------------------------------------------------

class EmployeeAdapter ( TabularAdapter ):
    
    columns = [ ( 'Name', 'name' ), ( 'Salary', 'salary' ) ]

    def get_default_value( self, object, trait ):
        return Employee( salary = 30000 )
    
#-- Employee Class -------------------------------------------------------------

class Employee ( HasTraits ):
    
    name   = Str
    salary = Float

#-- Company Class --------------------------------------------------------------

class Company ( HasTraits ):

    employees  = List( Employee )
    employee   = Instance( Employee )
    increase   = Float
    give_raise = Button( 'Give raise' )
    
    view = View(
        Item( 'employees', 
              show_label = False,
              editor     = TabularEditor( adapter     = EmployeeAdapter(),
                                          selected    = 'employee',
                                          auto_update = True )
        ),
        HGroup( 
            spring,
            Item( 'increase' ),
            Item( 'give_raise',
                  show_label   = False,
                  enabled_when = 'employee is not None' )
        ),
        title     = 'Auto Update Tabular Editor demo', 
        height    = 0.25,
        width     = 0.30,
        resizable = True 
    )
    
    def _give_raise_changed ( self ):
        self.employee.salary += self.increase
        self.employee = None
        
#-- Set up the demo ------------------------------------------------------------        

demo = Company( increase = 1000, employees = [
    Employee( name = 'Fred',   salary = 45000 ),
    Employee( name = 'Sally',  salary = 52000 ),
    Employee( name = 'Jim',    salary = 39000 ),
    Employee( name = 'Helen',  salary = 41000 ),
    Employee( name = 'George', salary = 49000 ),
    Employee( name = 'Betty',  salary = 46000 ) ] )

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
    
