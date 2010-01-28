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
#  Date:   07/19/2005
#
#------------------------------------------------------------------------------

""" Defines the editor factory used to wrap a non-Traits based custom control.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ...api import Callable, Tuple, Property

from ..basic_editor_factory import BasicEditorFactory
                                      
from ..toolkit import toolkit_object   

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( BasicEditorFactory ):
    """ Editor factory for custom editors.
    """
    # Editor class to be instantiated.
    klass = Property
    
    # Factory function used to create the custom control
    factory = Callable
    
    # Arguments to be passed to the user's custom editor factory
    args    = Tuple
    
    #---------------------------------------------------------------------------
    #  Initializes the object:  
    #---------------------------------------------------------------------------
        
    def __init__ ( self, *args, **traits ):
        if len( args ) >= 1:
            self.factory = args[0]
            self.args    = args[1:]
        super( ToolkitEditorFactory, self ).__init__( **traits )  
    
    #---------------------------------------------------------------------------
    #  Property getters
    #---------------------------------------------------------------------------
    def _get_klass(self):
        """ Returns the editor class to be created.
        """
        return toolkit_object('custom_editor:CustomEditor')

# Define the CustomEditor class.    
CustomEditor = ToolkitEditorFactory

### EOF #######################################################################
