#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

#--(Extended Property depends_on References)------------------------------------
"""
Extended Property *depends_on* References
=========================================

In Traits 3.0, the **Property** *depends_on* metadata has been extended to
take advantage of the new extended trait name support offered by the
*on_trait_change* method.

Previously, the *depends_on* metadata for a *Property* was restricted to
referencing traits defined either on the same object as the **Property**, or
on an object immediately reachable from the object. For example::

    class Wheel ( Part ):

        axel     = Instance( Axel )
        position = Property( depends_on = 'axel.position' )

        ...

Starting with Traits 3.0, the *depends_on* metadata may now include any
extended trait reference that is allowed by the enhanced *on_trait_change*
method. So, for example it is now legal to write things like::

    class Wheel ( Part ):

        axel     = Instance( Axel )
        position = Property( depends_on = 'axel.chassis.position' )

or::

    class Child ( Person ):

        mother = Instance( Person )
        father = Instance( Person )
        mood   = Property( depends_on = [ 'mother.+mood_affecting',
                                          'father.+mood_affecting' ] )

In particular, in the last example we are declaring that the **Child** class's
*mood* property depends upon the values of any of either its mother or
father object's traits that have *mood_affecting* metadata defined.

Thus, a **Child** object's *mood* property will fire a trait change notification
whenever any of the its mother's or father's mood affecting traits change.

Refer also to the code tabs for this lesson for a complete example using a
**Property** definition using *depends_on* metadata containing an extended trait
reference. In particular, take a look at the **LeagueModelView Class** tab's
*total_hits* trait definition.
"""
# FIXME - the functionality demoed above belongs here, but traitsui should be
# removed from the exampel below.
#--<Imports>--------------------------------------------------------------------

from traits.api \
    import *

#--[Player Class]---------------------------------------------------------------

# Define a baseball player:
class Player ( HasTraits ):

    # The name of the player:
    name = Str( '<new player>' )

    # The number of hits the player made this season:
    hits = Int

#--[Team Class]-----------------------------------------------------------------

# Define a baseball team:
class Team ( HasTraits ):

    # The name of the team:
    name = Str( '<new team>' )

    # The players on the team:
    players = List( Player )

    # The number of players on the team:
    num_players = Property( depends_on = 'players' )

    def _get_num_players ( self ):
        """ Implementation of the 'num_players' property.
        """
        return len( self.players )

#--[League Class]---------------------------------------------------------------

# Define a baseball league model:
class League ( HasTraits ):

    # The name of the league:
    name = Str( '<new league>' )

    # The teams in the league:
    teams = List( Team )

#--[Example*]-------------------------------------------------------------------

# Define some sample teams and players:
blue_birds = Team( name = 'Blue Birds', players = [
    Player( name = 'Mike Scott',     hits = 25 ),
    Player( name = 'Willy Shofield', hits = 37 ),
    Player( name = 'Tony Barucci',   hits = 19 ) ] )

chicken_hawks = Team( name = 'Chicken Hawks', players = [
    Player( name = 'Jimmy Domore',   hits = 34 ),
    Player( name = 'Bill Janks',     hits = 16 ),
    Player( name = 'Tim Saunders',   hits = 27 ) ] )

eagles = Team( name = 'Eagles', players = [
    Player( name = 'Joe Peppers',    hits = 33 ),
    Player( name = 'Sam Alone',      hits = 12 ),
    Player( name = 'Roger Clemson',  hits = 23 ) ] )

# Create a league and its corresponding model view:
demo = LeagueModelView(
    League( name  = 'National Baseball Conference',
            teams = [ blue_birds, chicken_hawks, eagles ] )
)

