#-------------------------------------------------------------------------------
#  
#  Written by: David C. Morrill
#  
#  Date: 09/22/2005
#  
#  (c) Copyright 2005 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------
""" Converts a wx.KeyEvent to a standardized "name".
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx
    
#-------------------------------------------------------------------------------
#  Constants:  
#-------------------------------------------------------------------------------
        
# Mapping from wxPython special key names to Enable key names
key_map = {
    wx.WXK_BACK:      'Backspace',
    wx.WXK_TAB:       'Tab',
    wx.WXK_RETURN:    'Enter',
    wx.WXK_ESCAPE:    'Esc',
    wx.WXK_DELETE:    'Delete',
    wx.WXK_START:     'Start',
    wx.WXK_LBUTTON:   'Left Button',
    wx.WXK_RBUTTON:   'Right Button',
    wx.WXK_CANCEL:    'Cancel',
    wx.WXK_MBUTTON:   'Middle Button',
    wx.WXK_CLEAR:     'Clear',
    wx.WXK_SHIFT:     'Shift',
    wx.WXK_CONTROL:   'Control',
    wx.WXK_MENU:      'Menu',
    wx.WXK_PAUSE:     'Pause',
    wx.WXK_CAPITAL:   'Capital',
    wx.WXK_PRIOR:     'Page Up',
    wx.WXK_NEXT:      'Page Down',
    wx.WXK_END:       'End',
    wx.WXK_HOME:      'Home',
    wx.WXK_LEFT:      'Left',
    wx.WXK_UP:        'Up',
    wx.WXK_RIGHT:     'Right',
    wx.WXK_DOWN:      'Down',
    wx.WXK_SELECT:    'Select',
    wx.WXK_PRINT:     'Print',
    wx.WXK_EXECUTE:   'Execute',
    wx.WXK_SNAPSHOT:  'Snapshot',
    wx.WXK_INSERT:    'Insert',
    wx.WXK_HELP:      'Help',
    wx.WXK_NUMPAD0:   'Numpad 0',
    wx.WXK_NUMPAD1:   'Numpad 1',
    wx.WXK_NUMPAD2:   'Numpad 2',
    wx.WXK_NUMPAD3:   'Numpad 3',
    wx.WXK_NUMPAD4:   'Numpad 4',
    wx.WXK_NUMPAD5:   'Numpad 5',
    wx.WXK_NUMPAD6:   'Numpad 6',
    wx.WXK_NUMPAD7:   'Numpad 7',
    wx.WXK_NUMPAD8:   'Numpad 8',
    wx.WXK_NUMPAD9:   'Numpad 9',
    wx.WXK_MULTIPLY:  'Multiply',
    wx.WXK_ADD:       'Add',
    wx.WXK_SEPARATOR: 'Separator',
    wx.WXK_SUBTRACT:  'Subtract',
    wx.WXK_DECIMAL:   'Decimal',
    wx.WXK_DIVIDE:    'Divide',
    wx.WXK_F1:        'F1',
    wx.WXK_F2:        'F2',
    wx.WXK_F3:        'F3',
    wx.WXK_F4:        'F4',
    wx.WXK_F5:        'F5',
    wx.WXK_F6:        'F6',
    wx.WXK_F7:        'F7',
    wx.WXK_F8:        'F8',
    wx.WXK_F9:        'F9',
    wx.WXK_F10:       'F10',
    wx.WXK_F11:       'F11',
    wx.WXK_F12:       'F12',
    wx.WXK_F13:       'F13',
    wx.WXK_F14:       'F14',
    wx.WXK_F15:       'F15',
    wx.WXK_F16:       'F16',
    wx.WXK_F17:       'F17',
    wx.WXK_F18:       'F18',
    wx.WXK_F19:       'F19',
    wx.WXK_F20:       'F20',
    wx.WXK_F21:       'F21',
    wx.WXK_F22:       'F22',
    wx.WXK_F23:       'F23',
    wx.WXK_F24:       'F24',
    wx.WXK_NUMLOCK:   'Num Lock',
    wx.WXK_SCROLL:    'Scroll Lock'
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

