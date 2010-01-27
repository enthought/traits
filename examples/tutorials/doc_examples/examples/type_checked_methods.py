#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# type_checked_methods.py --- Example of traits-based 
#                             method type checking

#--[Imports]--------------------------------------------------------------------
from enthought.traits.api import HasTraits, method, Tuple

#--[Code]-----------------------------------------------------------------------

Color = Tuple(int, int, int, int)

class Palette(HasTraits):

    method(Color, color1=Color, color2=Color)
    def blend (self, color1, color2):
        return ((color1[0] + color2[0]) / 2,
                (color1[1] + color2[1]) / 2,
                (color1[2] + color2[2]) / 2,
                (color1[3] + color2[3]) / 2 )

    method(Color, Color, Color)
    def max (self, color1, color2):
        return (max( color1[0], color2[0]),
                max( color1[1], color2[1]),
                max( color1[2], color2[2]),
                max( color1[3], color2[3]) )
