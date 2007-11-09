#--[Imports]--------------------------------------------------------------------

from enthought.traits.api import HasTraits, CStr, CFloat

#--[Code]-----------------------------------------------------------------------
# Shows use of some of the simple casting types.

class Person ( HasTraits ):
    
    # Casts assigned values to 'string':
    name = CStr
    
    # Casts assigned values to 'float':
    weight = CFloat
    
#--[Example*]-------------------------------------------------------------------    

# Create a sample Person:
bill = Person()

# Simple cases:
bill.name = 'William'
print "bill.name:", bill.name

bill.weight = 186.4
print "bill.weight:", bill.weight

# Some examples that cast:
bill.name = 451
print "bill.name:", bill.name

bill.weight = 210
print "bill.weight:", bill.weight

bill.weight = '191.3'
print "bill.weight:", bill.weight

# Some examples that won't cast:

try:
    # Don't allow objects to be cast to string:
    bill.name = bill
except:
    import traceback
    traceback.print_exc()

try:
    # This string can't be cast to a float:
    bill.weight = 'about average'
except:
    import traceback
    traceback.print_exc()
    
