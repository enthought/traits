# -*- coding: utf-8 -*-
""" Tests for the trait documenter. """

import textwrap
import tokenize
import unittest
try:
    # Python 3: mock in the standard library.
    import unittest.mock as mock
except ImportError:
    # Python 2: need to use 3rd-party mock.
    import mock

import pkg_resources
import six

try:
    import sphinx  # noqa: F401
except ImportError:
    sphinx_available = False
else:
    sphinx_available = True

from traits.api import HasTraits, Int

if sphinx_available:
    from sphinx.ext.autodoc import Options
    from sphinx.ext.autodoc.directive import DocumenterBridge
    from sphinx.testing.util import SphinxTestApp
    from sphinx.testing.path import path
    from sphinx.util.docutils import LoggingReporter

    from traits.util.trait_documenter import (
        _get_definition_tokens,
        TraitDocumenter,
    )

skip_unless_sphinx_present = unittest.skipUnless(
    sphinx_available,
    "Sphinx is not available. Cannot test documenter.",
)


class MyTestClass(HasTraits):
    """
    Class-level docstring.
    """
    #: I'm a troublesome trait with a long definition.
    bar = Int(42, desc=""" First line

        The answer to
        Life,
        the Universe,

        and Everything.
    """)


@skip_unless_sphinx_present
class TestTraitDocumenter(unittest.TestCase):
    """ Tests for the trait documenter. """

    def setUp(self):
        self.source = """
    depth_interval = Property(Tuple(Float, Float),
                              depends_on="_depth_interval")
"""
        string_io = six.StringIO(self.source)
        tokens = tokenize.generate_tokens(string_io.readline)
        self.tokens = tokens

    def test_get_definition_tokens(self):
        src = textwrap.dedent(
            """\
        depth_interval = Property(Tuple(Float, Float),
                                  depends_on="_depth_interval")
        """
        )
        string_io = six.StringIO(src)
        tokens = tokenize.generate_tokens(string_io.readline)

        definition_tokens = _get_definition_tokens(tokens)

        # Check if they are correctly untokenized. This should not raise.
        string = tokenize.untokenize(definition_tokens)

        self.assertEqual(src.rstrip(), string)

    def test_add_line(self):

        src = textwrap.dedent(
            """\
        class Fake(HasTraits):

            #: Test attribute
            test = Property(Bool, label=u"ミスあり")
        """
        )
        mocked_directive = mock.MagicMock()

        documenter = TraitDocumenter(mocked_directive, "test", "   ")
        documenter.object_name = "Property"

        with mock.patch(
            "traits.util.trait_documenter.inspect.getsource", return_value=src
        ):
            with mock.patch(
                (
                    "traits.util.trait_documenter.ClassLevelDocumenter"
                    ".add_directive_header"
                )
            ):
                documenter.add_directive_header("")

        self.assertEqual(
            len(documenter.directive.result.append.mock_calls), 1)

    def test_abbreviated_annotations(self):
        # Regression test for enthought/traits#493.
        directive = self.create_test_directive()
        documenter = TraitDocumenter(directive, __name__ + ".MyTestClass.bar")
        documenter.generate(all_members=True)

        # Find annotations line.
        for item in directive.result:
            if item.lstrip().startswith(":annotation:"):
                break
        else:
            self.fail("Didn't find the expected trait :annotation:")

        # Annotation should be a single line.
        self.assertIn("First line", item)
        self.assertNotIn("\n", item)

    def create_test_directive(self):
        """
        Helper function to create a a "directive" suitable
        for instantiating the TraitDocumenter with.

        Returns
        -------
        directive : DocumenterBridge

        """
        srcdir = pkg_resources.resource_filename(
            "traits.util.tests",
            "data/"
        )
        srcdir = path(srcdir)

        app = SphinxTestApp(srcdir=srcdir)
        app.builder.env.app = app
        app.builder.env.temp_data["docname"] = "dummy"
        return DocumenterBridge(app.env, LoggingReporter(''), Options(), 1)
