import os

qt_api = os.environ.get('QT_API', 'pyqt')

if qt_api == 'pyqt':
    from PyQt4.QtScript import *
else:
    from PySide.QtScript import *

