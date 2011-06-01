from . import qt_api

if qt_api == 'pyqt':
    from PyQt4.QtWebKit import *
    
else:
    from PySide.QtWebKit import *
