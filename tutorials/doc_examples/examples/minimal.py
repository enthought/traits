# minimal.py --- Minimal example of using traits.

#--[Imports]--------------------------------------------------------------------
from enthought.traits.api import HasTraits, Float

#--[Code]-----------------------------------------------------------------------

class Person(HasTraits):
    weight = Float(150.0)

#--[Example*]-------------------------------------------------------------------

# instantiate the class
joe = Person()
# Show the default value
joe.weight
150.0
# Assign new values
joe.weight = 161.9     # OK to assign a float 
joe.weight = 162       # OK to assign an int
# The following line causes a traceback:
joe.weight = 'average' # Error to assign a string 


