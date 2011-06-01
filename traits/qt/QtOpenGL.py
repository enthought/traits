from . import qt_api

if qt_api == 'pyqt':
    from PyQt4.QtOpenGL import *
    
else:
    from PySide.QtOpenGL import *
