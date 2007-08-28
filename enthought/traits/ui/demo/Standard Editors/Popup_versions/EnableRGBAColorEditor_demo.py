"""
Implementation of an EnableRGBAColorEditor demo plugin for Traits UI demo
program.

This demo shows each of the four styles of the EnableRGBAColorEditor
"""

from enthought.enable2.traits.ui.wx.enable_rgba_color_editor import \
    EnableRGBAColorEditor
from enthought.enable2.traits.api import RGBAColor
from enthought.traits.api import HasTraits
from enthought.traits.ui.api import Item, Group, View

#-------------------------------------------------------------------------------
#  Demo Class
#-------------------------------------------------------------------------------

class EnableRGBAColorEditorDemo ( HasTraits ):
    """ This class specifies the details of the EnableRGBAColorEditor demo.
    """

    # To demonstrate any given Trait editor, an appropriate Trait is required.
    RGBAcolor_trait = RGBAColor

    # Items are used to define the demo display - one Item per
    # editor style
    RGBAcolor_group = Group( Item('RGBAcolor_trait',
                                   editor=EnableRGBAColorEditor(),
                                   style='simple',
                                   label='Simple'),
                             Item('_'),

                             # Custom editor has to be enclosed in a 'horizontal'
                             # Group to work around painting bug.
                             Group(Item('RGBAcolor_trait',
                                         editor=EnableRGBAColorEditor(),
                                         style='custom',
                                         label='Custom'),
                                   orientation='horizontal'),

                             Item('_'),
                             Item('RGBAcolor_trait',
                                   editor=EnableRGBAColorEditor(),
                                   style='text',
                                   label='Text'),
                             Item('_'),
                             Item('RGBAcolor_trait',
                                   editor=EnableRGBAColorEditor(),
                                   style='readonly',
                                   label='ReadOnly'))

    # Demo view
    view1 = View( RGBAcolor_group,
                  title = 'EnableRGBAColorEditor',
                  buttons = ['OK'] )


# Hook for 'demo.py'
popup = EnableRGBAColorEditorDemo()

if __name__ == "__main__":
    popup.configure_traits()
