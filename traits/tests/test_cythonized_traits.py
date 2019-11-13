""" Test some usage of Trait classes when the code is cythonized.

The tests reflects some of the patterns needed in different applications. They
probably don't cover all of the user case.

Each test case is written as if the test code was in a separate module then
compiled with Cython Inline before evaluation the produced object behaves
properly.

The tests need a Cython version > 0.19 and a compiler.

"""
import sys
import unittest

import six

from traits.testing.unittest_tools import UnittestTools
from traits.testing.optional_dependencies import cython

if cython is None:
    skip_reason = "Cython is not installed"
elif sys.platform == "win32" and six.PY2:
    # Tests are failing for undiagnosed reasons on Windows / Python 2.7.
    # Ref: enthought/traits#557.
    skip_reason = (
        "Compilation issues with Windows / Python 2.7. "
        "See enthought/traits#557"
    )
else:
    skip_reason = None


@unittest.skipIf(skip_reason, skip_reason)
class CythonizedTraitsTestCase(unittest.TestCase, UnittestTools):
    def test_simple_default_methods(self):

        code = """
from traits.api import HasTraits, Str

class Test(HasTraits):
    name = Str

    def _name_default(self):
        return 'Joe'

return Test()
"""

        obj = self.execute(code)
        self.assertEqual(obj.name, "Joe")

    def test_basic_events(self):

        code = """
from traits.api import HasTraits, Str

class Test(HasTraits):
    name = Str

return Test()
"""

        obj = self.execute(code)
        with self.assertTraitChanges(obj, "name", count=1):
            obj.name = "changing_name"

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

        obj = self.execute(code)
        with self.assertTraitChanges(obj, "value", count=1):
            obj.name = "changing_name"

        self.assertEqual(obj.value, 1)

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

        obj = self.execute(code)
        with self.assertTraitChanges(obj, "value", count=1):
            obj.name = "changing_name"

        self.assertEqual(obj.value, 1)

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

        obj = self.execute(code)
        self.assertEqual(obj.name_len, len(obj.name))

        # Assert dependency works
        obj.name = "Bob"
        self.assertEqual(obj.name_len, len(obj.name))

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

        obj = self.execute(code)
        self.assertEqual(obj.name_len, len(obj.name))

        # Assert dependency works
        obj.name = "Bob"
        self.assertEqual(obj.name_len, len(obj.name))

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

        obj = self.execute(code)
        self.assertEqual(obj.funky_name, obj.name)

        # Assert dependency works
        obj.name = "Bob"
        self.assertEqual(obj.funky_name, obj.name)

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

        obj = self.execute(code)
        self.assertEqual(obj.funky_name, obj.name)

        # Assert dependency works
        obj.name = "Bob"
        self.assertEqual(obj.funky_name, obj.name)

    def execute(self, code):
        """
        Helper function to execute the given code under cython.inline and
        return the result.
        """
        return cython.inline(
            code,
            force=True,
            language_level="3",
        )
