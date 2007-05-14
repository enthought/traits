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
# Date: 11/22/2004
#------------------------------------------------------------------------------
""" Defines a subclass of the base wxPython color editor factory, for colors
that are represented as tuples of the form ( *red*, *green*, *blue* ), where 
*red*, *green* and *blue* are floats in the range from 0.0 to 1.0.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from color_editor \
    import ToolkitEditorFactory as EditorFactory
    
from enthought.traits.trait_base \
    import SequenceTypes

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython factory for editors for RGB colors.
    """
    #---------------------------------------------------------------------------
    #  Gets the wxPython color equivalent of the object trait:
    #---------------------------------------------------------------------------
    
    def to_wx_color ( self, editor ):
        """ Gets the wxPython color equivalent of the object trait.
        """
        try:
            color = getattr( editor.object, editor.name + '_' )
        except AttributeError:
            color = getattr( editor.object, editor.name )
        return wx.Colour( int( color[0] * 255.0 ), 
                          int( color[1] * 255.0 ), 
                          int( color[2] * 255.0 ) )
 
    #---------------------------------------------------------------------------
    #  Gets the application equivalent of a wxPython value:
    #---------------------------------------------------------------------------
    
    def from_wx_color ( self, color ):
        """ Gets the application equivalent of a wxPython value.
        """
        return ( color.Red()   / 255.0, 
                 color.Green() / 255.0,
                 color.Blue()  / 255.0 )
        
    #---------------------------------------------------------------------------
    #  Returns the text representation of a specified color value:
    #---------------------------------------------------------------------------
  
    def str_color ( self, color ):
        """ Returns the text representation of a specified color value.
        """
        if type( color ) in SequenceTypes:
            return "(%d,%d,%d)" % ( int( color[0] * 255.0 ),
                                    int( color[1] * 255.0 ),
                                    int( color[2] * 255.0 ) )
        return color

