# (C) Copyright 2020-2026 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!


import importlib.resources
from unittest import TestCase

from traits.testing.optional_dependencies import (
    requires_mypy,
    requires_numpy_typing,
)
from traits.stubs_tests.util import MypyAssertions


@requires_mypy
class TestAnnotations(TestCase, MypyAssertions):
    def test_all(self, filename_suffix=""):
        """ Run mypy for all files contained in traits.stubs_tests/examples
        directory.

        Lines with expected errors are marked inside these files.
        Any mismatch will raise an assertion error.

        Parameters
        ----------
        filename_suffix: str
            Optional filename suffix filter.
        """
        examples = importlib.resources.files('traits.stubs_tests') / 'examples'

        with importlib.resources.as_file(examples) as examples_dir:
            for file_path in examples_dir.glob(
                    "*{}.py".format(filename_suffix)):
                with self.subTest(file_path=file_path):
                    self.assertRaisesMypyError(file_path)

    @requires_numpy_typing
    def test_numpy_examples(self):
        """ Run mypy for files contained in traits.stubs_tests/numpy_examples
        directory.

        Lines with expected errors are marked inside these files.
        Any mismatch will raise an assertion error.
        """
        examples = (
            importlib.resources.files('traits.stubs_tests') / 'numpy_examples'
        )

        with importlib.resources.as_file(examples) as examples_dir:
            for file_path in examples_dir.glob("*.py"):
                with self.subTest(file_path=file_path):
                    self.assertRaisesMypyError(file_path)
