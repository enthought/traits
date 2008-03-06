# delegate_prefix.py --- Examples of Delegate() prefix parameter

#--[Imports]--------------------------------------------------------------------
from enthought.traits.api import Delegate, Float, HasTraits, Instance, Str

#--[Code]-----------------------------------------------------------------------

class Parent (HasTraits):
    first_name = Str 
    family_name = '' 
    favorite_first_name = Str 
    child_allowance = Float(1.00)

class Child (HasTraits):
    __prefix__ = 'child_'
    first_name = Delegate('mother', prefix='favorite_*')
    last_name  = Delegate('father', prefix='family_name')
    allowance  = Delegate('father', prefix='*')
    father     = Instance(Parent)
    mother     = Instance(Parent)
    
#--[Example*]-------------------------------------------------------------------

fred = Parent( first_name = 'Fred',
               family_name = 'Lopez',
               favorite_first_name = 'Diego',
               child_allowance = 5.0 )
               
maria = Parent( first_name = 'Maria',
                family_name = 'Gonzalez',
                favorite_first_name = 'Tomas',
                child_allowance = 10.0 )
                
nino = Child( father=fred, mother=maria )

print '%s %s gets $%.2f for allowance' % (nino.first_name, nino.last_name, nino.allowance)
