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

from __future__ import absolute_import

from ...api import Bool 

from ..toolkit import toolkit_object

# CIRCULAR IMPORT FIXME: Importing from the source rather than traits.ui.api
# to avoid circular imports, as this EditorFactory will be part of 
# traits.ui.api as well.     
from ..view import View

from ..editor_factory import EditorFactory
    
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
# The function will try to return the toolkit-specific editor factory (located 
# in enthought.traits.ui.<toolkit>.color_editor, and if none is found, the
# ToolkitEditorFactory declared here is returned.
def ColorEditor(*args, **traits):
    """ Returns an instance of the toolkit-specific editor factory declared in 
    enthought.traits.ui.<toolkit>.color_editor. If such an editor factory 
    cannot be located, an instance of the abstract ToolkitEditorFactory 
    declared in enthought.traits.ui.editors.color_editor is returned.

    Parameters 
    ----------
    \*args, \*\*traits
        arguments and keywords to be passed on to the editor 
        factory's constructor. 
    """
    
    try: 
        return toolkit_object('color_editor:ToolkitEditorFactory', True)(*args,
                                                                    **traits)
    except:
        return ToolkitEditorFactory(*args, **traits)

## EOF #######################################################################
