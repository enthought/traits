#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
This demo illustrates use of the LEDEditor for displaying numeric values
using a simulated LED display control.
"""

from threading \
    import Thread

from time \
    import sleep

from traits.api \
    import HasTraits, Instance, Int, Bool, Float

from traitsui.api \
    import View, Item, HGroup, Handler, UIInfo, spring

from traitsui.wx.extra.led_editor \
    import LEDEditor

# Handler class for the LEDDemo class view:
class LEDDemoHandler ( Handler ):

    # The UIInfo object associated with the UI:
    info = Instance( UIInfo )

    # Is the demo currently running:
    running = Bool( True )

    # Is the thread still alive?
    alive = Bool( True )

    def init ( self, info ):
        self.info = info
        Thread( target = self._update_counter ).start()

    def closed ( self, info, is_ok ):
        self.running = False
        while self.alive:
            sleep( .05 )

    def _update_counter ( self ):
        while self.running:
            self.info.object.counter1 += 1
            self.info.object.counter2 += .001
            sleep( .01 )
        self.alive = False

# The main demo class:
class LEDDemo ( HasTraits ):

    # A counter to display:
    counter1 = Int

    # A floating point value to display:
    counter2 = Float

    # The traits view:
    view = View(
        Item( 'counter1',
              label  = 'Left aligned',
              editor = LEDEditor( alignment = 'left' )
        ),
        Item( 'counter1',
              label  = 'Center aligned',
              editor = LEDEditor( alignment = 'center' )
        ),
        Item( 'counter1',
              label  = 'Right aligned',
              editor = LEDEditor()  # default = 'right' aligned
        ),
        Item( 'counter2',
              label  = 'Float value',
              editor = LEDEditor( format_str = '%.3f' )
        ),
        '_',
        HGroup(
            Item( 'counter1',
                  label  = 'Left',
                  height = -40,
                  width  = 120,
                  editor = LEDEditor( alignment = 'left' )
            ),
            spring,
            Item( 'counter1',
                  label  = 'Center',
                  height = -40,
                  width  = 120,
                  editor = LEDEditor( alignment = 'center' )
            ),
            spring,
            Item( 'counter1',
                  label  = 'Right',
                  height = -40,
                  width  = 120,
                  editor = LEDEditor()  # default = 'right' aligned
            ),
            spring,
            Item( 'counter2',
                  label  = 'Float',
                  height = -40,
                  width  = 120,
                  editor = LEDEditor( format_str = '%.3f' )
            )
        ),
        title   = 'LED Editor Demo',
        buttons = [ 'OK' ],
        handler = LEDDemoHandler
    )

# Create the demo:
demo = LEDDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
