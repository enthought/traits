# all_wildcard.py --- Example of trait attribute wildcard rules

#--[Imports]--------------------------------------------------------------------
from enthought.traits.api import Any, Str, Int, HasTraits

#--[Code]-----------------------------------------------------------------------

class Person ( HasTraits ):
    
    # Normal, explicitly defined trait:
    name = Str
    
    # By default, let all traits have any value:
    _ = Any 
    
    # Except for this one, which must be an Int:
    age = Int
    
#--[Example*]-------------------------------------------------------------------

# Create a sample Person:
bill = Person()

# These assignments should all work:
bill.name      = 'William'
bill.address  = '121 Drury Lane'
bill.zip_code = 55212
bill.age      = 49

# This should generate an error (must be an Int):
try:
    bill.age = 'middle age'
except:
    import traceback
    traceback.print_exc()
    
# Display the final results:
bill.print_traits()
