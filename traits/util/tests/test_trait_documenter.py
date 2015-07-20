""" Tests for the trait documenter. """

import contextlib
import sys
import tokenize
import types
from mock import Mock

from traits.testing.unittest_tools import unittest

@contextlib.contextmanager
def sphinx_mock_import():
    try:
        from sphinx.ext.autodoc import ClassLevelDocumenter
    except ImportError:
        sphinx = types.ModuleType("sphinx")
        sphinx.ext = types.ModuleType("sphinx.ext")
        sphinx.ext.autodoc = types.ModuleType("sphinx.ext.autodoc")
        sys.modules["sphinx"] = sphinx
        sys.modules["sphinx.ext"] = sphinx.ext
        sys.modules["sphinx.ext.autodoc"] = sphinx.ext.autodoc
        sphinx.ext.autodoc.__dict__["ClassLevelDocumenter"] = Mock()

    yield

    del sys.modules["sphinx.ext.autodoc"]


class TestTraitDocumenter(unittest.TestCase):
    """ Tests for the trait documenter. """

    def setUp(self):
        self.tokens = [
            (1, 'Property', (12, 21), (12, 29),
             '    depth_interval = Property(Tuple(Float, Float),\n'),
            (51, '(', (12, 29), (12, 30),
             '    depth_interval = Property(Tuple(Float, Float),\n'),
            (1, 'Tuple', (12, 30), (12, 35),
             '    depth_interval = Property(Tuple(Float, Float),\n'),
            (51, '(', (12, 35), (12, 36),
             '    depth_interval = Property(Tuple(Float, Float),\n'),
            (1, 'Float', (12, 36), (12, 41),
             '    depth_interval = Property(Tuple(Float, Float),\n'),
            (51, ',', (12, 41), (12, 42),
             '    depth_interval = Property(Tuple(Float, Float),\n'),
            (1, 'Float', (12, 43), (12, 48),
             '    depth_interval = Property(Tuple(Float, Float),\n'),
            (51, ')', (12, 48), (12, 49),
             '    depth_interval = Property(Tuple(Float, Float),\n'),
            (51, ',', (12, 49), (12, 50),
             '    depth_interval = Property(Tuple(Float, Float),\n'),
            (54, '\n', (12, 50), (12, 51),
             '    depth_interval = Property(Tuple(Float, Float),\n'),
            (1, 'depends_on', (13, 30), (13, 40),
             '                              depends_on="_depth_interval")\n'),
            (51, '=', (13, 40), (13, 41),
             '                              depends_on="_depth_interval")\n'),
            (3, '"_depth_interval"', (13, 41), (13, 58),
             '                              depends_on="_depth_interval")\n'),
            (51, ')', (13, 58), (13, 59),
             '                              depends_on="_depth_interval")\n'),
            (4, '\n', (13, 59), (13, 60),
             '                              depends_on="_depth_interval")\n')]

    def test_get_definition_tokens(self):
        with sphinx_mock_import():
            from traits.util.trait_documenter import _get_definition_tokens

            definition_tokens = _get_definition_tokens(self.tokens)

            # Check if they are correctly untokenized. This should not raise.
            tokenize.untokenize(definition_tokens)

if __name__ == '__main__':
    unittest.main()

# ## EOF ######################################################################
