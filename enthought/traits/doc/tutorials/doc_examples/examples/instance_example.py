#--[Imports]--------------------------------------------------------------------

from enthought.traits.api \ 
    import HasTraits, Instance, Int, Str

#--[Code]-----------------------------------------------------------------------

# Example of using the Instance trait:

class Person ( HasTraits ):
    
    name = Str
    age  = Int

# Create a sample Person to use on the class below:    
bill = Person( name = 'William' )

# Define a class containing 'Instance' trait definitions:
class EmployeeInfo ( HasTraits ):
    
    # Define an instance using a class (default value is None):
    worker = Instance( Person )
    
    # Define an instance using a class (default value is a new instance of
    # Person( name = 'William' ):
    substitute = Instance( Person, { 'name': 'Mike' } )
    
    # Define an instance using an instance (i.e. an example):
    # The values must be instances of Person, and the default value is the
    # 'bill' object (not usually what you want):
    manager = Instance( bill )
    
#--[Example*]-------------------------------------------------------------------

# Create a sample EmployeeInfo object:
ei = EmployeeInfo()

# Display its initial contents:
ei.print_traits()

# Create another EmployeeInfo object:
ei2 = EmployeeInfo()

# Display its initial contents (compare to the first object):
ei2.print_traits()

# Assign a new manager:
ei.manager = Person( name = 'Mark' )

# Now try it with an invalid value:
ei2.manager = 'Richard'

