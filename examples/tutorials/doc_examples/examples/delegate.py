#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# delegate.py --- Example of trait delegation

#--[Imports]-------------------------------------------------------------------
from traits.api import DelegatesTo, HasTraits, Instance, Str, TraitError


#--[Code]----------------------------------------------------------------------
class Parent(HasTraits):
    first_name = Str
    last_name = Str


class Child(HasTraits):
    first_name = Str
    last_name = DelegatesTo('father')
    father = Instance(Parent)
    mother = Instance(Parent)


#--[Example*]------------------------------------------------------------------
tony = Parent(first_name='Anthony', last_name='Jones')
alice = Parent(first_name='Alice', last_name='Smith')
sally = Child(first_name='Sally', father=tony, mother=alice)

# Child delegates its 'last_name' to its 'father' object's 'last_name'
print sally.last_name
# Output: Jones

# Assign an explicit value to the child's 'last_name'
sally.last_name = 'Cooper'
print tony.last_name
#Output: Cooper

# Validation is still controlled by the father's 'last_name' trait
print 'Attempting to assign a Parent object to a Str trait...\n'
try:
    sally.last_name = sally.mother  # ERR: string expected
except TraitError, c:
    print 'TraitError: ', c

"""
The exception printed will look similar to the following:

Traceback (most recent call last):
  File "<stdin>", line 1, in ?
  File "c:\src\trunk\enthought\traits\trait_handlers.py", line 163, in error
    raise TraitError, ( object, name, self.info(), value )
traits.trait_errors.TraitError: The 'last_name' trait of a Child
instance must be a value of type 'str', but a value of <__main__.Parent object
at 0x009DD6F0> was specified.
"""
