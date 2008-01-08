#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
# 
# This software is provided without warranty under the terms of the GPL v2
# license.
# 
# Author: Riverbank Computing Limited
# Description: <Enthought pyface package component>
#------------------------------------------------------------------------------


# Standard library imports.
import sys
import code

# Major package imports.
from PyQt4 import QtCore, QtGui

# Enthought library imports.
from enthought.traits.api import Event, implements

# Local imports.
from enthought.pyface.i_python_shell import IPythonShell, MPythonShell
from enthought.pyface.key_pressed_event import KeyPressedEvent
from widget import Widget


class PythonShell(MPythonShell, Widget):
    """ The toolkit specific implementation of a PythonShell.  See the
    IPythonShell interface for the API documentation.
    """

    implements(IPythonShell)

    #### 'IPythonShell' interface #############################################

    command_executed = Event

    key_pressed = Event(KeyPressedEvent)

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    # FIXME v3: Either make this API consistent with other Widget sub-classes
    # or make it a sub-class of HasTraits.
    def __init__(self, parent, **traits):
        """ Creates a new pager. """

        # Base class constructor.
        super(PythonShell, self).__init__(**traits)

        # Create the toolkit-specific control that represents the widget.
        self.control = self._create_control(parent)

        # Set up to be notified whenever a Python statement is executed:
        self.control.exec_callback = self._on_command_executed

    ###########################################################################
    # 'IPythonShell' interface.
    ###########################################################################

    def interpreter(self):
        return self.control.interpreter

    def execute_command(self, command, hidden=True):
        self.control.run(command, hidden)

    ###########################################################################
    # Protected 'IWidget' interface.
    ###########################################################################

    def _create_control(self, parent):
        # FIXME v3: Note that we don't (yet) support DND or the zoom(?) of the
        # wx version.
        return PyShell(parent)


