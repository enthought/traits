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
#  Author: Judah De Paula
#  Date:   10/7/2008
#
#------------------------------------------------------------------------------
"""
A Traits UI editor that wraps a WX timer control.
"""
import datetime

from enthought.traits.api import Property
from enthought.traits.ui.basic_editor_factory import BasicEditorFactory
from enthought.traits.ui.toolkit import toolkit_object   


#-- TimeEditor definition ----------------------------------------------------- 
class TimeEditor ( BasicEditorFactory ):
    """
    Editor factory for time editors.  Generates _TimeEditor()s.
    """

    # The editor class to be created:
    klass = Property
    
    #---------------------------------------------------------------------------
    #  Property getters
    #---------------------------------------------------------------------------
    def _get_klass(self):
        """ Returns the editor class to be created.
        """
        return toolkit_object('time_editor:_TimeEditor')
#-- end TimeEditor definition ------------------------------------------------- 


#-- eof ----------------------------------------------------------------------- 
