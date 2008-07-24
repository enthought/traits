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
#  Date:   10/21/2004
#
#------------------------------------------------------------------------------

""" Defines the BasicEditorFactory class, which allows creating editor 
    factories that use the same class for creating all editor styles.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------
    
from enthought.traits.api \
    import Any

from enthought.traits.ui.editor_factory \
    import EditorFactory

#-------------------------------------------------------------------------------
#  'BasicEditorFactory' base class:
#-------------------------------------------------------------------------------

class BasicEditorFactory ( EditorFactory ):
    """ Base class for editor factories that use the same class for creating
        all editor styles.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    # Editor class to be instantiated
    klass = Any
    
    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------
    
    def simple_editor ( self, ui, object, name, description, parent ):
        return self.klass( parent,
                           factory     = self, 
                           ui          = ui, 
                           object      = object, 
                           name        = name, 
                           description = description ) 
    
    def custom_editor ( self, ui, object, name, description, parent ):
        return self.klass( parent,
                           factory     = self, 
                           ui          = ui, 
                           object      = object, 
                           name        = name, 
                           description = description ) 
    
    def text_editor ( self, ui, object, name, description, parent ):
        return self.klass( parent,
                           factory     = self, 
                           ui          = ui, 
                           object      = object, 
                           name        = name, 
                           description = description ) 
    
    def readonly_editor ( self, ui, object, name, description, parent ):
        return self.klass( parent,
                           factory     = self, 
                           ui          = ui, 
                           object      = object, 
                           name        = name, 
                           description = description ) 
                           
    #---------------------------------------------------------------------------
    #  Allow an instance to be called:  
    #---------------------------------------------------------------------------
                                      
    def __call__ ( self, *args, **traits ):
        return self.set( **traits )
        