class PyShell(QtGui.QTextEdit):
    """ A simple GUI Python shell until we do something more sophisticated. """

    def __init__(self, parent=None):
        """ Initialise the instance. """

        QtGui.QTextEdit.__init__(self, parent)

        self.setAcceptRichText(False)
        self.setWordWrapMode(QtGui.QTextOption.WrapAnywhere)

        self.interpreter = code.InteractiveInterpreter()

        self.exec_callback = None

        self._line = QtCore.QString()
        self._lines = []
        self._more = False
        self._history = []
        self._pointer = 0
        self._reading = False
        self._point = 0

        # Interpreter prompts.
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = ">>> "

        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = "... "

        # Interpreter banner.
        self.write('Python %s on %s.\n' % (sys.version, sys.platform))
        self.write('Type "copyright", "credits" or "license" for more information.\n')
        self.write(sys.ps1)

    def flush(self):
        """ Emulate a file object. """

        pass

    def isatty(self):
        """ Emulate a file object. """

        return 1

    def readline(self):
        """ Emulate a file object. """

        self._reading = True
        self._clear_line()
        self.moveCursor(QtGui.QTextCursor.EndOfLine)

        while self._reading:
            QtCore.QCoreApplication.processEvents()

        if self._line.length():
            return str(self._line) 

        return '\n'
    
    def write(self, text):
        """ Emulate a file object. """

        self.insertPlainText(text)
        self.ensureCursorVisible()

    def writelines(self, text):
        """ Emulate a file object. """

        map(self.write, text)

    def run(self, command, hidden=False):
        """ Run a (possibly partial) command without displaying anything. """

        self._lines.append(command)
        source = '\n'.join(self._lines)

        # Save the current std* and point them here.
        old_stdin, old_stdout, old_stderr = sys.stdin, sys.stdout, sys.stderr
        sys.stdin = sys.stdout = sys.stderr = self

        self._more = self.interpreter.runsource(source)

        # Restore std* unless the executed changed them.
        if sys.stdin is old_stdin:
            sys.stdin = old_stdin

        if sys.stdout is old_stdout:
            sys.stdout = old_stdout

        if sys.stderr is old_stderr:
            sys.stderr = old_stderr

        if not self._more:
            self._lines = []

            if self.exec_callback:
                self.exec_callback()

        if not hidden:
            self._pointer = 0
            self._history.append(QtCore.QString(command))

            self._clear_line()

            if self._more:
                self.write(sys.ps2)
            else:
                self.write(sys.ps1)

    def keyPressEvent(self, e):
        """ Handle user input a key at a time. """

        text = e.text()

        if text.length() and 32 <= ord(text.toAscii()[0]) < 127:
            self._insert_text(text)
            return

        key = e.key()

        if e.matches(QtGui.QKeySequence.Copy):
            text = self.textCursor().selectedText()
            if not text.isEmpty():
                QtGui.QApplication.clipboard().setText(text)
        elif e.matches(QtGui.QKeySequence.Paste):
            self._insert_text(QtGui.QApplication.clipboard().text())
        elif key == QtCore.Qt.Key_Backspace:
            if self._point:
                cursor = self.textCursor()
                cursor.deletePreviousChar()
                self.setTextCursor(cursor)

                self._point -= 1
                self._line.remove(self._point, 1)
        elif key == QtCore.Qt.Key_Delete:
            cursor = self.textCursor()
            cursor.deleteChar()
            self.setTextCursor(cursor)

            self._line.remove(self._point, 1)
        elif key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            self.write('\n')
            if self._reading:
                self._reading = False
            else:
                self.run(str(self._line))
        elif key == QtCore.Qt.Key_Tab:
            self._insert_text(text)
        elif e.matches(QtGui.QKeySequence.MoveToPreviousChar):
            if self._point:
                self.moveCursor(QtGui.QTextCursor.Left)
                self._point -= 1
        elif e.matches(QtGui.QKeySequence.MoveToNextChar):
            if self._point < self._line.length():
                self.moveCursor(QtGui.QTextCursor.Right)
                self._point += 1
        elif e.matches(QtGui.QKeySequence.MoveToStartOfLine):
            while self._point:
                self.moveCursor(QtGui.QTextCursor.Left)
                self._point -= 1
        elif e.matches(QtGui.QKeySequence.MoveToEndOfLine):
            self.moveCursor(QtGui.QTextCursor.EndOfBlock)
            self._point = self._line.length()
        elif e.matches(QtGui.QKeySequence.MoveToPreviousLine):
            if len(self._history):
                if self._pointer == 0:
                    self._pointer = len(self._history)
                self._pointer -= 1
                self._recall()
        elif e.matches(QtGui.QKeySequence.MoveToNextLine):
            if len(self._history):
                self._pointer += 1
                if self._pointer == len(self._history):
                    self._pointer = 0
                self._recall()
        else:
            e.ignore()

    def focusNextPrevChild(self, next):
        """ Suppress tabbing to the next window in multi-line commands. """

        if next and self._more:
            return False

        return QtGui.QTextEdit.focusNextPrevChild(self, next)

    def mousePressEvent(self, e):
        """
        Keep the cursor after the last prompt.
        """
        if e.button() == QtCore.Qt.LeftButton:
            self.moveCursor(QtGui.QTextCursor.EndOfLine)

    def contentsContextMenuEvent(self, ev):
        """ Suppress the right button context menu. """

        pass

    def _clear_line(self):
        """ Clear the input line buffer. """

        self._line.truncate(0)
        self._point = 0
        
    def _insert_text(self, text):
        """ Insert text at the current cursor position. """

        self.insertPlainText(text)
        self._line.insert(self._point, text)
        self._point += text.length()

    def _recall(self):
        """ Display the current item from the command history. """

        self.moveCursor(QtGui.QTextCursor.EndOfBlock)

        while self._point:
            self.moveCursor(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor)
            self._point -= 1

        self.textCursor().removeSelectedText()

        self._clear_line()
        self._insert_text(self._history[self._pointer])

#### EOF ######################################################################
