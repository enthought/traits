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
A Traits UI editor that wraps a WX calendar panel.
"""
import datetime

from enthought.traits.traits import Property
from enthought.traits.ui.basic_editor_factory import BasicEditorFactory
from enthought.traits.ui.toolkit import toolkit_object   


#-- DateEditor definition ----------------------------------------------------- 
class DateEditor ( BasicEditorFactory ):
    """
    Editor factory for date/time editors.  Generates _DateEditor()s.
    """

    # The editor class to be created:
    klass = Property
    
    #---------------------------------------------------------------------------
    #  Property getters
    #---------------------------------------------------------------------------
    def _get_klass(self):
        """ Returns the editor class to be created.
        """
        return toolkit_object('date_editor:_DateEditor')
#-- end DateEditor definition ------------------------------------------------- 


#-- eof ----------------------------------------------------------------------- 
