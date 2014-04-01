""" Test some usage of Trait classes when the code is cythonized.

The tests reflects some of the patterns needed in different applications. They
probably don't cover all of the user case.

Each test case is written as if the test code was in a separate module then
compiled with Cython Inline before evaluation the produced object behaves
properly.

The tests need a Cython version > 0.19 and a compiler.

"""
try:
    import cython
    no_cython = False
except ImportError:
    no_cython = True


from ..testing.unittest_tools import unittest, UnittestTools


def has_no_compiler():
    if no_cython:
        return True
    # Easy way to check if we have access to a compiler
    code = "return 1+1"
    try:
        cython.inline(code)
        return False
    except:
        return True


def cython_version():
    if no_cython:
        return None
    from Cython.Compiler.Version import version
    return tuple(int(v) for v in version.split('.'))

SKIP_TEST = has_no_compiler()


# Cython 0.19 implementation of safe_type fails while parsing some of the
# code. We provide a very basic implementation that always returns object
# (we don't need any particular optimizations)
def _always_object_type(arg, context):
    return 'object'


class CythonizedTraitsTestCase(unittest.TestCase, UnittestTools):

    @unittest.skipIf(SKIP_TEST, 'Missing Cython and/or compiler')
    def test_simple_default_methods(self):

        code = """
from traits.api import HasTraits, Str

class Test(HasTraits):
    name = Str

    def _name_default(self):
        return 'Joe'

return Test()
"""

        obj = cython.inline(code)

        self.assertEqual(obj.name, 'Joe')

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

    @unittest.skipIf(SKIP_TEST, 'Missing Cython and/or compiler')
    def test_on_trait_static_handlers(self):

        code = """
from traits.api import HasTraits, Str, Int

class Test(HasTraits):
    name = Str
    value = Int

    def _name_changed(self):
        self.value += 1

return Test()
"""

        obj = cython.inline(code, get_type=_always_object_type, force=True)

        with self.assertTraitChanges(obj, 'value', count=1):
            obj.name = 'changing_name'

        self.assertEqual(obj.value, 1)

    @unittest.skipIf(SKIP_TEST, 'Missing Cython and/or compiler')
    def test_on_trait_on_trait_change_decorator(self):

        code = """
from traits.api import HasTraits, Str, Int, on_trait_change

class Test(HasTraits):
    name = Str
    value = Int

    @on_trait_change('name')
    def _update_value(self):
        self.value += 1

return Test()
"""

        obj = cython.inline(code, get_type=_always_object_type, force=True,
                            locals={}, globals={})

        with self.assertTraitChanges(obj, 'value', count=1):
            obj.name = 'changing_name'

        self.assertEqual(obj.value, 1)

    @unittest.skipIf(SKIP_TEST, 'Missing Cython and/or compiler')
    def test_on_trait_properties(self):

        code = """
from traits.api import HasTraits, Str, Int, Property, cached_property

class Test(HasTraits):
    name = Str
    name_len = Property(depends_on='name')

    @cached_property
    def _get_name_len(self):
        return len(self.name)

return Test()
"""

        obj = cython.inline(code, get_type=_always_object_type, force=True,
                            locals={}, globals={})

        self.assertEqual(obj.name_len, len(obj.name))

        # Assert dependency works
        obj.name = 'Bob'
        self.assertEqual(obj.name_len, len(obj.name))

    @unittest.skipIf(SKIP_TEST, 'Missing Cython and/or compiler')
    def test_on_trait_properties_with_standard_getter(self):

        code = """
from traits.api import HasTraits, Str, Int, Property

class Test(HasTraits):
    name = Str

    def _get_name_length(self):
        return len(self.name)

    name_len = Property(_get_name_length)

return Test()
"""

        obj = cython.inline(code, get_type=_always_object_type, force=True,
                            locals={}, globals={})

        self.assertEqual(obj.name_len, len(obj.name))

        # Assert dependency works
        obj.name = 'Bob'
        self.assertEqual(obj.name_len, len(obj.name))

    @unittest.skipIf(SKIP_TEST, 'Missing Cython and/or compiler')
    def test_on_trait_aliasing(self):

        code = """
from traits.api import HasTraits, Str, Int, Property

def Alias(name):
    def _get_value(self):
        return getattr(self, name)
    def _set_value(self, value):
        return setattr(self, name, value)

    return Property(_get_value, _set_value)

class Test(HasTraits):
    name = Str

    funky_name = Alias('name')

return Test()
"""

        obj = cython.inline(code, get_type=_always_object_type, force=True,
                            locals={}, globals={})

        self.assertEqual(obj.funky_name, obj.name)

        # Assert dependency works
        obj.name = 'Bob'
        self.assertEqual(obj.funky_name, obj.name)

    @unittest.skipIf(SKIP_TEST, 'Missing Cython and/or compiler')
    def test_on_trait_aliasing_different_scope(self):

        code = """
from traits.api import HasTraits, Str, Int, Property

def _get_value(self, name):
    return getattr(self, 'name')
def _set_value(self, name, value):
    return setattr(self, 'name', value)


class Test(HasTraits):
    name = Str

    funky_name = Property(_get_value, _set_value)

return Test()
"""

        obj = cython.inline(code, get_type=_always_object_type)

        self.assertEqual(obj.funky_name, obj.name)

        # Assert dependency works
        obj.name = 'Bob'
        self.assertEqual(obj.funky_name, obj.name)

    @unittest.skipIf(SKIP_TEST, 'Missing Cython and/or compiler')
    def test_on_trait_lambda_failure(self):

        # Lambda function are converted like builtins when cythonized which
        # causes the following code to fail

        code = """
from traits.api import HasTraits, Str, Int, Property

def Alias(name):
    return Property(
        lambda obj: getattr(obj, name),
        lambda obj, value: setattr(obj, name, value)
    )

class Test(HasTraits):
    name = Str

    funky_name = Alias('name')

return Test()
"""

        try:
            cython.inline(code, get_type=_always_object_type, force=True,
                          locals={}, globals={})
        except:
            # We suppose we have an exception. Because of the usage of the
            # skipIf decorator on the test, we can't use an expectedFailure
            # decorator as they don't play well together.
            pass
        else:
            self.fail(
                'Unexpected results. Cython was not managing lambda as regular'
                ' functions. Behaviour changed ...'
            )
