#--[Imports]--------------------------------------------------------------------

from enthought.traits.api \
    import HasTraits, Str, Int, Enum

#--[Code]-----------------------------------------------------------------------

# Example of using a default traits user interface:

# Define a class without an explit View:
class Person ( HasTraits ):
    
    first_name = Str
    last_name  = Str
    age        = Int
    gender     = Enum( 'Male', 'Female' )

#--[Example*]-------------------------------------------------------------------

# Create a sample Person and edit it using a default traits
# user interface (since no explicit View is defined either
# in the class or here):
demo = Person()
