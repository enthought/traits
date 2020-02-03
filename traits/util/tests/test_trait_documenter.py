# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Tests for the trait documenter. """

import contextlib
import io
import os
import shutil
import tempfile
import textwrap
import tokenize
import unittest
import unittest.mock as mock

from traits.api import HasTraits, Int
from traits.testing.optional_dependencies import sphinx, requires_sphinx


if sphinx is not None:
    from sphinx.ext.autodoc import Options
    from sphinx.ext.autodoc.directive import DocumenterBridge
    from sphinx.testing.path import path
    from sphinx.testing.util import SphinxTestApp
    from sphinx.util.docutils import LoggingReporter

    from traits.util.trait_documenter import (
        _get_definition_tokens,
        TraitDocumenter,
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


@requires_sphinx
class TestTraitDocumenter(unittest.TestCase):
    """ Tests for the trait documenter. """

    def setUp(self):
        self.source = """
    depth_interval = Property(Tuple(Float, Float),
                              depends_on="_depth_interval")
"""
        string_io = io.StringIO(self.source)
        tokens = tokenize.generate_tokens(string_io.readline)
        self.tokens = tokens

    def test_get_definition_tokens(self):
        src = textwrap.dedent(
            """\
        depth_interval = Property(Tuple(Float, Float),
                                  depends_on="_depth_interval")
        """
        )
        string_io = io.StringIO(src)
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
            test = Property(Bool, label="ミスあり")
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
        with self.create_directive() as directive:
            documenter = TraitDocumenter(
                directive, __name__ + ".MyTestClass.bar")
            documenter.generate(all_members=True)
            result = directive.result

        # Find annotations line.
        for item in result:
            if item.lstrip().startswith(":annotation:"):
                break
        else:
            self.fail("Didn't find the expected trait :annotation:")

        # Annotation should be a single line.
        self.assertIn("First line", item)
        self.assertNotIn("\n", item)

    @contextlib.contextmanager
    def create_directive(self):
        """
        Helper function to create a a "directive" suitable
        for instantiating the TraitDocumenter with, along with resources
        to support that directive, and clean up the resources afterwards.

        Returns
        -------
        contextmanager
            A context manager that returns a DocumenterBridge instance.
        """
        with self.tmpdir() as tmpdir:
            # The configuration file must exist, but it's okay if it's empty.
            conf_file = os.path.join(tmpdir, "conf.py")
            with open(conf_file, "w", encoding="utf-8"):
                pass

            app = SphinxTestApp(srcdir=path(tmpdir))
            app.builder.env.app = app
            app.builder.env.temp_data["docname"] = "dummy"

            # Backwards compatibility hack: for now, we need to be compatible
            # with both Sphinx < 2.1 (whose DocumenterBridge doesn't take
            # a state argument) and Sphinx >= 2.3 (which warns if the state
            # isn't passed). Eventually we should be able to drop support
            # for Sphinx < 2.1.
            kwds = {}
            if sphinx.version_info >= (2, 1):
                state = mock.Mock()
                state.document.settings.tab_width = 8
                kwds["state"] = state
            yield DocumenterBridge(
                app.env, LoggingReporter(''), Options(), 1, **kwds)

    @contextlib.contextmanager
    def tmpdir(self):
        """
        Helper function to create a temporary directory.

        Returns
        -------
        contextmanager
            Context manager that returns the path to a temporary directory.
        """
        tmpdir = tempfile.mkdtemp()
        try:
            yield tmpdir
        finally:
            shutil.rmtree(tmpdir)
