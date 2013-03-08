""" General regression tests for fixed bugs.
"""

import gc
import unittest
import sys

from traits.has_traits import HasTraits


def _create_subclass():
    class Subclass(HasTraits):
        pass
    return Subclass


class TestRegression(unittest.TestCase):

    def test_subclasses_weakref(self):
        """ Make sure that dynamically created subclasses are not held
        strongly by HasTraits.
        """
        previous_subclasses = HasTraits.__subclasses__()
        _create_subclass()
        _create_subclass()
        _create_subclass()
        _create_subclass()
        gc.collect()
        self.assertEqual(previous_subclasses, HasTraits.__subclasses__())
