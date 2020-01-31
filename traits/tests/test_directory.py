# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import pathlib
import sys
from tempfile import gettempdir

import unittest

from traits.api import BaseDirectory, Directory, HasTraits, TraitError


TESTS_SKIPPED_MESSAGE = (
    "Directory trait PathLib tests skipped for Python < 3.6")


class ExampleModel(HasTraits):
    path = Directory(exists=True)


class FastExampleModel(HasTraits):
    path = Directory()


class ExistsBaseDirectory(HasTraits):
    path = BaseDirectory(value=pathlib.Path(gettempdir()), exists=True)


class SimpleBaseDirectory(HasTraits):
    path = BaseDirectory(exists=False)


class DirectoryTestCase(unittest.TestCase):
    def test_valid_directory(self):
        example_model = ExampleModel(path=gettempdir())
        example_model.path = "."

    def test_invalid_directory(self):
        example_model = ExampleModel(path=gettempdir())

        def assign_invalid():
            example_model.path = "not_valid_path!#!#!#"

        self.assertRaises(TraitError, assign_invalid)

    def test_file(self):
        example_model = ExampleModel(path=gettempdir())

        def assign_invalid():
            example_model.path = __file__

        self.assertRaises(TraitError, assign_invalid)

    def test_invalid_type(self):
        example_model = ExampleModel(path=gettempdir())

        def assign_invalid():
            example_model.path = 11

        self.assertRaises(TraitError, assign_invalid)

    def test_fast_accepts_str(self):
        example_model = FastExampleModel(path=gettempdir())
        example_model.path = "."

    @unittest.skipIf(sys.version_info < (3, 6), TESTS_SKIPPED_MESSAGE)
    def test_fast_accepts_pathlib_dir(self):
        example_model = FastExampleModel()
        example_model.path = pathlib.Path(gettempdir())

        self.assertIsInstance(example_model.path, str)

    def test_fast_rejects_bytes(self):
        example_model = FastExampleModel()

        with self.assertRaises(TraitError):
            example_model.path = b"REJECT_BYTES"


class TestBaseDirectory(unittest.TestCase):

    def test_accepts_valid_dir_name(self):
        foo = ExistsBaseDirectory()
        tempdir = gettempdir()

        self.assertIsInstance(tempdir, str)

        foo.path = tempdir

    def test_rejects_invalid_dir_name(self):
        foo = ExistsBaseDirectory()

        with self.assertRaises(TraitError):
            foo.path = "!!!invalid_directory"

    def test_rejects_valid_file_name(self):
        foo = ExistsBaseDirectory()

        with self.assertRaises(TraitError):
            foo.path = __file__

    @unittest.skipIf(sys.version_info < (3, 6), TESTS_SKIPPED_MESSAGE)
    def test_accepts_valid_pathlib_dir(self):
        foo = ExistsBaseDirectory()
        foo.path = pathlib.Path(gettempdir())

        self.assertIsInstance(foo.path, str)

    @unittest.skipIf(sys.version_info < (3, 6), TESTS_SKIPPED_MESSAGE)
    def test_rejects_invalid_pathlib_dir(self):
        foo = ExistsBaseDirectory()

        with self.assertRaises(TraitError):
            foo.path = pathlib.Path("!!!invalid_directory")

    @unittest.skipIf(sys.version_info < (3, 6), TESTS_SKIPPED_MESSAGE)
    def test_rejects_valid_pathlib_file(self):
        foo = ExistsBaseDirectory()

        with self.assertRaises(TraitError):
            foo.path = pathlib.Path(__file__)

    def test_rejects_invalid_type(self):
        """ Rejects instances that are not `str` or `os.PathLike`.
        """
        foo = ExistsBaseDirectory()

        with self.assertRaises(TraitError):
            foo.path = 1

        with self.assertRaises(TraitError):
            foo.path = b"!!!invalid_directory"

    def test_simple_accepts_any_name(self):
        """ BaseDirectory with no existence check accepts any path name.
        """
        foo = SimpleBaseDirectory()
        foo.path = "!!!invalid_directory"

    @unittest.skipIf(sys.version_info < (3, 6), TESTS_SKIPPED_MESSAGE)
    def test_simple_accepts_any_pathlib(self):
        """ BaseDirectory with no existence check accepts any pathlib path.
        """
        foo = SimpleBaseDirectory()
        foo.path = pathlib.Path("!!!")

        self.assertIsInstance(foo.path, str)
