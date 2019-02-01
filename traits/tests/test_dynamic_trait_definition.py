import unittest

from traits.api import Float, HasTraits, Int, List


class Foo(HasTraits):
    x = Float

    y_changes = List

    def _y_changed(self, new):
        self.y_changes.append(new)


class TestDynamicTraitDefinition(unittest.TestCase):
    """ Test demonstrating special change events using the 'event' metadata.
    """

    def test_add_trait(self):
        foo = Foo(x=3)
        foo.add_trait("y", Int)

        self.assertTrue(hasattr(foo, "y"))
        self.assertEqual(type(foo.y), int)

        foo.y = 4
        self.assertEqual(foo.y_changes, [4])

    def test_remove_trait(self):
        foo = Foo(x=3)

        # We can't remove a "statically" added trait (i.e., a trait defined
        # in the Foo class).
        result = foo.remove_trait("x")
        self.assertFalse(result)

        # We can remove dynamically added traits.
        foo.add_trait("y", Int)
        foo.y = 70

        result = foo.remove_trait("y")
        self.assertTrue(result)

        self.assertFalse(hasattr(foo, "y"))
        foo.y = 10
        self.assertEqual(foo.y_changes, [70])
