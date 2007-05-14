#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# 
# Author: David C. Morrill
# Date: 01/21/2005
# Description: Defines the 'ColorInfo' class used in the 'VET" tool
#  'color_clipboard.py'
#------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api import HasStrictTraits, RGBAColor, Enum

#-------------------------------------------------------------------------------
#  'ColorInfo' class:
#-------------------------------------------------------------------------------

class ColorInfo ( HasStrictTraits ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
    
    color  = RGBAColor
    format = Enum( 'Web', 'Enable', 'wxPython' )    
