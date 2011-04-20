#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
This demo shows the proper way to create a <b>Property</b> whose value is a
list, especially when the value of the <b>Property</b> will be used in a user
interface, such as with the <b>TableEditor</b>.

Most of the demo is just the machinery to set up the example. The key thing to
note is the declaration of the <i>people</i> trait:

    people = Property( List, depends_on = 'ticker' )

In this case, by defining the <b>Property</b> as having a value of type
<b>List</b>, you are ensuring that the computed value of the property will be
validated using the <b>List</b> type, which in addition to verifying that the
value is indeed a list, also guarantees that it will be converted to a
<b>TraitListObject</b>, which is necessary for correct interaction with various
Traits UI editors in a user interface.

Note also the use of the <i>depends_on</i> metadata to trigger a trait property
change whenever the <i>ticker</i> trait changes (in this case, it is changed
every three seconds by a background thread).

Finally, the use of the <i>@cached_property</i> decorator simplifies the
implementation of the property by allowing the <b>_get_people</b> <i>getter</i>
method to perform the expensive generation of a new list of people only when
the <i>ticker</i> event fires, not every time it is accessed.
"""

#-- Imports --------------------------------------------------------------------

from random \
    import randint, choice

from threading \
   import Thread

from time \
    import sleep

from traits.api \
    import HasStrictTraits, HasPrivateTraits, Str, Int, Enum, List, Event, \
           Property, cached_property

from traitsui.api \
    import View, Item, TableEditor

from traitsui.table_column \
    import ObjectColumn

#-- Person Class ---------------------------------------------------------------

class Person ( HasStrictTraits ):
    """ Defines some sample data to display in the TableEditor.
    """

    name   = Str
    age    = Int
    gender = Enum( 'Male', 'Female' )

#-- PropertyListDemo Class -----------------------------------------------------

class PropertyListDemo ( HasPrivateTraits ):
    """ Displays a random list of Person objects in a TableEditor that is
        refreshed every 3 seconds by a background thread.
     """

    # An event used to trigger a Property value update:
    ticker = Event

    # The property being display in the TableEditor:
    people = Property( List, depends_on = 'ticker' )

    # Tiny hack to allow starting the background thread easily:
    begin = Int

    #-- Traits View Definitions ------------------------------------------------

    view = View(
        Item( 'people',
              show_label = False,
              editor = TableEditor(
                  columns = [
                      ObjectColumn( name = 'name',   editable = False,
                                    width = 0.50 ),
                      ObjectColumn( name = 'age',    editable = False,
                                    width = 0.15 ),
                      ObjectColumn( name = 'gender', editable = False,
                                    width = 0.35 )
                  ],
                  auto_size    = False,
                  show_toolbar = False
              )
        ),
        title     = 'Property List Demo',
        width     = 0.25,
        height    = 0.33,
        resizable = True
    )

    #-- Property Implementations -----------------------------------------------

    @cached_property
    def _get_people ( self ):
        """ Returns the value for the 'people' property.
        """
        return [ Person(
            name = '%s %s' % (
                choice( [ 'Tom', 'Dick', 'Harry', 'Alice', 'Lia', 'Vibha' ] ),
                choice( [ 'Thomas', 'Jones', 'Smith', 'Adams', 'Johnson' ] ) ),
            age    = randint( 21, 75 ),
            gender = choice( [ 'Male', 'Female' ] ) )
            for i in xrange( randint( 10, 20 ) )
        ]

    #-- Default Value Implementations ------------------------------------------

    def _begin_default ( self ):
        """ Starts the background thread running.
        """
        thread = Thread( target = self._timer )
        thread.setDaemon( True )
        thread.start()

        return 0

    #-- Private Methods --------------------------------------------------------

    def _timer ( self ):
        """ Triggers a property update every 3 seconds for 30 seconds.
        """
        for i in range( 10 ):
            sleep( 3 )
            self.ticker = True

# Create the demo:
demo = PropertyListDemo()
demo.begin

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

