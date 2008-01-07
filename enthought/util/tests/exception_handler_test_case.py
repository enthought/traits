

import sys
import unittest

from enthought.util.ui.exception_handler import ExceptionHandler

class ExceptionHandlerTestCase( unittest.TestCase ):
    
    def test_simple(self):
        try:
            ex_handler = None
            raise Exception, 'test exception'

        except:
            ex_handler = ExceptionHandler(message='Your message here!')
            t,v,tb = sys.exc_info()
            
            self.failUnlessEqual(t, ex_handler.ex_type)
            self.failUnlessEqual(v, ex_handler.ex_value)
            self.failUnlessEqual(tb, ex_handler.ex_traceback)

            text = """Your message here!
Traceback (most recent call last):
  File "%s", line 13, in test_simple
    raise Exception, 'test exception'
Exception: test exception""" % __file__
            self.failUnlessEqual(text, str(ex_handler))
        
        self.failIfEqual(ex_handler, None)
        
        return
    
    def ui_simple_dialog(self):
        try:
            ex_handler = None
            raise Exception, 'test exception'

        except:
            ex_handler = ExceptionHandler(message='Your application message here!')
            ex_handler.configure_traits()
        return
    
    def ui_file_not_found(self):
        try:
            ex_handler = None
            file('foo.bar', 'rb')

        except:
            ex_handler = ExceptionHandler(message='Unable to find your file.')
            ex_handler.configure_traits()
        
        return

    def ui_syntax_error(self):
        try:
            ex_handler = None
            eval('import foo')

        except:
            ex_handler = ExceptionHandler(message='Trouble with your source.')
            ex_handler.configure_traits()
        
        return
    
### EOF
