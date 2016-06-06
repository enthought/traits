from traits.testing.unittest_tools import unittest
from traits.api import Constant, HasTraits


class A(HasTraits):
    txt = Constant('something')


class TestConstant(unittest.TestCase):

    def test_default_value(self):
        a = A()
        self.assertEqual(a.txt, 'something')
