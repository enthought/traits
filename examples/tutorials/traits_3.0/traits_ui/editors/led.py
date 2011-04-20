#--(LED Editor)-----------------------------------------------------------------
"""
LED Editor
==========

In Traits 3.0, a new **LEDEditor** has been added to the Traits UI package. The
editor allows displaying (but not editing) numeric values using a set of
simulated LEDs.

This editor is currently only available in the wxPython version of the Traits UI
in the *traitsui.wx.extras* package. The purpose of the *extras*
package is to provide a location for editors which may be toolkit specific, and
not necessarily available in all Traits UI toolkit packages.

The traits supported by the **LEDEditor** editor are as follows:

alignment
    Specifies the alignment of the numeric text within the control. The possible
    values are: *right* (the default), *left* and *center*.

The value edited by an **LEDEditor** should be an integer or float value,
or a string value containing only characters that would be found in an interger
or float value.
"""

#--[Imports]--------------------------------------------------------------------

from threading \
    import Thread

from time \
    import sleep

from traits.api \
    import HasTraits, Instance, Int, Float, Bool

from traitsui.api \
    import View, Item, HGroup, Handler, UIInfo, spring

from traitsui.wx.extra.led_editor \
    import LEDEditor

#--[LEDDemoHandler Class]-------------------------------------------------------

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

#--[LEDDemo Class]--------------------------------------------------------------

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

#--<Example*>-------------------------------------------------------------------

demo = LEDDemo()

