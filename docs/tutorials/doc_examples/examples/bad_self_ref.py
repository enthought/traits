#--[Imports]--------------------------------------------------------------------

from enthought.traits.api import HasTraits, Trait

#--[Code]-----------------------------------------------------------------------

# Shows the incorrect way of defining a self-referencing class.

class Employee ( HasTraits ):
    
    # This won't work, 'Employee' is not defined until the class definition
    # is complete:
    manager = Instance( Employee )
