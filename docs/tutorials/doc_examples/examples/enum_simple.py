#--[Imports]--------------------------------------------------------------------

from enthought.traits.api \
    import HasTraits, Enum

#--[Code]-----------------------------------------------------------------------

# Example of using simple Enum traits:

class Flower ( HasTraits ):
    
    kind  = Enum( 'annual', 'perennial' )
    color = Enum( 'red', [ 'white', 'yellow', 'red' ] )
    
    view = View(
        Item( 'kind' ),
        Item( 'color' )
    )
    
#--[Example*]-------------------------------------------------------------------

demo = Flower()
    
