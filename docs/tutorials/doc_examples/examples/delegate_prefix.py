# delegate_prefix.py --- Examples of Delegate() prefix 
#                        parameter
from enthought.traits.api import Delegate, Float, HasTraits, Str, \
                             Trait

class Parent (HasTraits):
    first_name = Str 
    family_name = '' 
    favorite_first_name = Str 
    child_allowance = Float(1.00)

class Child (HasTraits):
    __prefix__ = 'child_'
    first_name = Delegate('mother', 'favorite_*')
    last_name  = Delegate('father', 'family_name')
    allowance  = Delegate('father', '*')
    father     = Trait(Parent)
    mother     = Trait(Parent)
