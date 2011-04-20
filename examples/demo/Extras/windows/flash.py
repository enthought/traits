#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

""" Demo showing how to use the Windows specific Flash editor.
"""

# Imports:
from traitsui.wx.extra.windows.flash_editor \
    import FlashEditor

from traits.api \
    import Enum, HasTraits

from traitsui.api \
    import View, HGroup, Item

# The demo class:
class FlashDemo ( HasTraits ):

    # The Flash file to display:
    flash = Enum( 'http://www.ianag.com/arcade/swf/sudoku.swf',
                  'http://www.ianag.com/arcade/swf/f-336.swf',
                  'http://www.ianag.com/arcade/swf/f-3D-Reversi-1612.swf',
                  'http://www.ianag.com/arcade/swf/game_234.swf',
                  'http://www.ianag.com/arcade/swf/flashmanwm.swf',
                  'http://www.ianag.com/arcade/swf/2379_gyroball.swf',
                  'http://www.ianag.com/arcade/swf/f-1416.swf',
                  'http://www.ianag.com/arcade/swf/mah_jongg.swf',
                  'http://www.ianag.com/arcade/swf/game_e4fe4e55fedc2f502be627ee6df716c5.swf',
                  'http://www.ianag.com/arcade/swf/rhumb.swf' )

    # The view to display:
    view = View(
        HGroup(
            Item( 'flash', label = 'Pick a game to play' )
        ),
        '_',
        Item( 'flash',
              show_label = False,
              editor     = FlashEditor()
        )
    )

# Create the demo:
demo = FlashDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

