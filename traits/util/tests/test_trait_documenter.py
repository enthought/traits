# -*- coding: utf-8 -*-
""" Tests for the trait documenter. """

import StringIO
import sys
import textwrap
import tokenize

import mock

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

    def test_get_definition_tokens(self):

        from traits.util.trait_documenter import _get_definition_tokens

        src = textwrap.dedent("""\
        depth_interval = Property(Tuple(Float, Float),
                                  depends_on="_depth_interval")
        """)
        string_io = StringIO.StringIO(src)
        tokens = tokenize.generate_tokens(string_io.readline)

        definition_tokens = _get_definition_tokens(tokens)

        # Check if they are correctly untokenized. This should not raise.
        string = tokenize.untokenize(definition_tokens)

        self.assertEqual(src.rstrip(), string)

    def test_add_line(self):

        from traits.util.trait_documenter import TraitDocumenter

        src = textwrap.dedent("""\
        class Fake(HasTraits):

            #: Test attribute
            test = Property(Bool, label=u"ミスあり")
        """)
        mocked_directive = mock.MagicMock()

        documenter = TraitDocumenter(mocked_directive, 'test', '   ')
        documenter.object_name = 'Property'

        with mock.patch(
                'traits.util.trait_documenter.inspect.getsource',
                return_value=src):
            with mock.patch(
                    'traits.util.trait_documenter.ClassLevelDocumenter'):
                documenter.add_directive_header('')


if __name__ == '__main__':
    unittest.main()

# ## EOF ######################################################################
