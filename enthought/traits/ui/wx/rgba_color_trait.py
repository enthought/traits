#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# 
# Author: David C. Morrill
# Data: 12/22/2004
#------------------------------------------------------------------------------
""" Trait definition for an RGBA-based color, which is either:

* A tuple of the form (*red*,*green*,*blue*,*alpha*), where each component is 
  in the range from 0.0 to 1.0
* An integer which in hexadecimal is of the form 0xAARRGGBB, where AA is alpha,
  RR is red, GG is green, and BB is blue.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api                   import Trait, TraitError
from enthought.traits.trait_base        import SequenceTypes
from enthought.traits.ui.api                import RGBAColorEditor
from enthought.traits.ui.wx.color_trait import standard_colors

#-------------------------------------------------------------------------------
#  Convert a value into an Enable/Kiva color:
#-------------------------------------------------------------------------------

def convert_to_color ( object, name, value ):
    """ Converts a value to an Enable or Kiva color.
    """
    if ((type( value ) in SequenceTypes) and
        (len( value ) == 4) and
        (0.0 <= value[0] <= 1.0) and
        (0.0 <= value[1] <= 1.0) and
        (0.0 <= value[2] <= 1.0) and
        (0.0 <= value[3] <= 1.0)):
        return value
    if type( value ) is int:
        result = ( ((value >> 24) & 0xFF) / 255.0, 
                   ((value >> 16) & 0xFF) / 255.0, 
                   ((value >>  8) & 0xFF) / 255.0,
                    (value & 0xFF)        / 255.0 )
        return result
    raise TraitError

convert_to_color.info = ('a tuple of the form (red,green,blue,alpha), where '
                         'each component is in the range from 0.0 to 1.0, or '
                         'an integer which in hex is of the form 0xAARRGGBB, '
                         'where AA is alpha, RR is red, GG is green, and BB is '
                         'blue')
             
#-------------------------------------------------------------------------------
#  Standard colors:
#-------------------------------------------------------------------------------

# RGBA versions of standard colors
rgba_standard_colors = {}
for name, color in standard_colors.items():
    rgba_standard_colors[ name ] = ( color.Red()   / 255.0, 
                                     color.Green() / 255.0,
                                     color.Blue()  / 255.0, 
                                     1.0 )
rgba_standard_colors[ 'clear' ] = ( 0, 0, 0, 0 )

#-------------------------------------------------------------------------------
#  Define Enable/Kiva specific color traits:
#-------------------------------------------------------------------------------
    
# Trait whose value must be an RGBA color
RGBAColor = Trait( 'white', convert_to_color, rgba_standard_colors, 
                            editor = RGBAColorEditor )

