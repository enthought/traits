# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# delegate.py --- Example of trait delegation

# --[Imports]------------------------------------------------------------------
from traits.api import DelegatesTo, HasTraits, Instance, Str, TraitError


# --[Code]---------------------------------------------------------------------
class Parent(HasTraits):
    first_name = Str
    last_name = Str


class Child(HasTraits):
    first_name = Str
    last_name = DelegatesTo("father")
    father = Instance(Parent)
    mother = Instance(Parent)


# --[Example*]-----------------------------------------------------------------
tony = Parent(first_name="Anthony", last_name="Jones")
alice = Parent(first_name="Alice", last_name="Smith")
sally = Child(first_name="Sally", father=tony, mother=alice)

# Child delegates its 'last_name' to its 'father' object's 'last_name'
print(sally.last_name)
# Output: Jones

# Assign an explicit value to the child's 'last_name'
sally.last_name = "Cooper"
print(tony.last_name)
# Output: Cooper

# Validation is still controlled by the father's 'last_name' trait
print("Attempting to assign a Parent object to a Str trait...\n")
try:
    sally.last_name = sally.mother  # ERR: string expected
except TraitError as c:
    print("TraitError: ", c)

r"""
The exception printed will look similar to the following:

Traceback (most recent call last):
  File "<stdin>", line 1, in ?
  File "c:\src\trunk\enthought\traits\trait_handlers.py", line 163, in error
    raise TraitError( object, name, self.info(), value )
traits.trait_errors.TraitError: The 'last_name' trait of a Child
instance must be a value of type 'str', but a value of <__main__.Parent object
at 0x009DD6F0> was specified.
"""
