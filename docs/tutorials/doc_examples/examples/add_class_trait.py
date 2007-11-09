#--[Imports]--------------------------------------------------------------------

from enthought.traits.api import HasTraits, Instance

#--[Code]-----------------------------------------------------------------------

# Defining mutually-referring classes using add_class_trait()

class Chicken ( HasTraits ):
    
    pass

    
class Egg ( HasTraits ):
    
    created_by = Instance( Chicken )

# Now that 'Egg' is defined, we can add the 'hatched_from' trait to
# solve the mutual-reference problem...

Chicken.add_class_trait( 'hatched_from', Instance( Egg ) )

