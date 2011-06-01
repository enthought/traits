from . import qt_api

if qt_api == 'pyqt':
    from PyQt4.QtTest import *
    
else:
    from PySide.QtTest import *
