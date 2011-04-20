#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
This program demonstrates adding and using a statusbar in a Traits UI window.

A statusbar may contain one or more fields, and each field can be of a fixed
or variable size. Fixed width fields are specified in pixels, while variable
width fields are specified as fractional values relative to other variable
width fields.

The content of a statusbar field is specified via the extended trait name of
the object attribute that will contain the statusbar information.

In this example, there are two statusbar fields:

 - The current length of the text input data (variable width)
 - The current time (fixed width, updated once a second).

The demo runs as a pop-up window since statusbars can only appear within a
window frame.
"""

#-- Imports --------------------------------------------------------------------

from time \
    import sleep, strftime

from threading \
    import Thread

from traits.api \
    import HasPrivateTraits, Str, Property

from traitsui.api \
    import View, Item, StatusItem

#-- The demo class -------------------------------------------------------------

class TextEditor ( HasPrivateTraits ):

    # The text being edited:
    text = Str

    # The current length of the text being edited:
    length = Property( depends_on = 'text' )

    # The current time:
    time = Str

    # The view definition:
    view = View(
        Item( 'text', style = 'custom', show_label = False ),
        title     = 'Text Editor',
        id        = 'traitsui.demo.advanced.statusbar_demo',
        width     = 0.4,
        height    = 0.4,
        resizable = True,
        statusbar = [ StatusItem( name = 'length', width = 0.5 ),
                      StatusItem( name = 'time',   width = 85 ) ]
    )

    #-- Property Implementations -----------------------------------------------

    def _get_length ( self ):
        return ('Length: %d characters' % len( self.text ))

    #-- Default Trait Values ---------------------------------------------------

    def _time_default ( self ):
        thread = Thread( target = self._clock )
        thread.setDaemon( True )
        thread.start()

        return ''

    #-- Private Methods --------------------------------------------------------

    def _clock ( self ):
        """ Update the statusbar time once every second.
        """
        while True:
            self.time = strftime( '%I:%M:%S %p' )
            sleep( 1.0 )

# Create the demo object:
popup = TextEditor()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

