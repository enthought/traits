#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the key binding editor for use with the KeyBinding class. This is a 
specialized editor used to associate a particular key with a control (i.e., the
key binding editor).
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtCore, QtGui

from enthought.traits.api \
    import Bool, Event

from editor \
    import Editor
    
from basic_editor_factory \
    import BasicEditorFactory
    
from key_event_to_name \
    import key_event_to_name
                                      
#-------------------------------------------------------------------------------
#  'KeyBindingEditor' class:
#-------------------------------------------------------------------------------
                               
class KeyBindingEditor ( Editor ):
    """ An editor for modifying bindings of keys to controls.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    # Does the editor's control have focus currently?
    has_focus = Bool(False)
    
    # Keyboard event
    key = Event

    # Clear field event
    clear = Event

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init (self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = KeyBindingCtrl(self, parent)

    #---------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #---------------------------------------------------------------------------
  
    def update_object ( self, event ):
        """ Handles the user entering input data in the edit control.
        """
        try:
            self.value = value = key_event_to_name( event )
            self._binding.text = value
        except:
            pass
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        self.control.setText(self.value)

    #---------------------------------------------------------------------------
    #  Updates the current focus setting of the control:  
    #---------------------------------------------------------------------------
    
    def update_focus ( self, has_focus ):
        """ Updates the current focus setting of the control.
        """
        if has_focus:
            self._binding.border_size     = 1
            self.object.owner.focus_owner = self._binding
        
    #---------------------------------------------------------------------------
    #  Handles a keyboard event:   
    #---------------------------------------------------------------------------
    
    def _key_changed ( self, event ):
        """ Handles a keyboard event.
        """
        binding     = self.object
        key_name    = key_event_to_name( event )
        cur_binding = binding.owner.key_binding_for( binding, key_name )
        if cur_binding is not None:
            if QtGui.QMessageBox.question(self.control,
                    "Duplicate Key Definition",
                    "'%s' has already been assigned to '%s'.\n"
                    "Do you wish to continue?" % (key_name,
                        cur_binding.description),
                     QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                     QtGui.QMessageBox.No) != QtGui.QMessageBox.Yes:
                return
                
        self.value = key_name

    #---------------------------------------------------------------------------
    #  Handles a clear field event:
    #---------------------------------------------------------------------------

    def _clear_changed ( self ):
        """ Handles a clear field event.
        """
        self.value = ''

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------
                
ToolkitEditorFactory = BasicEditorFactory( klass = KeyBindingEditor )
        
#-------------------------------------------------------------------------------
#  'KeyBindingCtrl' class:
#-------------------------------------------------------------------------------

class KeyBindingCtrl(QtGui.QLabel):
    """ PyQt control for editing key bindings.
    """
    #---------------------------------------------------------------------------
    #  Initialize the object:
    #---------------------------------------------------------------------------
    
    def __init__(self, editor, parent):

        QtGui.QLabel.__init__(self, parent)

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setIndent(4)
        self.setMinimumWidth(160)

        pal = QtGui.QPalette(self.palette())
        pal.setColor(QtGui.QPalette.Window, QtCore.Qt.white)
        self.setPalette(pal)
        self.setAutoFillBackground(True)

        # Save the reference to the controlling editor object:
        self.editor = editor
        
        # Indicate we don't have the focus right now:
        editor.has_focus = False

    #---------------------------------------------------------------------------
    #  Handle keyboard keys being pressed:
    #---------------------------------------------------------------------------
           
    def keyPressEvent(self, event):
        """ Handle keyboard keys being pressed.
        """
        # Ignore presses of the control and shift keys.
        if event.key() not in (QtCore.Qt.Key_Control, QtCore.Qt.Key_Shift):
            self.editor.key = event

    #---------------------------------------------------------------------------
    #  Do a GUI toolkit specific screen update:
    #---------------------------------------------------------------------------

    def paintEvent(self, event):
        """ Updates the screen.
        """
        QtGui.QLabel.paintEvent(self, event)

        w = self.width()
        h = self.height()
        p = QtGui.QPainter(self)

        if self.editor.has_focus:
            p.setRenderHint(QtGui.QPainter.Antialiasing, True)
            pen = QtGui.QPen(QtCore.Qt.red)
            pen.setWidth(2)
            p.setPen(pen)
            p.drawRect(1, 1, w - 2, h - 2)
        else:
            p.setPen(QtCore.Qt.black)
            p.drawRect(0, 0, w - 1, h - 1)

        p.end()

    #---------------------------------------------------------------------------
    #  Handles getting/losing the focus:
    #---------------------------------------------------------------------------
    
    def focusInEvent(self, event):
        """ Handles getting the focus.
        """
        self.editor.has_focus = True
        self.update()

    def focusOutEvent(self, event):  
        """ Handles losing the focus.
        """
        self.editor.has_focus = False
        self.update()

    #---------------------------------------------------------------------------
    #  Handles the user double clicking the control to clear its contents:
    #---------------------------------------------------------------------------

    def mouseDoubleClickEvent(self, event):
        """ Handles the user double clicking the control to clear its contents.
        """
        self.editor.clear = True
