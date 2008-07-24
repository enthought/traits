#-------------------------------------------------------------------------------
#
#  Copyright (c) 2006, Enthought, Inc.
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
#  Date:   07/26/2006
#
#-------------------------------------------------------------------------------

""" Defines a completely empty editor, intended to be used as a spacer.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtGui

from enthought.traits.ui.qt4.editor \
    import Editor
    
from enthought.traits.ui.qt4.basic_editor_factory \
    import BasicEditorFactory
                                      
#-------------------------------------------------------------------------------
#  'NullEditor' class:
#-------------------------------------------------------------------------------
                               
class NullEditor ( Editor ):
    """ A completely empty editor.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = QtGui.QLabel()
                        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        pass

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------
                
ToolkitEditorFactory = BasicEditorFactory( klass = NullEditor )
                 
#-------------------------------------------------------------------------------
#
#  Copyright (c) 2006, Enthought, Inc.
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
#  Date:   07/26/2006
#
#-------------------------------------------------------------------------------

""" Defines a completely empty editor, intended to be used as a spacer.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtGui

from enthought.traits.ui.qt4.editor \
    import Editor
    
from enthought.traits.ui.qt4.basic_editor_factory \
    import BasicEditorFactory
                                      
#-------------------------------------------------------------------------------
#  'NullEditor' class:
#-------------------------------------------------------------------------------
                               
class NullEditor ( Editor ):
    """ A completely empty editor.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = QtGui.QLabel()
                        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        pass

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------
                
ToolkitEditorFactory = BasicEditorFactory( klass = NullEditor )
                 
