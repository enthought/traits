#--<Imports>--------------------------------------------------------------------

from enthought.traits.api import *

#--[Employee Class]-------------------------------------------------------------

class Employee ( HasTraits ):

    # The name of the employee:
    name = Str

    # The number of sick days they have taken this year:
    sick_days = Int

#--[Department Class]-----------------------------------------------------------

class Department ( HasTraits ):

    # The name of the department:
    name = Str

    # The employees in the department:
    employees = List( Employee )

#--[Corporation Class]----------------------------------------------------------

class Corporation ( HasTraits ):

    # The name of the corporation:
    name = Str

    # The departments within the corporation:
    departments = List( Department )

#--[Example*]-------------------------------------------------------------------

# Create some sample employees:
millie   = Employee( name = 'Millie',   sick_days = 2 )
ralph    = Employee( name = 'Ralph',    sick_days = 3 )
tom      = Employee( name = 'Tom',      sick_days = 1 )
slick    = Employee( name = 'Slick',    sick_days = 16 )
marcelle = Employee( name = 'Marcelle', sick_days = 7 )
reggie   = Employee( name = 'Reggie',   sick_days = 11 )
dave     = Employee( name = 'Dave',     sick_days = 0 )
bob      = Employee( name = 'Bob',      sick_days = 1 )
alphonse = Employee( name = 'Alphonse', sick_days = 5 )

# Create some sample departments:
accounting = Department( name      = 'accounting',
                         employees = [ millie, ralph, tom ] )

sales = Department( name      = 'Sales',
                    employees = [ slick, marcelle, reggie ] )

development = Department( name      = 'Development',
                          employees = [ dave, bob, alphonse ] )

# Create a sample corporation:
acme = Corporation( name        = 'Acme, Inc.',
                    departments = [ accounting, sales, development ] )

# Define a corporate 'whistle blower' function:
def sick_again ( object, name, old, new ):
    print '%s just took sick day number %d for this year!' % (
          object.name, new )

# Set up the function as a listener:
acme.on_trait_change( sick_again, 'departments.employees.sick_days' )

# Now let's try it out:
slick.sick_days  += 1
reggie.sick_days += 1
