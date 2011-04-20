"""
Implementation of an ImageEnumEditor demo plugin for the Traits UI demo program.

This demo shows each of the four styles of the ImageEnumEditor.
"""

from traits.api import HasTraits, Str, Trait
from traitsui.api import Item, Group, View, ImageEnumEditor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# This list of image names (with the standard suffix "_origin") is used to
# construct an image enumeration trait to demonstrate the ImageEnumEditor.

image_list = [ 'top left', 'top right', 'bottom left', 'bottom right' ]


#-------------------------------------------------------------------------------
#  Classes:
#-------------------------------------------------------------------------------

class Dummy(HasTraits):
    """ Dummy class for ImageEnumEditor
    """
    x = Str
    view = View(" ")



class ImageEnumEditorDemo( HasTraits ):
    """ This class specifies the details of the ImageEnumEditor demo.
    """

    # To demonstrate any given Trait editor, an appropriate Trait is required.
    image_from_list  = Trait( editor = ImageEnumEditor( values = image_list,
                                                        prefix = '@icons:',
                                                        suffix = '_origin',
                                                        cols   = 4,
                                                        klass  = Dummy ),
                              *image_list )


    # Items are used to define the demo display - one Item per
    # editor style
    img_group = Group( Item('image_from_list', style='simple', label='Simple'),
                       Item('_'),
                       Item('image_from_list', style='custom', label='Custom'),
                       Item('_'),
                       Item('image_from_list', style='text', label='Text'),
                       Item('_'),
                       Item('image_from_list',
                             style='readonly',
                             label='ReadOnly'))

    #Demo view
    view1 = View( img_group,
                  title='ImageEnumEditor',
                  buttons=['OK'] )


# Create the demo:
popup = ImageEnumEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

