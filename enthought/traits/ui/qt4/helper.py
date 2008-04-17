#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines helper functions and classes used to define PyQt-based trait
    editors and trait editor factories.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import os.path

from PyQt4 import QtCore, QtGui

from enthought.traits.api \
    import Enum, CTrait, BaseTraitHandler, TraitError
    
from enthought.traits.ui.ui_traits \
    import SequenceTypes
    
#-------------------------------------------------------------------------------
#  Trait definitions:  
#-------------------------------------------------------------------------------

# Layout orientation for a control and its associated editor
Orientation = Enum( 'horizontal', 'vertical' )

#-------------------------------------------------------------------------------
#  Convert an image file name to a cached QPixmap:
#-------------------------------------------------------------------------------

def pixmap_cache(name):
    """ Return the QPixmap corresponding to a filename.  If the filename does
        not contain a path component then the local 'images' directory is used.
    """
    path, _ = os.path.split(name)
    if not path:
        name = os.path.join(os.path.dirname(__file__), 'images', name)

    pm = QtGui.QPixmap()

    if not QtGui.QPixmapCache.find(name, pm):
        pm.load(name)
        QtGui.QPixmapCache.insert(name, pm)

    return pm

#-------------------------------------------------------------------------------
#  Positions a window on the screen with a specified width and height so that
#  the window completely fits on the screen if possible:
#-------------------------------------------------------------------------------

def position_window ( window, width = None, height = None, parent = None ):
    """ Positions a window on the screen with a specified width and height so
        that the window completely fits on the screen if possible.
    """
    # Get the available geometry of the screen containing the window.
    sgeom = QtGui.QApplication.desktop().availableGeometry(window)
    screen_dx = sgeom.width()
    screen_dy = sgeom.height()

    # Use the frame geometry even though it is very unlikely that the X11 frame
    # exists at this point.
    fgeom = window.frameGeometry()
    width = width or fgeom.width()
    height = height or fgeom.height()

    if parent is None:
        parent = window._parent

    if parent is None:
        # Center the popup on the screen.
        window.move((screen_dx - width) / 2, (screen_dy - height) / 2)
        return

    # Calculate the desired size of the popup control:
    if isinstance(parent, QtGui.QWidget):
        gpos = parent.mapToGlobal(QtCore.QPoint())
        x = gpos.x()
        y = gpos.y()
        cdx = parent.width()
        cdy = parent.height()

        # Get the frame height of the parent and assume that the window will
        # have a similar frame.  Note that we would really like the height of
        # just the top of the frame.
        pw = parent.window()
        fheight = pw.frameGeometry().height() - pw.height()
    else:
        # Special case of parent being a screen position and size tuple (used
        # to pop-up a dialog for a table cell):
        x, y, cdx, cdy = parent

        fheight = 0

    x -= (width - cdx) / 2
    y += cdy + fheight

    # Position the window (making sure it will fit on the screen).
    window.move(max(0, min(x, screen_dx - width)),
                max(0, min(y, screen_dy - height)))
    
#-------------------------------------------------------------------------------
#  Restores the user preference items for a specified UI:
#-------------------------------------------------------------------------------
    
def restore_window ( ui ):
    """ Restores the user preference items for a specified UI.
    """
    prefs = ui.restore_prefs()
    if prefs is not None:
        ui.control.setGeometry( *prefs )
    
#-------------------------------------------------------------------------------
#  Saves the user preference items for a specified UI:
#-------------------------------------------------------------------------------
    
def save_window ( ui ):
    """ Saves the user preference items for a specified UI.
    """
    geom = ui.control.geometry()
    ui.save_prefs( (geom.x(), geom.y(), geom.width(), geom.height()) ) 

#-------------------------------------------------------------------------------
#  Recomputes the mappings for a new set of enumeration values:
#-------------------------------------------------------------------------------
 
def enum_values_changed ( values ):
    """ Recomputes the mappings for a new set of enumeration values.
    """
    
    if isinstance( values, dict ):
        data = [ ( str( v ), n ) for n, v in values.items() ]
        if len( data ) > 0:
            data.sort( lambda x, y: cmp( x[0], y[0] ) )
            col = data[0][0].find( ':' ) + 1
            if col > 0:
                data = [ ( n[ col: ], v ) for n, v in data ]
    elif not isinstance( values, SequenceTypes ):
        handler = values
        if isinstance( handler, CTrait ):
            handler = handler.handler
        if not isinstance( handler, BaseTraitHandler ):
            raise TraitError, "Invalid value for 'values' specified"
        if handler.is_mapped:
            data = [ ( str( n ), n ) for n in handler.map.keys() ]
            data.sort( lambda x, y: cmp( x[0], y[0] ) )
        else:
            data = [ ( str( v ), v ) for v in handler.values ]
    else:
        data = [ ( str( v ), v ) for v in values ]
    
    names           = [ x[0] for x in data ]
    mapping         = {}
    inverse_mapping = {}
    for name, value in data:
        mapping[ name ] = value
        inverse_mapping[ value ] = name
        
    return ( names, mapping, inverse_mapping )  

#-------------------------------------------------------------------------------
#  Safely tries to pop up an FBI window if enthought.debug is installed
#-------------------------------------------------------------------------------

def open_fbi():
    try:
        from enthought.developer.helper.fbi import if_fbi
        if not if_fbi():
            import traceback
            traceback.print_exc()
    except ImportError:
        pass

#-------------------------------------------------------------------------------
#  'IconButton' class:
#-------------------------------------------------------------------------------

class IconButton(QtGui.QPushButton):
    """ The IconButton class is a push button that contains a small image or a
        standard icon provided by the current style.
    """

    def __init__(self, icon, slot):
        """ Initialise the button.  icon is either the name of an image file or
            one of the QtGui.QStyle.SP_* values.
        """
        QtGui.QPushButton.__init__(self)

        # Get the current style.
        sty = QtGui.QApplication.instance().style()

        # Get the minimum icon size to use.
        ico_sz = sty.pixelMetric(QtGui.QStyle.PM_ButtonIconSize)

        if isinstance(icon, basestring):
            pm = pixmap_cache(icon)

            # Increase the icon size to accomodate the image if needed.
            pm_width = pm.width()
            pm_height = pm.height()

            if ico_sz < pm_width:
                ico_sz = pm_width

            if ico_sz < pm_height:
                ico_sz = pm_height

            ico = QtGui.QIcon(pm)
        else:
            ico = sty.standardIcon(icon)

        # Configure the button.
        self.setIcon(ico)
        self.setMaximumSize(ico_sz, ico_sz)
        self.setFlat(True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        QtCore.QObject.connect(self, QtCore.SIGNAL('clicked()'), slot)

#-------------------------------------------------------------------------------
#  Dock-related stubs.
#-------------------------------------------------------------------------------

DockStyle = Enum('horizontal', 'vertical', 'tab', 'fixed')
