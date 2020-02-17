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

from util import MypyAssertions

examples_dir = Path(
    pkg_resources.resource_filename('traits-stubs', 'tests/examples'))


class TestAnnotations(TestCase, MypyAssertions):
    def test_all(self):
        for file_path in examples_dir.glob("*.py"):
            with self.subTest(file_path=file_path):
                self.assertRaisesMypyError(file_path)
