#------------------------------------------------------------------------------
# Copyright (c) 2010, Enthought Inc
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.

#
# Author: Enthought Inc
# Description: Qt API selector. Can be used to switch between pyQt and PySide
#------------------------------------------------------------------------------

import os

def prepare_pyqt4():
    # Set PySide compatible APIs.
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)

qt_api = os.environ.get('QT_API')

if qt_api is None:
    try:
        import PySide
        qt_api = 'pyside'
    except ImportError:
        try:
            prepare_pyqt4()
            import PyQt4
            qt_api = 'pyqt'
        except ImportError:
            raise ImportError('Cannot import PySide or PyQt4')

elif qt_api == 'pyqt':
    prepare_pyqt4()

elif qt_api != 'pyside':
    raise RuntimeError("Invalid Qt API %r, valid values are: 'pyqt' or 'pyside'"
                       % qt_api)
