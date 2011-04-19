import os

qt_api = os.environ.get('QT_API', 'pyqt')

if qt_api == 'pyqt':
    from PyQt4.QtCore import *

    from PyQt4.QtCore import pyqtSignal as Signal
    from PyQt4.Qt import QCoreApplication
    from PyQt4.Qt import Qt

    __version__ = QT_VERSION_STR
    __version_info__ = tuple(map(int, QT_VERSION_STR.split('.')))

else:
    import PySide
    from PySide.QtCore import *

    __version__ = PySide.__version__
    __version_info__ = PySide.__version_info__
