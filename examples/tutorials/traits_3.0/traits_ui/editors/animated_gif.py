#--(Animated GIF Editor)--------------------------------------------------------
"""
Animated GIF Editor
===================

In Traits 3.0, a new **AnimatedGIFEditor** has been added to the Traits UI
package. The purpose of the editor is to allow inclusion of simple animated
graphics into a traits UI via the use of animated GIF files.

The traits supported by the **AnimatedGIFEditor** editor are as follows:
    
playing
    A string that specifies the extended name of a trait that specifies whether
    the animated GIF file is playing or not. If not specified, the default is to 
    play the animated GIF file endlessly.
    
The value associated with **AnimatedGIFEditor** should be the name of the
animated GIF image file to be displayed. No user editing of the value is
provided by this editor, it is display only.
"""

#--[Imports]--------------------------------------------------------------------

from os.path \
    import join, dirname
    
from enthought.traits.api \
    import HasTraits, File, Bool, Int
    
from enthought.traits.ui.api \
    import View, VGroup, HGroup, Item, EnumEditor
    
from enthought.traits.ui.wx.animated_gif_editor \
    import AnimatedGIFEditor

#--[Setup]----------------------------------------------------------------------

# Some sample animated GIF files:    
import enthought.traits.ui as ui

base_path = join( dirname( ui.__file__ ), 'demo', 'Extras', 'images' )

# Get the names of the animated GIF files that can be displayed:
files = [
    join( base_path, 'logo_64x64.gif' ),
    join( base_path, 'logo_48x48.gif' ),
    join( base_path, 'logo_32x32.gif' )
]

#--[AnimatedGIFDemo Class]------------------------------------------------------

class AnimatedGIFDemo ( HasTraits ):
    
    # The animated GIF file to display:
    gif_file = File( files[0] )
                 
    # Is the animation playing or not?
    playing = Bool( True )
                 
    # The traits view:
    view = View(
        VGroup(
            HGroup(
                Item( 'gif_file', 
                      editor     = AnimatedGIFEditor( playing = 'playing' ),
                      show_label = False ),
                Item( 'playing' ),
            ),
            '_',
            Item( 'gif_file', 
                  label  = 'GIF File',
                  editor = EnumEditor( values = files )
            )
        ),
        title     = 'Animated GIF Demo',
        resizable = True,
        buttons   = [ 'OK' ]
    )

#--<Example*>-------------------------------------------------------------------

demo = AnimatedGIFDemo()

