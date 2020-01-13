import os

import unittest
from pathlib import Path

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

    def test_valid_pathlike_file(self):
        example_model = ExampleModel(file_name=Path(__file__))

    def test_invalid_file(self):
        example_model = ExampleModel(file_name=__file__)

        def assign_invalid():
            example_model.file_name = "not_valid_path!#!#!#"

        self.assertRaises(TraitError, assign_invalid)

    def test_invalid_pathlike_file(self):
        example_model = ExampleModel(file_name=__file__)

        def assign_invalid():
            example_model.file_name = Path("not_valid_path!#!#!#")

        self.assertRaises(TraitError, assign_invalid)

    def test_directory(self):
        example_model = ExampleModel(file_name=__file__)

        def assign_invalid():
            example_model.file_name = os.path.dirname(__file__)

        self.assertRaises(TraitError, assign_invalid)

    def test_pathlike_directory(self):
        example_model = ExampleModel(file_name=__file__)

        def assign_invalid():
            example_model.file_name = Path(os.path.dirname(__file__))

        self.assertRaises(TraitError, assign_invalid)

    def test_invalid_type(self):
        example_model = ExampleModel(file_name=__file__)

        def assign_invalid():
            example_model.file_name = 11

        self.assertRaises(TraitError, assign_invalid)

    @unittest.skip("Unimplemented fast validator for File trait")
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
