#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

#--(Extended Traits UI Item and Editor References)------------------------------
"""
Extended Traits UI Item and Editor References
=============================================

In Traits 3.0, the Traits UI **Item** class and various *editor* classes
have been extended to use the new extended trait name support provided by the
*on_trait_change* method.

In previous Traits versions, for example, **Item** objects could only refer to
traits defined directly on a UI context object. For example::

    view = View(
        Item( 'name' ),
        Item( 'object.age' ),
        Item( 'handler.status' )
    )

In Traits 3.0 this restriction has been lifted, and now **Items** can reference
(i.e. edit) any trait reachable from a UI context object::

    view = View(
        Item( 'object.mother.name' ),
        Item( 'object.axel.chassis.serial_number', style = 'readonly' )
    )

Similarly, any Traits UI *editor* classes that previously accepted a trait name
now accept an extended trait name::

    view = View(
        Item( 'address' ),
        Item( 'state', editor = EnumEditor( name = 'handler.country.states' )
    )

Because **Items** and *editors* only refer to a single trait, you should not use
extended trait references that refer to multiple traits, such as
*'foo.[bar,baz]'* or *'foo.+editable'*, since the behavior of such references
is not defined.

Look at the code tabs for this lesson for a complete example of a Traits UI
using extended **Item** and editor references. In particular, the
**LeagueModelView Class** tab contains a **View** definition containing
extended references.

Code Incompatibilities
----------------------

Note that the editor enhancement may cause some incompatibities with editors
that previously supported both an *object* and *name* trait, with the *object*
trait containing the context object name, and the *name* trait containing the
name of  the trait on the specified context object. Using the new extended trait
references, these have been combined into a single *name* trait.

If you encounter such an occurrence in existing code, simply combine the
context object name and trait name into a single extended name of the form::

    context_object_name.trait_name

Warning
-------

Avoid extended **Item** references that contain intermediate links that could
be *None*. For example, in the following code::

    view = View(
        ...
        Item( 'object.team.players', ... )
        ...
    )

an exception will be raised if *object.team* is *None*, or is set to *None*,
while the view is active, since there is no obvious way to obtain a valid value
for *object.team.players* for the associated **Item** *editor* to display.

Note that the above example is borrowed from this lesson's demo code, which has
additional code written to ensure that *object.team* is not *None*. See the
*_model_changed* method in the **LeagueModelView Class** tab, which makes sure
that the *team* trait is intialized to a valid value when a new **League**
model is set up.
"""

#--<Imports>--------------------------------------------------------------------

from traits.api \
    import *

from traitsui.api \
    import *

from traitsui.table_column \
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

#--[LeagueModelView Class]-----------------------------------------------------

# Define a ModelView for a League model:
class LeagueModelView ( ModelView ):

    # The currently selected team:
    team = Instance( Team )

    # The currently selected player:
    player = Instance( Player )

    # Button to add a hit to the current player:
    got_hit = Button( 'Got a Hit' )

    # The total number of hits
    total_hits = Property( depends_on = 'model.teams.players.hits' )

    @cached_property
    def _get_total_hits ( self ):
        """ Returns the total number of hits across all teams and players.
        """
        return reduce( add, [ reduce( add, [ p.hits for p in t.players ], 0 )
                              for t in self.model.teams ], 0 )

    view = View(
        VGroup(
            HGroup(
                Item( 'total_hits', style = 'readonly' ),
                      label       = 'League Statistics',
                      show_border = True
            ),
            VGroup(
                Item( 'model.teams',
                      show_label = False,
                      editor = TableEditor(
                                columns = [ ObjectColumn( name  = 'name',
                                                          width = 0.70 ),
                                            ObjectColumn( name  = 'num_players',
                                                          label = '# Players',
                                                          editable = False,
                                                          width = 0.29 ) ],
                                selected     = 'object.team',
                                auto_add     = True,
                                row_factory  = Team,
                                configurable = False,
                                sortable     = False )
                ),
                label       = 'League Teams',
                show_border = True
            ),
            VGroup(
                Item( 'object.team.players', # <-- Extended Item name
                      show_label = False,
                      editor = TableEditor(
                                   columns  = [ ObjectColumn( name  = 'name',
                                                              width = 0.70 ),
                                                ObjectColumn( name  = 'hits',
                                                              editable = False,
                                                              width = 0.29 ) ],
                                   selected     = 'object.player',
                                   auto_add     = True,
                                   row_factory  = Player,
                                   configurable = False,
                                   sortable     = False )
                ),
                '_',
                HGroup(
                    Item( 'got_hit',
                          show_label   = False,
                          enabled_when = 'player is not None'
                    )
                ),
                label       = 'Team Players',
                show_labels = False,
                show_border = True
            )
        ),
        resizable = True
    )

    def _model_changed ( self, model ):
        """ Handles the 'league' model being initialized.
        """
        if len( model.teams ) > 0:
            self.team = model.teams[0]

    def _got_hit_changed ( self ):
        """ Handles the currently selected player making a hit.
        """
        self.player.hits += 1

    def _team_changed ( self, team ):
        """ Handles a new team being selected.
        """
        if len( team.players ) > 0:
            self.player = team.players[0]
        else:
            self.player = None

# Function to add two numbers (used with 'reduce'):
add = lambda a, b: a + b

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

