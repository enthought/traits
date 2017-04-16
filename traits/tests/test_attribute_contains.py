from __future__ import absolute_import
from traits.testing.unittest_tools import unittest
from ..api import HasTraits, Int


class TestTraits(HasTraits):
    value = Int


class HasTraitsContainsTest(unittest.TestCase):
    def test_in_operator(self):
        test_traits = TestTraits(value=1)
        self.assertTrue('value' in test_traits)
        self.assertFalse('abrakadabra' in test_traits)
