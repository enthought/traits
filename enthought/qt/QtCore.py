import os

qt_api = os.environ.get('QT_API', 'pyqt')

if qt_api == 'pyqt':
    from PyQt4.QtCore import *

    from PyQt4.QtCore import pyqtSignal as Signal
    from PyQt4.Qt import QCoreApplication
    from PyQt4.Qt import Qt

else:
    from PySide.QtCore import *
