# delegate.py --- Example of trait delegation
from enthought.traits.api import Delegate, HasTraits, Str, Trait
class Parent(HasTraits):
    first_name = Str 
    last_name  = Str 

class Child(HasTraits):
    first_name = Trait('')
    last_name  = Delegate('father')
    father     = Trait(Parent)
    mother     = Trait(Parent)
"""
>>> tony  = Parent(first_name='Anthony', last_name='Jones')
>>> alice = Parent(first_name='Alice', last_name='Smith')
>>> sally = Child( first_name='Sally', father=tony, \
...                mother=alice)
>>> print sally.last_name
Jones
>>> sally.last_name = 'Smith'
>>> sally.last_name = sally.mother # ERR: string expected
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
  File "c:\wrk\src\lib\enthought\traits\trait_handlers.py", line 
90, in error
    raise TraitError, ( object, name, self.info(), value )
enthought.traits.trait_errors.TraitError: The 'last_name' trait 
of a Child instance must be a value of type 'str', but a value of 
<__main__.Parent object at 0x009DD6F0> was specified.
"""
