#-------------------------------------------------------------------------------
#
#  Written by: David C. Morrill
#
#  Date: 03/02/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines an editor for playing animated GIF files.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

# Define the wx version dependent version of the editor:
if wx.__version__[:3] == '2.6':
    from animated_gif_editor_26 import AnimatedGIFEditor
else:    
    from animated_gif_editor_28 import AnimatedGIFEditor

