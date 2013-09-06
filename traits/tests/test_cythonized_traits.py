try:
    import cython
    no_cython = False
except ImportError:
    no_cython = True


from ..testing.unittest_tools import unittest, UnittestTools

def has_no_compiler():
    if no_cython:
        return True
    code = "return 1+1"
    try:
        result = cython.inline(code)
        return False
    except:
        return True

def cython_version():
    if no_cython:
        return None
    from Cython.Compiler.Version import version
    return tuple(int(v) for v in version.split('.'))

SKIP_TEST = has_no_compiler()

class CythonizedTraitsTestCase(unittest.TestCase, UnittestTools):


    @unittest.skipIf(SKIP_TEST, 'Missing Cython and/or compiler')
    def test_simple_default_methods(self):

        code =  """
from traits.api import HasTraits, Str

class Test(HasTraits):
    name = Str

    def _name_default(self):
        return 'Joe'

return Test()
"""

        obj = cython.inline(code)

        self.assertEquals(obj.name, 'Joe')


    @unittest.skipIf(SKIP_TEST, 'Missing Cython and/or compiler')
    def test_basic_events(self):

        code = """
from traits.api import HasTraits, Str

class Test(HasTraits):
    name = Str

return Test()
"""

        obj = cython.inline(code)

        with self.assertTraitChanges(obj, 'name', count=1):
            obj.name = 'changing_name'



    @unittest.skipIf(SKIP_TEST or cython_version() <= (0,19,1), 'Triggers Cython bug')
    def test_on_trait_change_decorator(self):

        code = """
from traits.api import Int, HasTraits, Str, on_trait_change

class Test(HasTraits):
    name = Str
    value = Int

    @on_trait_change('name')
    def _update_a_value(self):
        self.value += 1

return Test()
"""

        obj = cython.inline(code)

        with self.assertTraitChanges(obj, 'value', count=1):
            obj.name = 'changing_name'

        self.assertEquals(obj.value, 1)
