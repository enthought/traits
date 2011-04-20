#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
This program demonstrates defining and visualizing dynamic ranges.

A dynamic range is a range whose low or high limit can be modified dynamically
at run time.

You can define a dynamic range using the standard Range trait and specifying
the name of other traits as either the low or high limit value (or both). In
fact, it is even possible to specify the default value of the range trait as
another trait if desired. The traits used as low, high or default values need
not be defined on the same object, but can be defined on any object reachable
from the object (i.e. it allows use of extended trait names).

In this completely artificial example, we present an example of the first
hotel at the North Pole. The hotel guarantees that each room will be heated
to a certain minimum temperature. However, that minimum value is determined
both by the time of year and the current cost of heating fuel, so it can vary;
but each room is guaranteed the same minimum temperature.

Each guest of the hotel can choose among several different plans that allow
them to control the maximum room temperature. Higher maximum room temperatures
correspond to higher plan costs. Thus each guest must decide which plan (and
highest maximum room temperature) to pay for.

And finally, each guest is free to set the current room temperature anywhere
between the hotel minimum value and the guest's maximum plan value.

The demo is organized as a series of tabs corresponding to each guest of the
hotel, with access to the plan they have chosen and the current room
temperature setting. In addition, there is a master set of hotel information
displayed at the top of the view which allows you to change the season of the
year and the current fuel cost. There is also a button to allow more guests to
be added to the hotel.

Notes:
    - The dynamic range trait is the 'temperature' trait in the Guest class. It
      depends upon traits defined both in the Guest instance as well as in the
      containing Hotel object.

    - As with most traits code and examples, observe how much of the code is
      'declarative' versus 'imperative'. Note also the use of properties and
      'depends_on' metadata, as well as 'cached_property' and 'on_trait_change'
      method decorators.

    - Try dragging the guest tabs around so that you can see multiple guests
      simultaneously, and then watch the behavior of the guest's 'temperature'
      slider as you adjust the hotel 'season', 'fuel cost' and each guest's
      'plan'.
"""

#-- Imports --------------------------------------------------------------------

import logging, sys
logging.basicConfig(stream=sys.stderr)

from random \
    import choice

from traits.api \
    import HasPrivateTraits, Str, Enum, Range, List, Button, Instance, \
           Property, cached_property, on_trait_change

from traitsui.api \
    import View, VGroup, HGroup, Item, ListEditor, spring

#-- The Hotel class ------------------------------------------------------------

class Hotel ( HasPrivateTraits ):

    # The season of the year:
    season = Enum( 'Winter', 'Spring', 'Summer', 'Fall' )

    # The current cost of heating fuel (in dollars/gallon):
    fuel_cost = Range( 2.00, 10.00, 4.00 )

    # The current minimum temparature allowed by the hotel:
    min_temperature = Property( depends_on = 'season, fuel_cost' )

    # The guests currently staying at the hotel:
    guests = List # ( Instance( 'Guest' ) )

    # Add a new guest to the hotel:
    add_guest = Button( 'Add Guest' )

    # The view of the hotel:
    view = View(
        VGroup(
            HGroup(
                Item( 'season' ), '20',
                Item( 'fuel_cost', width = 300 ),
                spring,
                Item( 'add_guest', show_label = False ),
                show_border = True,
                label       = 'Hotel Information'
            ),
            VGroup(
                Item( 'guests',
                      style  = 'custom',
                      editor = ListEditor( use_notebook = True,
                                           deletable    = True,
                                           dock_style   = 'tab',
                                           page_name    = '.name' )
                ),
                show_labels = False,
                show_border = True,
                label       = 'Guests'
            )
        ),
        title     = 'The Belmont Hotel Dashboard',
        width     = 0.6,
        height    = 0.2,
        resizable = True
    )

    # Property implementations:
    @cached_property
    def _get_min_temperature ( self ):
        return ({ 'Winter': 32,
                  'Spring': 40,
                  'Summer': 45,
                  'Fall':   40 }[ self.season ] +
                  min( int( 60.00 / self.fuel_cost ), 15 ))

    # Event handlers:
    @on_trait_change( 'guests[]' )
    def _guests_modified ( self, removed, added ):
        for guest in added:
            guest.hotel = self

    def _add_guest_changed ( self ):
        self.guests.append( Guest() )

#-- The Guest class ------------------------------------------------------------

class Guest ( HasPrivateTraits ):

    # The name of the guest:
    name = Str

    # The hotel the guest is staying at:
    hotel = Instance( Hotel )

    # The room plan the guest has chosen:
    plan = Enum( 'Flop house', 'Cheap', 'Cozy', 'Deluxe' )

    # The maximum temperature allowed by the guest's plan:
    max_temperature = Property( depends_on = 'plan' )

    # The current room temperature as set by the guest:
    temperature = Range( 'hotel.min_temperature', 'max_temperature' )

    # The view of the guest:
    view = View(
        Item( 'plan' ),
        Item( 'temperature' )
    )

    # Property implementations:
    @cached_property
    def _get_max_temperature ( self ):
        return { 'Flop house': 62,
                 'Cheap':      66,
                 'Cozy':       75,
                 'Deluxe':     85 }[ self.plan ]

    # Default values:
    def _name_default ( self ):
        return choice(
            [ 'Leah', 'Vibha', 'Janet', 'Jody', 'Dave', 'Evan', 'Ilan', 'Gael',
              'Peter', 'Robert', 'Judah', 'Eric', 'Travis', 'Mike', 'Bryce',
              'Chris' ] )

#-- Create the demo ------------------------------------------------------------

# Create the demo object:
demo = Hotel( guests = [ Guest() for i in range( 5 ) ] )

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    logging.info('Start!')
    demo.configure_traits()

