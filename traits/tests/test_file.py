import os.path as osp

import six

from traits.testing.unittest_tools import unittest

from traits.api import File, HasTraits, TraitError


class ExampleModel(HasTraits):
    file_name = File(exists=True)


class FastExampleModel(HasTraits):
    file_name = File()


class FileTestCase(unittest.TestCase):
    def test_valid_file(self):
        example_model = ExampleModel(file_name=__file__)
        example_model.file_name = osp.__file__
        example_model.file_name = six.text_type(osp.__file__)

    def test_invalid_file(self):
        example_model = ExampleModel(file_name=__file__)

        def assign_invalid():
            example_model.file_name = 'not_valid_path!#!#!#'

        self.assertRaises(TraitError, assign_invalid)

    def test_directory(self):
        example_model = ExampleModel(file_name=__file__)

        def assign_invalid():
            example_model.file_name = osp.dirname(__file__)

        self.assertRaises(TraitError, assign_invalid)

    def test_invalid_type(self):
        example_model = ExampleModel(file_name=__file__)

        def assign_invalid():
            example_model.file_name = 11

        self.assertRaises(TraitError, assign_invalid)

    def test_fast(self):
        example_model = FastExampleModel(file_name=__file__)
        example_model.path = '.'
        example_model.path = u'.'