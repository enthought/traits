#--[Imports]--------------------------------------------------------------------

from enthought.traits.api import HasTraits, Trait

#--[Code]-----------------------------------------------------------------------

# Shows the incorrect way of defining mutually-referring classes.

class Chicken ( HasTraits ):
    
    # Won't work: 'Egg' not defined yet:
    hatched_from = Instance( Egg )

    
class Egg ( HasTraits ):
    
    # If we move this class to the top, then this line won't work, because
    # 'Chicken' won't be defined yet:
    created_by = Instance( Chicken )
