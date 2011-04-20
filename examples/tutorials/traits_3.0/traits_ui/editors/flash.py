#--(Flash Editor (Windows Only))------------------------------------------------
"""
Flash Editor (Windows Only)
===========================

In Traits 3.0, a new **FlashEditor** has been added to the Traits UI package.
The editor allows displaying and interacting with Adobe Flash compatible files.

This editor is currently only available for the Windows platform and is
located in the wxPython version of the Traits UI in the
*traitsui.wx.extras.windows* package. The purpose of the
*extras.windows* package is to provide a location for editors which may be
toolkit and Windows platform specific, and not necessarily available in all
Traits UI toolkit packages or platforms.

The **FlashEditor** has no developer settable traits.

The value edited by a **FlashEditor** should be a string containing either the
URL or file name of the Flash file to display. This is a *read only* value that
is not modified by the editor. Changing the value causes the editor to display
the Flash file defined by the new value of the trait.
"""

#--[Imports]--------------------------------------------------------------------

from traitsui.wx.extra.windows.flash_editor \
    import FlashEditor

from traits.api \
    import HasTraits, Enum

from traitsui.api \
    import View, HGroup, Item

#--[FlashDemo Class]------------------------------------------------------------

class FlashDemo ( HasTraits ):

    # The Flash file to display:
    flash = Enum(
        'http://www.ianag.com/arcade/swf/sudoku.swf',
        'http://www.ianag.com/arcade/swf/f-336.swf',
        'http://www.ianag.com/arcade/swf/f-3D-Reversi-1612.swf',
        'http://www.ianag.com/arcade/swf/game_234.swf',
        'http://www.ianag.com/arcade/swf/flashmanwm.swf',
        'http://www.ianag.com/arcade/swf/2379_gyroball.swf',
        'http://www.ianag.com/arcade/swf/f-1416.swf',
        'http://www.ianag.com/arcade/swf/mah_jongg.swf',
        'http://www.ianag.com/arcade/swf/game_e4fe4e55fedc2f502be627ee6df716c5.swf',
        'http://www.ianag.com/arcade/swf/rhumb.swf'
    )

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

#--<Example*>-------------------------------------------------------------------

demo = FlashDemo()

