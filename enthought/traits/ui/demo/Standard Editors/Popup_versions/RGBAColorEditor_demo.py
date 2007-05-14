"""
Implementation of an RGBAColorEditor demo plugin for Traits UI demo program.

This demo shows each of the four styles of the RGBAColorEditor.
"""

from enthought.traits.api import HasTraits, RGBAColor
from enthought.traits.ui.api import Item, Group, View

#-------------------------------------------------------------------------------
#  Demo Class
#-------------------------------------------------------------------------------

class RGBAColorEditorDemo ( HasTraits ): 
    """ This class specifies the details of the RGBAColorEditor demo.
    """

    # To demonstrate any given Trait editor, an appropriate Trait is required. 
    RGBAcolor_trait = RGBAColor

    # Items are used to define the demo display - one item per 
    # editor style
    RGBAcolor_group = Group( Item('RGBAcolor_trait',
                                   style='simple', 
                                   label='Simple'), 
                             Item('_'),
                             Item('RGBAcolor_trait', 
                                   style='custom', 
                                   label='Custom'), 
                             Item('_'),
                             Item('RGBAcolor_trait',
                                   style='text', 
                                   label='Text'), 
                             Item('_'),
                             Item('RGBAcolor_trait',
                                   style='readonly', 
                                   label='ReadOnly')) 

    # Demo view
    view1 = View( RGBAcolor_group,
                  title = 'RGBAColorEditor',
                  buttons = ['OK'] )


# Hook for 'demo.py' 
popup = RGBAColorEditorDemo()

if __name__ == "__main__":
    popup.configure_traits()
