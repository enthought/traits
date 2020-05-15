import unittest

from traits.api import HasTraits, Expression


class TestExpression(unittest.TestCase):

    def test_set_value_original(self):
        class Foo(HasTraits):
            # The default value set in the class definition is "0"
            bar = Expression()

        f = Foo()
        f.bar = "1"
        self.assertEqual(f.bar, "1")

    def test_default_value_original(self):
        class Foo(HasTraits):
            # The default value set in the class definition is "0"
            bar = Expression(default_value="1")

        f = Foo()
        self.assertEqual(f.bar, "1")

    def test_default_method_original(self):
        class Foo(HasTraits):
            # The default value set in the class definition is "0"
            bar = Expression()

            def _bar_default(self):
                return "1"

        f = Foo()
        self.assertEqual(f.bar, "1")
