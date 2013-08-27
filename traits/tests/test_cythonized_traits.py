try:
    import cython
    no_cython = False
except ImportError:
    no_cython = True


from ..testing.api import unittest, UnittestTools


class CythonizedTraitsTestCase(unittest.TestCase, UnittestTools):


    @unittest.skip(no_cython)
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


    @unittest.skip(no_cython)
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



    @unittest.skip(no_cython)
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
