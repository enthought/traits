# cached_prop.py - Example of @cached_property decorator 

#--[Imports]--------------------------------------------------------------------
from enthought.traits.api import HasPrivateTraits, List, Int,\
                                 Property, cached_property

#--[Code]-----------------------------------------------------------------------

class TestScores ( HasPrivateTraits ):

    scores  = List( Int )
    average = Property( depends_on = 'scores' )

    @cached_property
    def _get_average ( self ):
        s = self.scores
        return (float( reduce( lambda n1, n2: n1 + n2, s, 0 ) )
                 / len( s ))

