#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines a subclass of the base PyQt color editor factory, for colors
that are represented as tuples of the form ( *red*, *green*, *blue* ), where 
*red*, *green* and *blue* are floats in the range from 0.0 to 1.0.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtGui

from color_editor \
    import ToolkitEditorFactory as EditorFactory
    
from enthought.traits.trait_base \
    import SequenceTypes

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ PyQt factory for editors for RGB colors.
    """
    #---------------------------------------------------------------------------
    #  Gets the PyQt color equivalent of the object trait:
    #---------------------------------------------------------------------------
    
    def to_pyqt_color ( self, editor ):
        """ Gets the PyQt color equivalent of the object trait.
        """
        try:
            color = getattr( editor.object, editor.name + '_' )
        except AttributeError:
            color = getattr( editor.object, editor.name )

        c = QtGui.QColor()
        c.setRgbF(color[0], color[1], color[2])

        return c
 
    #---------------------------------------------------------------------------
    #  Gets the application equivalent of a PyQt value:
    #---------------------------------------------------------------------------
    
    def from_pyqt_color ( self, color ):
        """ Gets the application equivalent of a PyQt value.
        """
        return (color.redF(), color.greenF(), color.blueF())
        
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
