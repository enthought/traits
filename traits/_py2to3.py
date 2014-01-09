""" Helper module, providing a common API for tasks that require a different implementation in python 2 and 3.
"""

from __future__ import division, absolute_import

import sys


if sys.version_info[0] < 3:
    import string
    str_find = string.find
    str_rfind = string.rfind
else:
    str_find = str.find
    str_rfind = str.rfind

if sys.version_info[0] < 3:
    from types import InstanceType,ClassType
    def is_old_style_instance(obj):
        return type(obj) is InstanceType
    def is_old_style_class(obj):
        return type(obj) is ClassType
    def is_InstanceType(obj):
        return obj is InstanceType
    def is_ClassType(obj):
        return obj is ClassType
else:
    def is_old_style_instance(obj):
        return False
    def is_old_style_instance(obj):
        return False
    def is_InstanceType(obj):
        return False
    def is_ClassType(obj):
        return False


if sys.version_info[0] < 3:
    from types import InstanceType
    def type_w_old_style(obj):
        the_type = type(obj)
        if the_type is InstanceType:
            # Old-style class.
            the_type = obj.__class__
        return the_type
else:
    type_w_old_style = type

if sys.version_info[0] < 3:
    from types import ClassType
    ClassTypes    = ( ClassType, type )
else:
    ClassTypes    = ( type, )


import contextlib
if sys.version_info[0] < 3:
    def nested_context_mgrs(*args):
        return contextlib.nested(*args)
else:
    if sys.version_info[:2] < (3,3):
        # ExitStack was introduced in python 3.3. We copy the 3.3 version here
        # to support python 3.2
        class ExitStack(object):
            """Context manager for dynamic management of a stack of exit callbacks
        
            For example:
        
                with ExitStack() as stack:
                    files = [stack.enter_context(open(fname)) for fname in filenames]
                    # All opened files will automatically be closed at the end of
                    # the with statement, even if attempts to open files later
                    # in the list raise an exception
        
            """
            def __init__(self):
                from collections import deque
                self._exit_callbacks = deque()
        
            def pop_all(self):
                """Preserve the context stack by transferring it to a new instance"""
                from collections import deque
                new_stack = type(self)()
                new_stack._exit_callbacks = self._exit_callbacks
                self._exit_callbacks = deque()
                return new_stack
        
            def _push_cm_exit(self, cm, cm_exit):
                """Helper to correctly register callbacks to __exit__ methods"""
                def _exit_wrapper(*exc_details):
                    return cm_exit(cm, *exc_details)
                _exit_wrapper.__self__ = cm
                self.push(_exit_wrapper)
        
            def push(self, exit):
                """Registers a callback with the standard __exit__ method signature
        
                Can suppress exceptions the same way __exit__ methods can.
        
                Also accepts any object with an __exit__ method (registering a call
                to the method instead of the object itself)
                """
                # We use an unbound method rather than a bound method to follow
                # the standard lookup behaviour for special methods
                _cb_type = type(exit)
                try:
                    exit_method = _cb_type.__exit__
                except AttributeError:
                    # Not a context manager, so assume its a callable
                    self._exit_callbacks.append(exit)
                else:
                    self._push_cm_exit(exit, exit_method)
                return exit # Allow use as a decorator
        
            def callback(self, callback, *args, **kwds):
                """Registers an arbitrary callback and arguments.
        
                Cannot suppress exceptions.
                """
                def _exit_wrapper(exc_type, exc, tb):
                    callback(*args, **kwds)
                # We changed the signature, so using @wraps is not appropriate, but
                # setting __wrapped__ may still help with introspection
                _exit_wrapper.__wrapped__ = callback
                self.push(_exit_wrapper)
                return callback # Allow use as a decorator
        
            def enter_context(self, cm):
                """Enters the supplied context manager
        
                If successful, also pushes its __exit__ method as a callback and
                returns the result of the __enter__ method.
                """
                # We look up the special methods on the type to match the with statement
                _cm_type = type(cm)
                _exit = _cm_type.__exit__
                result = _cm_type.__enter__(cm)
                self._push_cm_exit(cm, _exit)
                return result
        
            def close(self):
                """Immediately unwind the context stack"""
                self.__exit__(None, None, None)
        
            def __enter__(self):
                return self
        
            def __exit__(self, *exc_details):
                # We manipulate the exception state so it behaves as though
                # we were actually nesting multiple with statements
                frame_exc = sys.exc_info()[1]
                def _fix_exception_context(new_exc, old_exc):
                    while 1:
                        exc_context = new_exc.__context__
                        if exc_context in (None, frame_exc):
                            break
                        new_exc = exc_context
                    new_exc.__context__ = old_exc
        
                # Callbacks are invoked in LIFO order to match the behaviour of
                # nested context managers
                suppressed_exc = False
                while self._exit_callbacks:
                    cb = self._exit_callbacks.pop()
                    try:
                        if cb(*exc_details):
                            suppressed_exc = True
                            exc_details = (None, None, None)
                    except:
                        new_exc_details = sys.exc_info()
                        # simulate the stack of exceptions by setting the context
                        _fix_exception_context(new_exc_details[1], exc_details[1])
                        if not self._exit_callbacks:
                            raise
                        exc_details = new_exc_details
                return suppressed_exc
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
        def __init__(self,*args):
            super(nested_context_mgrs,self).__init__()
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

if sys.version_info[0] < 3:
    def assertCountEqual(self,itemsA,itemsB):
        self.assertItemsEqual(itemsA,itemsB)
else:
    def assertCountEqual(self,itemsA,itemsB):
        self.assertCountEqual(itemsA,itemsB)
    