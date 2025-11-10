# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
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

from traits.api import Bool, HasTraits, Int, Property
from traits.testing.optional_dependencies import sphinx, requires_sphinx


if sphinx is not None:
    from sphinx.ext.autodoc import ClassDocumenter, INSTANCEATTR, Options
    from sphinx.ext.autodoc.directive import DocumenterBridge
    from sphinx.testing.util import SphinxTestApp
    from sphinx.util.docutils import LoggingReporter

    from traits.util.trait_documenter import (
        _get_definition_tokens,
        trait_definition,
        TraitDocumenter,
    )

    if sphinx.version_info < (7, 2):
        from sphinx.testing.path import path as Path
    else:
        from pathlib import Path

    no_index_entry = sphinx.version_info >= (8, 2)
    no_index = 'noindex' if sphinx.version_info < (7, 2) else 'no-index'


# Configuration file content for testing.
CONF_PY = """\
extensions = ['sphinx.ext.autodoc']

# The suffix of source filenames.
source_suffix = '.rst'

autodoc_mock_imports = [
    'dummy'
]
"""


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


class Fake(HasTraits):

    #: Test attribute
    test_attribute = Property(Bool, label="ミスあり")


class FindTheTraits(HasTraits):
    """
    Class for testing the can_document_member functionality.
    """

    #: A TraitType subclass on the right-hand side.
    an_int = Int

    #: A TraitType instance on the right-hand side.
    another_int = Int()

    #: A non-trait integer
    magic_number = 1729

    @property
    def not_a_trait(self):
        """
        I'm a regular property, not a trait.
        """


class MySubClass(MyTestClass):

    #: A new attribute.
    foo = Bool(True)


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
        mocked_directive = mock.MagicMock()

        documenter = TraitDocumenter(mocked_directive, "test", "   ")
        documenter.object_name = "test_attribute"
        documenter.parent = Fake

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

    def test_successful_trait_definition(self):
        definition = trait_definition(cls=Fake, trait_name="test_attribute")
        self.assertEqual(
            definition, 'Property(Bool, label="ミスあり")',
        )

    def test_failed_trait_definition(self):
        with self.assertRaises(ValueError):
            trait_definition(cls=Fake, trait_name="not_a_trait")

    def test_can_document_member(self):
        # Regression test for enthought/traits#1238

        with self.create_directive() as directive:
            class_documenter = ClassDocumenter(
                directive, __name__ + ".FindTheTraits"
            )
            class_documenter.parse_name()
            class_documenter.import_object()

            self.assertTrue(
                TraitDocumenter.can_document_member(
                    INSTANCEATTR, "an_int", True, class_documenter,
                )
            )

            self.assertTrue(
                TraitDocumenter.can_document_member(
                    INSTANCEATTR, "another_int", True, class_documenter,
                )
            )

            self.assertFalse(
                TraitDocumenter.can_document_member(
                    INSTANCEATTR, "magic_number", True, class_documenter,
                )
            )

            self.assertFalse(
                TraitDocumenter.can_document_member(
                    INSTANCEATTR, "not_a_trait", True, class_documenter,
                )
            )

    def test_class(self):
        # given
        documenter = TraitDocumenter(mock.Mock(), 'test')
        documenter.parent = MyTestClass
        documenter.object_name = 'bar'
        documenter.modname = 'traits.util.tests.test_trait_documenter'
        documenter.get_sourcename = mock.Mock(return_value='<autodoc>')
        documenter.objpath = ['MyTestClass', 'bar']
        documenter.add_line = mock.Mock()

        # when
        documenter.add_directive_header('')

        # then
        self.assertEqual(documenter.directive.warn.call_args_list, [])
        expected = [
            ('.. py:attribute:: MyTestClass.bar', '<autodoc>'),
            (f'   :{no_index}:', '<autodoc>'),
            ('   :module: traits.util.tests.test_trait_documenter', '<autodoc>'),  # noqa
            ('   :annotation: = Int(42, desc=""" First line …', '<autodoc>')]  # noqa
        if no_index_entry:
            expected.insert(2, ('   :no-index-entry:', '<autodoc>'))
        calls = documenter.add_line.call_args_list
        for index, line in enumerate(expected):
            self.assertEqual(calls[index][0], line)

    def test_subclass(self):
        # given
        documenter = TraitDocumenter(mock.Mock(), 'test')
        documenter.object_name = 'bar'
        documenter.objpath = ['MySubClass', 'bar']
        documenter.parent = MySubClass
        documenter.modname = 'traits.util.tests.test_trait_documenter'
        documenter.get_sourcename = mock.Mock(return_value='<autodoc>')
        documenter.add_line = mock.Mock()

        # when
        documenter.add_directive_header('')

        # then
        self.assertEqual(documenter.directive.warn.call_args_list, [])
        expected = [
            ('.. py:attribute:: MySubClass.bar', '<autodoc>'),
            (f'   :{no_index}:', '<autodoc>'),
            ('   :module: traits.util.tests.test_trait_documenter', '<autodoc>'),  # noqa
            ('   :annotation: = Int(42, desc=""" First line …', '<autodoc>')]  # noqa
        if no_index_entry:
            expected.insert(2, ('   :no-index-entry:', '<autodoc>'))
        calls = documenter.add_line.call_args_list
        for index, line in enumerate(expected):
            self.assertEqual(calls[index][0], line)

        # given
        documenter.object_name = 'foo'
        documenter.objpath = ['MySubClass', 'foo']
        documenter.add_line = mock.Mock()

        # when
        documenter.add_directive_header('')

        # then
        self.assertEqual(documenter.directive.warn.call_args_list, [])
        expected = [
            ('.. py:attribute:: MySubClass.foo', '<autodoc>'),
            (f'   :{no_index}:', '<autodoc>'),
            ('   :module: traits.util.tests.test_trait_documenter', '<autodoc>'),  # noqa
            ('   :annotation: = Bool(True)', '<autodoc>')]  # noqa
        if no_index_entry:
            expected.insert(2, ('   :no-index-entry:', '<autodoc>'))
        calls = documenter.add_line.call_args_list
        for index, line in enumerate(expected):
            self.assertEqual(calls[index][0], line)

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
            # Ensure configuration file exists.
            conf_file = os.path.join(tmpdir, "conf.py")
            with open(conf_file, "w", encoding="utf-8") as f:
                f.write(CONF_PY)

            app = SphinxTestApp(srcdir=Path(tmpdir))
            app.builder.env.app = app
            app.builder.env.temp_data["docname"] = "dummy"

            kwds = {}
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
