""" Tests for the trait documenter. """

import StringIO
import sys
import tokenize

from traits.testing.unittest_tools import unittest


def _sphinx_present():
    try:
        import sphinx  # noqa
    except ImportError:
        return False

    return True


def _python_version_is_32():
    return sys.version_info[:2] == (3, 2)


# Skipping for python 3.2 because sphinx does not work on it.
@unittest.skipIf(not _sphinx_present() or _python_version_is_32(),
                 "Sphinx not available. Cannot test documenter")
class TestTraitDocumenter(unittest.TestCase):
    """ Tests for the trait documenter. """

    def setUp(self):
        self.source = """
    depth_interval = Property(Tuple(Float, Float),
                              depends_on="_depth_interval")
"""
        string_io = StringIO.StringIO(self.source)
        tokens = tokenize.generate_tokens(string_io.readline)
        self.tokens = tokens

    def test_get_definition_tokens(self):

        from traits.util.trait_documenter import _get_definition_tokens

        definition_tokens = _get_definition_tokens(self.tokens)

        # Check if they are correctly untokenized. This should not raise.
        string = tokenize.untokenize(definition_tokens)

        self.assertEqual(self.source.rstrip(), string)

if __name__ == '__main__':
    unittest.main()

# ## EOF ######################################################################
