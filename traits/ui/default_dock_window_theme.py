#-------------------------------------------------------------------------------
#
#  Copyright (c) 2007, Enthought, Inc.
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
#  Date:   07/14/2007
#
#-------------------------------------------------------------------------------

""" Defines the default DockWindow theme.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from .dock_window_theme import DockWindowTheme

from .theme import Theme

#-------------------------------------------------------------------------------
#  Define the default theme:
#-------------------------------------------------------------------------------

# The original DockWindows UI redone as a theme:
default_dock_window_theme = DockWindowTheme(
    use_theme_color     = False,
    tab_active          = Theme( '@std:tab_active',
                                 label = ( 0, -3 ), content = ( 7, 6, 0, 0 ) ),
    tab_inactive        = Theme( '@std:tab_inactive',
                                 label = ( 0, -1 ), content = ( 5, 0 ) ),
    tab_hover           = Theme( '@std:tab_hover',
                                 label = ( 0, -2 ), content = ( 5, 0 ) ),
    tab_background      = Theme( '@std:tab_background' ),
    tab                 = Theme( '@std:tab',
                                 content = 0, label = ( -7, 0 ) ),
    vertical_splitter   = Theme( '@std:vertical_splitter',
                                 content = 0, label  = ( 0, -25 ) ),
    horizontal_splitter = Theme( '@std:horizontal_splitter',
                                 content = 0, label = ( -24, 0 ) ),
    vertical_drag       = Theme( '@std:vertical_drag',
                                 content = ( 0, 10 ) ),
    horizontal_drag     = Theme( '@std:horizontal_drag',
                                 content = ( 10, 0 ) )
)

