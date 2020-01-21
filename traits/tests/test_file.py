# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import os
from pathlib import Path
import sys
import unittest

from traits.api import File, HasTraits, TraitError
from traits.testing.optional_dependencies import requires_traitsui


class ExampleModel(HasTraits):
    file_name = File(exists=True)


class FastExampleModel(HasTraits):
    file_name = File()


class FileTestCase(unittest.TestCase):
    def test_valid_file(self):
        example_model = ExampleModel(file_name=__file__)
        example_model.file_name = os.path.__file__

    @unittest.skipIf(sys.version_info < (3, 6), "PathLike File trait test")
    def test_valid_pathlike_file(self):
        ExampleModel(file_name=Path(__file__))

    def test_invalid_file(self):
        example_model = ExampleModel(file_name=__file__)

        with self.assertRaises(TraitError):
            example_model.file_name = "not_valid_path!#!#!#"

    @unittest.skipIf(sys.version_info < (3, 6), "PathLike File trait test")
    def test_invalid_pathlike_file(self):
        example_model = ExampleModel(file_name=__file__)

        with self.assertRaises(TraitError):
            example_model.file_name = Path("not_valid_path!#!#!#")

    def test_directory(self):
        example_model = ExampleModel(file_name=__file__)

        with self.assertRaises(TraitError):
            example_model.file_name = os.path.dirname(__file__)

    @unittest.skipIf(sys.version_info < (3, 6), "PathLike File trait test")
    def test_pathlike_directory(self):
        example_model = ExampleModel(file_name=__file__)

        with self.assertRaises(TraitError):
            example_model.file_name = Path(os.path.dirname(__file__))

    def test_invalid_type(self):
        example_model = ExampleModel(file_name=__file__)

        with self.assertRaises(TraitError):
            example_model.file_name = 11

    def test_fast(self):
        example_model = FastExampleModel(file_name=__file__)
        example_model.path = "."


class TestCreateEditor(unittest.TestCase):

    @requires_traitsui
    def test_exists_controls_editor_dialog_style(self):
        x = File(exists=True)
        editor = x.create_editor()
        self.assertEqual(editor.dialog_style, "open")

        x = File(exists=False)
        editor = x.create_editor()
        self.assertEqual(editor.dialog_style, "save")
