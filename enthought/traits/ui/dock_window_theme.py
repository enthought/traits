#-------------------------------------------------------------------------------
#  
#  Defines the theme style information for a DockWindow and its components.
#
#  Written by: David C. Morrill  
#  
#  Date: 07/14/2007
#  
#  (c) Copyright 2007 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

""" Defines the theme style information for a DockWindow and its components.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import HasPrivateTraits, Bool
    
from ui_traits \
    import Image, ATheme
    
from theme \
    import Theme

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
    tab_active = ATheme( Theme( 'tab_active', offset = ( 0, -2 ) ) )
    
    # Inactive tab theme:
    tab_inactive = ATheme( Theme( 'tab_inactive', offset = ( 0, -2 ) ) ) 
                          
    # Optional image to use for right edge of rightmost inactive tab:                                
    tab_inactive_edge = Image                                
    
    # Tab hover theme (used for inactive tabs):
    tab_hover = ATheme( Theme( 'tab_hover', offset = ( 0, -2 ) ) )
                          
    # Optional image to use for right edge of rightmost hover tab:                                
    tab_hover_edge = Image                                
    
    # Tab background theme:
    tab_background = ATheme( Theme( 'tab_background' ) )
    
    # Tab theme:
    tab = ATheme( Theme( 'tab', margins = ( -3, 1, 1, 1 ), 
                                offset  = ( -5, 0 ) ) )
    
    # Vertical splitter bar theme:
    vertical_splitter = ATheme( Theme( 'vertical_splitter', 
                                    alignment = 'center', offset = ( -1, 0 ) ) )
    
    # Horizontal splitter bar theme:
    horizontal_splitter = ATheme( Theme( 'horizontal_splitter', 
                                         alignment = 'center' ) )
    
    # Vertical drag bar theme:
    vertical_drag = ATheme( Theme( 'vertical_drag', margins = ( 0, 10 ) ) )
    
    # Horizontal drag bar theme:
    horizontal_drag = ATheme( Theme( 'horizontal_drag', margins = ( 10, 0 ) ) )

#-------------------------------------------------------------------------------
#  Define the default theme:
#-------------------------------------------------------------------------------
       
# Original DockWindows UI redone as a theme:
default_dock_window_theme = DockWindowTheme(
    use_theme_color     = False,
    tab_active          = Theme( 'std_tab_active',   offset  = ( 0, -3 ), 
                                                     margins = ( 7, 6, 0, 0 ) ),
    tab_inactive        = Theme( 'std_tab_inactive', offset  = ( 0, -1 ),
                                                     margins = ( 5, 0 ) ),
    tab_hover           = Theme( 'std_tab_hover',    offset  = ( 0, -2 ),
                                                     margins = ( 5, 0 ) ),
    tab_background      = Theme( 'std_tab_background' ),
    tab                 = Theme( 'std_tab', margins = 0, 
                                            offset  = ( -4, 0 ) ),
    vertical_splitter   = Theme( 'std_vertical_splitter', margins = 0, 
                                                          offset = ( 0, -25 ) ), 
    horizontal_splitter = Theme( 'std_horizontal_splitter', margins = 0, 
                                                          offset = ( -24, 0 ) ), 
    vertical_drag       = Theme( 'std_vertical_drag',   margins = ( 0, 10 ) ),
    horizontal_drag     = Theme( 'std_horizontal_drag', margins = ( 10, 0 ) )
)
    
# Alternate theme with white/grey 3D tabs:
white_dock_window_theme = DockWindowTheme(
    use_theme_color     = True,
    tab_active          = Theme( 'w_tab_active',   margins = ( 3, 0 ), 
                                                   offset  = ( 0, -4 ) ),
    tab_inactive        = Theme( 'w_tab_inactive', margins = ( 3, 0 ),
                                                   offset  = ( 1, -2 ) ),
    tab_hover           = Theme( 'w_tab_hover',    margins = ( 3, 0 ),
                                                   offset  = ( 1, -2 ) ),
    tab_background      = Theme( 'w_tab_background', margins = 0 ),
    tab                 = Theme( 'w_tab', margins = ( -4, -5, -4, 2 ), 
                                          offset  = ( 4, 0 ) ),
    vertical_splitter   = Theme( 'w_vertical_splitter', margins = 0,
                                  alignment = 'center', offset = ( 0, 0 ) ), 
    horizontal_splitter = Theme( 'w_horizontal_splitter', margins = 0, 
                                 alignment = 'center', offset = ( 0, -1 ) ), 
    vertical_drag       = Theme( 'w_vertical_drag',   margins = ( 0, 4 ) ),
    horizontal_drag     = Theme( 'w_horizontal_drag', margins = ( 4, 0 ) )
)
    
# Alternate theme with white/grey 3D tabs at the bottom:
white_bottom_dock_window_theme = DockWindowTheme(
    use_theme_color     = True,
    tabs_at_top         = False,
    tab_active          = Theme( 'w_tab_active_b',     margins = ( 3, 0 ), 
                                                       offset  = ( 0, -1 ) ),
    tab_inactive        = Theme( 'w_tab_inactive_b',   margins = ( 3, 0 ),
                                                       offset  = ( 1, -1 ) ),
    tab_hover           = Theme( 'w_tab_hover_b',      margins = ( 3, 0 ),
                                                       offset  = ( 0, -1 ) ),
    tab_background      = Theme( 'w_tab_background_b', margins = 0 ),
    tab                 = Theme( 'w_tab_b', margins = ( -4, -3, 1, -3 ), 
                                            offset  = ( 3, 0 ) ),
    vertical_splitter   = Theme( 'w_vertical_splitter',   margins = 0,
                                  alignment = 'center',   offset = ( 0, 0 ) ), 
    horizontal_splitter = Theme( 'w_horizontal_splitter', margins = 0, 
                                 alignment = 'center', offset = ( 0, -1 ) ), 
    vertical_drag       = Theme( 'w_vertical_drag',    margins = ( 0, 4 ) ),
    horizontal_drag     = Theme( 'w_horizontal_drag',  margins = ( 4, 0 ) )
)
    
# Alternate theme with blue/grey 2D tabs:
blue_dock_window_theme = DockWindowTheme(
    use_theme_color     = True,
    tab_active          = Theme( 'blue_tab_active',     margins = ( 3, 0 ), 
                                                        offset  = ( 0, -3 ) ),
    tab_inactive        = Theme( 'blue_tab_inactive',   margins = ( 3, 0 ),
                                                        offset  = ( 1, -2 ) ),
    tab_hover           = Theme( 'blue_tab_hover',      margins = ( 3, 0 ),
                                                        offset  = ( 1, -2 ) ),
    tab_background      = Theme( 'blue_tab_background', margins = 0 ),
    tab                 = Theme( 'blue_tab', margins = ( -3, -3, -3, 3 ), 
                                             offset  = ( 3, 0 ) ),
    tab_inactive_edge   = 'blue_tab_inactive_edge',
    tab_hover_edge      = 'blue_tab_hover_edge',
    vertical_splitter   = Theme( 'w_vertical_splitter',   margins = 0,
                                  alignment = 'center',   offset = ( 0, 0 ) ), 
    horizontal_splitter = Theme( 'w_horizontal_splitter', margins = 0, 
                                 alignment = 'center',    offset = ( 0, -1 ) ), 
    vertical_drag       = Theme( 'w_vertical_drag',       margins = ( 0, 4 ) ),
    horizontal_drag     = Theme( 'w_horizontal_drag',     margins = ( 4, 0 ) )
)
    
# Alternate theme with tan 2D tabs:
tan_dock_window_theme = DockWindowTheme(
    use_theme_color     = True,
    tab_active          = Theme( 't_tab_active',     margins = ( 3, 0 ), 
                                                     offset  = ( 0, -3 ) ),
    tab_inactive        = Theme( 't_tab_inactive',   margins = ( 3, 0 ),
                                                     offset  = ( 1, -1 ) ),
    tab_hover           = Theme( 't_tab_hover',      margins = ( 3, 0 ),
                                                     offset  = ( 1, -1 ) ),
    tab_background      = Theme( 't_tab_background', margins = 0 ),
    tab                 = Theme( 't_tab', margins = ( -3, -3, -3, 3 ), 
                                          offset  = ( 3, 0 ) ),
    tab_inactive_edge   = 't_tab_inactive_edge',
    vertical_splitter   = Theme( 't_vertical_splitter',   margins = 0,
                                  alignment = 'center',   offset = ( 0, 0 ) ), 
    horizontal_splitter = Theme( 't_horizontal_splitter', margins = 0, 
                                 alignment = 'center',    offset = ( 0, 0 ) ), 
    vertical_drag       = Theme( 't_vertical_drag',       margins = ( 0, 4 ) ),
    horizontal_drag     = Theme( 't_horizontal_drag',     margins = ( 4, 0 ) )
)
    
# Alternate theme with tan 2D tabs:
tan2_dock_window_theme = DockWindowTheme(
    use_theme_color     = True,
    tab_active          = Theme( 't2_tab_active',     margins = ( 3, 0 ), 
                                                      offset  = ( 0, -3 ) ),
    tab_inactive        = Theme( 't2_tab_inactive',   margins = ( 3, 0 ),
                                                      offset  = ( 1, -1 ) ),
    tab_hover           = Theme( 't2_tab_hover',      margins = ( 3, 0 ),
                                                      offset  = ( 0, -1 ) ),
    tab_background      = Theme( 't2_tab_background', margins = 0 ),
    tab                 = Theme( 't2_tab', margins = ( -3, -3, -3, 3 ), 
                                           offset  = ( 3, 0 ) ),
    tab_inactive_edge   = 't2_tab_inactive_edge',
    vertical_splitter   = Theme( 't2_vertical_splitter', margins = 0,
                                  alignment = 'center',  offset  = ( 0, 0 ) ), 
    horizontal_splitter = Theme( 't2_horizontal_splitter', margins = 0, 
                                 alignment = 'center', offset = ( 0, 0 ) ), 
    vertical_drag       = Theme( 't_vertical_drag',   margins = ( 0, 4 ) ),
    horizontal_drag     = Theme( 't_horizontal_drag', margins = ( 4, 0 ) )
)
    
# Alternate theme with floating 3D button tabs:
button_dock_window_theme = DockWindowTheme(
    use_theme_color     = True,
    tab_active          = Theme( 'btn_tab_active',   margins = ( 0, 0 ), 
                                                     offset  = ( 2, -1 ) ),
    tab_inactive        = Theme( 'btn_tab_inactive', margins = ( 0, 0 ),
                                                     offset  = ( 1, -2 ) ),
    tab_hover           = Theme( 'btn_tab_hover',    margins = ( 0, 0 ),
                                                     offset  = ( 1, -2 ) ),
    tab_background      = Theme( 'btn_tab_background', margins = 0 ),
    tab                 = Theme( 'btn_tab', margins = ( 2, 2 ),
                                            offset  = ( -7, 0 ) ),
    vertical_splitter   = Theme( 'w_vertical_splitter', margins = 0,
                                  alignment = 'center', offset = ( 0, 0 ) ), 
    horizontal_splitter = Theme( 'w_horizontal_splitter', margins = 0, 
                                 alignment = 'center', offset = ( 0, -1 ) ), 
    vertical_drag       = Theme( 'w_vertical_drag',   margins = ( 0, 4 ) ),
    horizontal_drag     = Theme( 'w_horizontal_drag', margins = ( 4, 0 ) )
)
    
# Alternate tan theme with floating flat button tabs:
tan_button_dock_window_theme = DockWindowTheme(
    use_theme_color     = True,
    tab_active          = Theme( 'tbtn_tab_active',   margins = ( 0, 0 ), 
                                                      offset  = ( 2, -1 ) ),
    tab_inactive        = Theme( 'tbtn_tab_inactive', margins = ( 0, 0 ),
                                                      offset  = ( 2, -1 ) ),
    tab_hover           = Theme( 'tbtn_tab_hover',    margins = ( 0, 0 ),
                                                      offset  = ( 2, -1 ) ),
    tab_background      = Theme( 'tbtn_tab_background', margins = 0 ),
    tab                 = Theme( 'tbtn_tab', margins = ( 2, 2 ),
                                             offset  = ( -5, 0 ) ),
    vertical_splitter   = Theme( 'tbtn_vertical_splitter', margins = 0,
                                  alignment = 'center', offset = ( 0, 0 ) ), 
    horizontal_splitter = Theme( 'tbtn_horizontal_splitter', margins = 0, 
                                 alignment = 'center', offset = ( 0, 0 ) ), 
    vertical_drag       = Theme( 'tbtn_vertical_drag',   margins = ( 0, 4 ) ),
    horizontal_drag     = Theme( 'tbtn_horizontal_drag', margins = ( 4, 0 ) )
)

# Set the default DockWindow theme:
def dock_window_theme ( theme = None ):
    global default_dock_window_theme
    
    old_theme = default_dock_window_theme
    if theme is not None:
        default_dock_window_theme = theme
        
    return old_theme
    
