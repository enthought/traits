# delegate.py --- Example of trait delegation

#--[Imports]--------------------------------------------------------------------
from enthought.traits.api import Delegate, HasTraits, Str, Trait

#--[Code]-----------------------------------------------------------------------
class Parent(HasTraits):
    first_name = Str 
    last_name  = Str 

class Child(HasTraits):
    first_name = Trait('')
    last_name  = Delegate('father')
    father     = Trait(Parent)
    mother     = Trait(Parent)
    
#--[Example*]-------------------------------------------------------------------

tony  = Parent(first_name='Anthony', last_name='Jones')
alice = Parent(first_name='Alice', last_name='Smith')
sally = Child( first_name='Sally', father=tony, mother=alice)

# Child delegates its 'last_name' to its 'father' object's 'last_name'
print sally.last_name
# Output: Jones

# Assign an explicit value to the child's 'last_name'
sally.last_name = 'Smith'
# Validation is still controlled by the father's 'last_name' trait
sally.last_name = sally.mother # ERR: string expected
"""
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
  File "c:\src\trunk\enthought\traits\trait_handlers.py", line 163, in error
    raise TraitError, ( object, name, self.info(), value )
enthought.traits.trait_errors.TraitError: The 'last_name' trait of a Child 
instance must be a value of type 'str', but a value of <__main__.Parent object 
at 0x009DD6F0> was specified.
"""
