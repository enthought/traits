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
# Description: Test 'Person' class for the View Editing Tool
#------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.kiva.traits.kiva_font_trait import KivaFont
from enthought.traits.api    import HasStrictTraits, Trait, Font, Color, \
                                RGBColor, RGBAColor, Str, Range, List, Instance
from enthought.traits.ui.api import CodeEditor, View

#-------------------------------------------------------------------------------
#  'Person' class:
#-------------------------------------------------------------------------------

class Person ( HasStrictTraits ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    name       = Str
    age        = Range( 0, 120 )
    weight     = Range( 0.0, 500.0 )
    eye_color  = Color( 'blue' )
    rgb_color  = RGBColor( 'red' )
    rgba_color = RGBAColor( 'green' )
    sex        = Trait( 'male', 'female' )
    code       = Str( editor = CodeEditor )
    wx_font    = Font
    kiva_font  = KivaFont
    children   = List( Instance( 'Person' ), use_notebook = True )

    #---------------------------------------------------------------------------
    #  Traits view definition:
    #---------------------------------------------------------------------------

    traits_view = View( 'name', 'age', 'weight' )


