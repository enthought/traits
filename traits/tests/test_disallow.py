""" Unit tests for the Disallow singleton.
"""
from traits.testing.unittest_tools import unittest
from ..api import Disallow, HasTraits, TraitError


class A(HasTraits):

    x = Disallow


class B(HasTraits):

    _ = Disallow


class TestDisallow(unittest.TestCase):

    def test_trait_get_set(self):
        a = A()

        with self.assertRaises(AttributeError):
            a.x

        with self.assertRaises(TraitError):
            a.x = 123

    def test_wildcard_get_set(self):
        b = B()

        with self.assertRaises(AttributeError):
            b.some_attribute

        with self.assertRaises(TraitError):
            b.some_attribute = 'foo'
