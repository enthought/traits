# imageenumeditor.py --- Example of using an ImageEnumEditor
from enthought.traits.api import HasTraits, Trait
from enthought.traits.ui.api import ImageEnumEditor

origin_values = ['top left', 
                 'top right', 
                 'bottom left', 
                 'bottom right']

class ImageEnumTest(HasTraits):
    image_enum = Trait(editor=ImageEnumEditor( 
                                values=origin_values,
                                suffix='_origin', 
                                cols=4,
                                path='../../tests/images'),
                       *origin_values)
