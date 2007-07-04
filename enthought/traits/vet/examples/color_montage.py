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
# Description: The 'ColorMontage' traits view definition and handler.
#  Usage is:
#    ColorMontage().edit_traits( context = object_to_edit, ... )
#------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.enable2.traits.ui.wx.enable_rgba_color_editor import \
    EnableRGBAColorEditor
from enthought.traits.ui.api      import Handler, View, Group, Item
from enthought.traits.ui.menu import MenuBar, Menu, Action, Separator
import enthought.traits.ui

#-------------------------------------------------------------------------------
#  'ColorMontage' class:
#-------------------------------------------------------------------------------

class ColorMontage ( Handler ):

    #---------------------------------------------------------------------------
    #  Handles the object's 'rgba_color' trait changing value:
    #---------------------------------------------------------------------------

    def object_rgba_color_changed ( self, info ):
        """ Handles the object's 'rgba_color' trait changing value.
        """
        from enthought.util.wx.clipboard import clipboard
        c = info.object.rgba_color_
        clipboard.data = '0x%02X%02X%02X%02X' % (
            255 - int( 255 * c[3] ),
            int( 255 * c[0] ),
            int( 255 * c[1] ),
            int( 255 * c[2] ) )

    #---------------------------------------------------------------------------
    #  Traits view definition:
    #---------------------------------------------------------------------------

    traits_view = View(
        Group(
            Group(
                Item(
                    editor  = EnableRGBAColorEditor(),
                    name    = 'rgba_color',
                    style   = 'custom',
                    padding = -8
                ),
                Item(
                    editor  = EnableRGBAColorEditor( mode = 'hsv' ),
                    name    = 'rgba_color',
                    style   = 'custom',
                    padding = -8
                ),
                orientation = 'horizontal',
                show_labels = False
            ),
            Group(
                Item(
                    editor  = EnableRGBAColorEditor( mode = 'hsv2' ),
                    name    = 'rgba_color',
                    style   = 'custom',
                    padding = -8
                ),
                Item(
                    editor  = EnableRGBAColorEditor( mode = 'hsv3' ),
                    name    = 'rgba_color',
                    style   = 'custom',
                    padding = -8
                ),
                orientation = 'horizontal',
                show_labels = False
            ),
            show_labels = False
        ),
        title   = 'Color Montage',
        id      = 'enthought.traits.vet.examples.color_montage',
        buttons = [ 'Undo', 'OK', 'Cancel' ]
    )

#-------------------------------------------------------------------------------
#  'ColorMontage' test case:
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    import enthought.traits.vet.person
    ColorMontage().configure_traits( context = {
        'object': enthought.traits.vet.person.Person(),
    } )
