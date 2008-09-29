#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#  
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#  
#  Author: David C. Morrill
#  Date:   11/22/2004
#
#------------------------------------------------------------------------------

""" Defines a subclass of the base color editor factory, for colors
    that are represented as tuples of the form ( *red*, *green*, *blue* ), 
    where *red*, *green* and *blue* are floats in the range from 0.0 to 1.0.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from color_editor \
    import ToolkitEditorFactory as EditorFactory
    
from enthought.traits.trait_base \
    import SequenceTypes

from enthought.traits.ui.toolkit \
    import toolkit_object

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ Factory for editors for RGB colors.
    """
    pass
    
# Define the ColorEditor class
try:
    RGBColorEditor = toolkit_object('rgb_color_editor:ToolkitEditorFactory')
except:
    RGBColorEditor = ToolkitEditorFactory
