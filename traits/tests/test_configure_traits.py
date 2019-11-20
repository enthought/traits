# Copyright (c) 2019 by Enthought, Inc.
# All rights reserved.

try:
    # Python 3: mock in the standard library.
    import unittest.mock as mock
except ImportError:
    # Python 2: need to use 3rd-party mock.
    import mock
import os
import shutil
import tempfile
import unittest

import six

from traits.api import HasTraits, Int
from traits.testing.optional_dependencies import requires_traitsui


class Model(HasTraits):
    count = Int


@requires_traitsui
class TestConfigureTraits(unittest.TestCase):
    def setUp(self):
        import traitsui.api

        self.toolkit = traitsui.api.toolkit()
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        del self.tmpdir
        del self.toolkit

    def test_simple_call(self):
        # Minimal exercising of configure_traits functionality.
        model = Model()
        with mock.patch.object(self.toolkit, "view_application") as mock_view:
            model.configure_traits()
        self.assertEqual(mock_view.call_count, 1)

    def test_filename_but_no_file(self):
        model = Model(count=37)
        filename = os.path.join(self.tmpdir, "nonexistent.pkl")
        self.assertFalse(os.path.exists(filename))

        with mock.patch.object(self.toolkit, "view_application"):
            model.configure_traits(filename=filename)

        self.assertTrue(os.path.exists(filename))
        with open(filename, "rb") as pickled_object:
            unpickled = six.moves.cPickle.load(pickled_object)

        self.assertIsInstance(unpickled, Model)
        self.assertEqual(unpickled.count, model.count)

    def test_filename_with_existing_file(self):
        # Create pre-existing pickle file.
        stored_model = Model(count=52)
        filename = os.path.join(self.tmpdir, "model.pkl")
        with open(filename, "wb") as pickled_object:
            six.moves.cPickle.dump(stored_model, pickled_object)

        model = Model(count=19)
        with mock.patch.object(self.toolkit, "view_application"):
            model.configure_traits(filename=filename)
        self.assertEqual(model.count, 52)

    def test_filename_with_invalid_existing_file(self):
        # Create file whose contents are not unpickleable.
        filename = os.path.join(self.tmpdir, "model.pkl")
        with open(filename, "wb") as pickled_object:
            pickled_object.write(b"this is not a valid pickle")

        model = Model(count=19)
        with mock.patch.object(self.toolkit, "view_application"):
            with self.assertRaises(six.moves.cPickle.PickleError):
                model.configure_traits(filename=filename)

    def test_filename_with_existing_file_stores_updated_model(self):
        stored_model = Model(count=52)
        filename = os.path.join(self.tmpdir, "model.pkl")
        with open(filename, "wb") as pickled_object:
            six.moves.cPickle.dump(stored_model, pickled_object)

        def modify_model(*args, **kwargs):
            model.count = 23
            return mock.DEFAULT

        model = Model(count=19)
        with mock.patch.object(self.toolkit, "view_application") as mock_view:
            mock_view.side_effect = modify_model
            model.configure_traits(filename=filename)
        self.assertEqual(model.count, 23)

        with open(filename, "rb") as pickled_object:
            unpickled = six.moves.cPickle.load(pickled_object)

        self.assertIsInstance(unpickled, Model)
        self.assertEqual(unpickled.count, model.count)
