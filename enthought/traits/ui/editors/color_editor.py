#------------------------------------------------------------------------------
#
#  Copyright (c) 2008, Enthought, Inc.
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
#  Date:   10/21/2004
#
#------------------------------------------------------------------------------

""" Defines the color editor factory for the all traits toolkit backends.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import Bool

# CIRCULAR IMPORT FIXME: Importing from the source rather than traits.ui.api
# to avoid circular imports, as this EditorFactory will be part of 
# traits.ui.api as well.     
from enthought.traits.ui.view \
    import View

from enthought.traits.ui.editor_factory \
    import EditorFactory
    
#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ Editor factory for color editors.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # Is the underlying color trait mapped?
    mapped = Bool( True )
    
    #---------------------------------------------------------------------------
    #  Traits view definition:  
    #---------------------------------------------------------------------------
    
    traits_view = View( [ 'mapped{Is value mapped?}', '|[]>' ] )    
    
    
# Define the ColorEditor class
ColorEditor = ToolkitEditorFactory

## EOF #######################################################################