# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!


from pathlib import Path
from unittest import TestCase

import pkg_resources

from traits_stubs_tests.util import MypyAssertions


class TestAnnotations(TestCase, MypyAssertions):
    def test_all(self, filename_suffix=''):
        """ Run mypy for all files contained in traits_stubs_tests/examples
        directory.

        Lines with expected errors are marked inside these files.
        Any mismatch will raise an assertion error.

        Parameters
        ----------
        filename_suffix: str
            Optional filename suffix filter.
        """
        examples_dir = Path(pkg_resources.resource_filename(
            'traits_stubs_tests', 'examples'))

        for file_path in examples_dir.glob("*{}.py".format(filename_suffix)):
            with self.subTest(file_path=file_path):
                self.assertRaisesMypyError(file_path)
