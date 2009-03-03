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
from enthought.traits.trait_types import Bool, Any
from enthought.traits.ui.editor_factory import EditorFactory


#-- DateEditor definition ----------------------------------------------------- 
class DateEditor ( EditorFactory ):
    """
    Editor factory for date/time editors. 
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
    
    # Is multiselect enabled for a CustomEditor?
    # If True, then the edited object must be a Date.  If False, then it's
    # a List of Dates.
    multi_select = Bool(False)
    
    # Should users be able to pick future dates when using the CustomEditor?
    allow_future = Bool(True)
    
#-- end DateEditor definition ------------------------------------------------- 


#-- eof ----------------------------------------------------------------------- 
