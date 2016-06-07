""" Various small checks that came up in the Cython port.
"""
from traits.testing.unittest_tools import unittest
from traits.api import CTrait


class TestSetValidate(unittest.TestCase):

    def test_set_validate_invalid(self):
        t = CTrait(0)
        with self.assertRaises(ValueError):
            t.set_validate(None)
