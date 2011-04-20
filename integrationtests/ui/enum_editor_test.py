#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in /LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: David C. Morrill
# Date: 04/06/2005
# Description: Test the EnumEditor trait editor.
#------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import HasTraits, Trait, Enum, Range

from traitsui.api \
    import EnumEditor

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

values = [ 'one', 'two', 'three', 'four' ]
enum   = Enum( *values )
range  = Range( 1, 4 )

#-------------------------------------------------------------------------------
#  'TestEnumEditor' class:
#-------------------------------------------------------------------------------

class TestEnumEditor ( HasTraits ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    value = Trait( 1, enum, range,
                   editor = EnumEditor( values   = values,
                                        evaluate = int ) )

#-------------------------------------------------------------------------------
#  Run the test:
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    test = TestEnumEditor()
    test.configure_traits()
    test.print_traits()

