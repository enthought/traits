# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import pathlib
from tempfile import gettempdir

import unittest

from traits.api import BaseDirectory, Directory, HasTraits, TraitError


class ExampleModel(HasTraits):
    path = Directory(exists=True)


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

    def test_accepts_valid_pathlib_dir(self):
        foo = ExistsBaseDirectory()
        foo.path = pathlib.Path(gettempdir())

        self.assertIsInstance(foo.path, str)

    def test_rejects_invalid_pathlib_dir(self):
        foo = ExistsBaseDirectory()

        with self.assertRaises(TraitError):
            foo.path = pathlib.Path("!!!invalid_directory")

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

    def test_simple_accepts_any_pathlib(self):
        """ BaseDirectory with no existence check accepts any pathlib path.
        """
        foo = SimpleBaseDirectory()
        foo.path = pathlib.Path("!!!")

        self.assertIsInstance(foo.path, str)
