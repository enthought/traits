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

""" Defines the theme style information for a DockWindow and its components.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ..api import HasPrivateTraits, Bool

from .ui_traits import Image, ATheme

#-------------------------------------------------------------------------------
#  'DockWindowTheme' class:
#-------------------------------------------------------------------------------

class DockWindowTheme ( HasPrivateTraits ):
    """ Defines the theme style information for a DockWindow and its components.
    """

    #-- Public Trait Definitions -----------------------------------------------

    # Use the theme background color as the DockWindow background color?
    use_theme_color = Bool( True )

    # Draw notebook tabs at the top (True) or the bottom (False)?
    tabs_at_top = Bool( True )

    # Active tab theme:
    tab_active = ATheme

    # Inactive tab theme:
    tab_inactive = ATheme

    # Optional image to use for right edge of rightmost inactive tab:
    tab_inactive_edge = Image

    # Tab hover theme (used for inactive tabs):
    tab_hover = ATheme

    # Optional image to use for right edge of rightmost hover tab:
    tab_hover_edge = Image

    # Tab background theme:
    tab_background = ATheme

    # Tab theme:
    tab = ATheme

    # Vertical splitter bar theme:
    vertical_splitter = ATheme

    # Horizontal splitter bar theme:
    horizontal_splitter = ATheme

    # Vertical drag bar theme:
    vertical_drag = ATheme

    # Horizontal drag bar theme:
    horizontal_drag = ATheme

#-------------------------------------------------------------------------------
#  Define the default theme:
#-------------------------------------------------------------------------------

# The current default DockWindow theme:
_dock_window_theme = None

# Gets/Sets the default DockWindow theme:
def dock_window_theme ( theme = None ):
    global _dock_window_theme

    if _dock_window_theme is None:
        from .default_dock_window_theme import default_dock_window_theme

        _dock_window_theme = default_dock_window_theme

    old_theme = _dock_window_theme
    if theme is not None:
        _dock_window_theme = theme

    return old_theme

