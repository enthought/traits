# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from tempfile import gettempdir

import unittest

from traits.api import Directory, HasTraits, TraitError


class ExampleModel(HasTraits):
    path = Directory(exists=True)


class FastExampleModel(HasTraits):
    path = Directory()


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

    def test_fast(self):
        example_model = FastExampleModel(path=gettempdir())
        example_model.path = "."
