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
from enthought.traits.trait_types import Bool
from enthought.traits.ui.editor_factory import EditorFactory
from enthought.traits.ui.toolkit import toolkit_object   


#-- DateEditor definition ----------------------------------------------------- 
class DateEditor ( EditorFactory ):
    """
    Editor factory for date/time editors. 
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
    
    # Custom date editors can operate on a list of Dates, or just one.
    multi_select = Bool(True)
#-- end DateEditor definition ------------------------------------------------- 


#-- eof ----------------------------------------------------------------------- 
