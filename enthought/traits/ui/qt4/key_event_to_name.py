#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Converts a QKeyEvent to a standardized "name".
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtCore
    
#-------------------------------------------------------------------------------
#  Constants:  
#-------------------------------------------------------------------------------

# Mapping from PyQt special key names to Enable key names
key_map = {
    QtCore.Qt.Key_Backspace: 'Backspace',
    QtCore.Qt.Key_Tab:       'Tab',
    QtCore.Qt.Key_Return:    'Enter',
    QtCore.Qt.Key_Escape:    'Esc',
    QtCore.Qt.Key_Delete:    'Delete',
    #QtCore.Qt.Key_START:     'Start',
    #QtCore.Qt.Key_LBUTTON:   'Left Button',
    #QtCore.Qt.Key_RBUTTON:   'Right Button',
    QtCore.Qt.Key_Cancel:    'Cancel',
    #QtCore.Qt.Key_MBUTTON:   'Middle Button',
    QtCore.Qt.Key_Clear:     'Clear',
    QtCore.Qt.Key_Shift:     'Shift',
    QtCore.Qt.Key_Control:   'Control',
    QtCore.Qt.Key_Menu:      'Menu',
    QtCore.Qt.Key_Pause:     'Pause',
    #QtCore.Qt.Key_CAPITAL:   'Capital',
    QtCore.Qt.Key_PageUp:    'Page Up',
    QtCore.Qt.Key_PageDown:  'Page Down',
    QtCore.Qt.Key_End:       'End',
    QtCore.Qt.Key_Home:      'Home',
    QtCore.Qt.Key_Left:      'Left',
    QtCore.Qt.Key_Up:        'Up',
    QtCore.Qt.Key_Right:     'Right',
    QtCore.Qt.Key_Down:      'Down',
    QtCore.Qt.Key_Select:    'Select',
    QtCore.Qt.Key_Print:     'Print',
    QtCore.Qt.Key_Execute:   'Execute',
    #QtCore.Qt.Key_SNAPSHOT:  'Snapshot',
    QtCore.Qt.Key_Insert:    'Insert',
    QtCore.Qt.Key_Help:      'Help',
    #QtCore.Qt.Key_NUMPAD0:   'Numpad 0',
    #QtCore.Qt.Key_NUMPAD1:   'Numpad 1',
    #QtCore.Qt.Key_NUMPAD2:   'Numpad 2',
    #QtCore.Qt.Key_NUMPAD3:   'Numpad 3',
    #QtCore.Qt.Key_NUMPAD4:   'Numpad 4',
    #QtCore.Qt.Key_NUMPAD5:   'Numpad 5',
    #QtCore.Qt.Key_NUMPAD6:   'Numpad 6',
    #QtCore.Qt.Key_NUMPAD7:   'Numpad 7',
    #QtCore.Qt.Key_NUMPAD8:   'Numpad 8',
    #QtCore.Qt.Key_NUMPAD9:   'Numpad 9',
    #QtCore.Qt.Key_MULTIPLY:  'Multiply',
    #QtCore.Qt.Key_ADD:       'Add',
    #QtCore.Qt.Key_SEPARATOR: 'Separator',
    #QtCore.Qt.Key_SUBTRACT:  'Subtract',
    #QtCore.Qt.Key_DECIMAL:   'Decimal',
    #QtCore.Qt.Key_DIVIDE:    'Divide',
    QtCore.Qt.Key_F1:        'F1',
    QtCore.Qt.Key_F2:        'F2',
    QtCore.Qt.Key_F3:        'F3',
    QtCore.Qt.Key_F4:        'F4',
    QtCore.Qt.Key_F5:        'F5',
    QtCore.Qt.Key_F6:        'F6',
    QtCore.Qt.Key_F7:        'F7',
    QtCore.Qt.Key_F8:        'F8',
    QtCore.Qt.Key_F9:        'F9',
    QtCore.Qt.Key_F10:       'F10',
    QtCore.Qt.Key_F11:       'F11',
    QtCore.Qt.Key_F12:       'F12',
    QtCore.Qt.Key_F13:       'F13',
    QtCore.Qt.Key_F14:       'F14',
    QtCore.Qt.Key_F15:       'F15',
    QtCore.Qt.Key_F16:       'F16',
    QtCore.Qt.Key_F17:       'F17',
    QtCore.Qt.Key_F18:       'F18',
    QtCore.Qt.Key_F19:       'F19',
    QtCore.Qt.Key_F20:       'F20',
    QtCore.Qt.Key_F21:       'F21',
    QtCore.Qt.Key_F22:       'F22',
    QtCore.Qt.Key_F23:       'F23',
    QtCore.Qt.Key_F24:       'F24',
    QtCore.Qt.Key_NumLock:   'Num Lock',
    QtCore.Qt.Key_ScrollLock:'Scroll Lock'
}
        
#-------------------------------------------------------------------------------
#  Converts a keystroke event into a corresponding key name:  
#-------------------------------------------------------------------------------
                
def key_event_to_name ( event ):
    """ Converts a keystroke event into a corresponding key name.
    """
    key_code = event.GetKeyCode()
    if event.ControlDown() and (1 <= key_code <= 26):
        key = chr( key_code + 96 )
    else:
        key = key_map.get( key_code )
        if key is None:
            key = chr( key_code )
    
    name = ''
    if event.AltDown():
        name = 'Alt'
        
    if event.ControlDown():
        name += '-Ctrl'
            
    if event.ShiftDown() and ((name != '') or (len( key ) > 1)):
        name += '-Shift'
        
    if key == ' ':
        key = 'Space'
    
    name += ('-' + key)
    
    if name[:1] == '-':
        return name[1:]
    return name
