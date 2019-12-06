""" Helper module, providing a common API for tasks that require a different implementation in python 2 and 3.
"""

from __future__ import division, absolute_import

import contextlib

import six

if six.PY2:
    def nested_context_mgrs(*args):
        return contextlib.nested(*args)
else:
    ExitStack = contextlib.ExitStack

    class nested_context_mgrs(ExitStack):
        """ Emulation of python 2's :py:class:`contextlib.nested`.

        It has gone from python 3 due to it's deprecation status
        in python 2.

        Note that :py:class:`contextlib.nested` was deprecated for
        a reason: It has issues with context managers that fail
        during init. The same caveats also apply here.
        So do not use this unless really necessary!
        """

        def __init__(self, *args):
            super(nested_context_mgrs, self).__init__()
            self._ctxt_mgrs = args

        def __enter__(self):
            ret = []
            try:
                for mgr in self._ctxt_mgrs:
                    ret.append(self.enter_context(mgr))
            except:
                self.close()
                raise
            return tuple(ret)
