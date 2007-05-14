#--[Imports]--------------------------------------------------------------------

from enthought.traits.api import Any, Str, Int, HasTraits

#--[Code]-----------------------------------------------------------------------

# Shows the trait attribute wildcard rules:

class Person ( HasTraits ):
    
    # Normal, explicitly defined trait:
    name = Str
    
    # By default, let all traits starting with '_' have any value:
    _ = Any 
    
    # Except for this one, which must be an Int:
    _age = Int
    
#--[Example*]-------------------------------------------------------------------

# Create a sample Person:
bill = Person()

# These assignments should all work:
bill.name      = 'William'
bill._address  = '121 Drury Lane'
bill._zip_code = 55212
bill._age      = 49

# This should generate an error (must be an Int):
try:
    bill._age = 'middle age'
except:
    import traceback
    traceback.print_exc()
    
# So should this (it's undefined, not covered by '_' rule):
try:
    bill.nick_name = 'Bill'
except:
    import traceback
    traceback.print_exc()
    
# Display the final results:
bill.print_traits()
