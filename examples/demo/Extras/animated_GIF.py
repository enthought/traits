#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
This demo shows you how to use animated GIF files in a traits user interface.
"""

from os.path \
    import join, dirname, abspath

from traits.api \
    import HasTraits, File, Bool

from traitsui.api \
    import View, VGroup, HGroup, Item, EnumEditor

from traitsui.wx.animated_gif_editor \
    import AnimatedGIFEditor

# Some sample animated GIF files:
import traits as traits

base_path = join( dirname( traits.api.__file__ ),
                  '..', '..', 'examples', 'demo', 'Extras', 'images' )

files = [
    abspath( join( base_path, 'logo_64x64.gif' ) ),
    abspath( join( base_path, 'logo_48x48.gif' ) ),
    abspath( join( base_path, 'logo_32x32.gif' ) )
]

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
        title   = 'Animated GIF Demo',
        buttons = [ 'OK' ]
    )

# Create the demo:
demo = AnimatedGIFDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
