# minimal.py --- Minimal example of using traits.

#--[Imports]--------------------------------------------------------------------
from enthought.traits.api import HasTraits, Float

#--[Code]-----------------------------------------------------------------------

class Person(HasTraits):
    weight = Float(150.0)

#--[Example*]-------------------------------------------------------------------
"""
>>> # instantiate the class
>>> joe = Person()
>>> # Show the default value
>>> joe.weight
150.0
>>> # Assign new values
>>> joe.weight = 161.9     # OK to assign a float 
>>> joe.weight = 162       # OK to assign an int
>>> joe.weight = 'average' # Error to assign a string 
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
  File "c:\src\traits\enthought\traits\trait_handlers.py", line 163, in 
error
    raise TraitError, ( object, name, self.info(), 
value ) enthought.traits.trait_errors.TraitError: The 'weight' trait of a 
Person instance must be a value of type 'float', but a value of average was 
specified.
"""
