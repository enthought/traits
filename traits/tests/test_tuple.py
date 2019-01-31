""" Unit tests for the Tuple trait type.
"""
import unittest

from traits.tests.tuple_test_mixin import TupleTestMixin
from traits.trait_types import Tuple


class TupleTestCase(TupleTestMixin, unittest.TestCase):
    def setUp(self):
        self.trait = Tuple
