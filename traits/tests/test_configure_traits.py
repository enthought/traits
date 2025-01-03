# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import os
import pickle
import pickletools
import shutil
import tempfile
import unittest
import unittest.mock as mock
import warnings

from traits.api import HasTraits, Int
from traits.testing.optional_dependencies import requires_traitsui, traitsui


class Model(HasTraits):
    count = Int


@requires_traitsui
class TestConfigureTraits(unittest.TestCase):
    def setUp(self):
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
            with self.assertWarns(DeprecationWarning):
                model.configure_traits(filename=filename)

        self.assertTrue(os.path.exists(filename))
        with open(filename, "rb") as pickled_object:
            unpickled = pickle.load(pickled_object)

        self.assertIsInstance(unpickled, Model)
        self.assertEqual(unpickled.count, model.count)

    def test_pickle_protocol(self):
        # Pickled files should use protocol 3 (a compromise between
        # efficiency and wide applicability).

        model = Model(count=37)
        filename = os.path.join(self.tmpdir, "nonexistent.pkl")
        self.assertFalse(os.path.exists(filename))

        with mock.patch.object(self.toolkit, "view_application"):
            with self.assertWarns(DeprecationWarning):
                model.configure_traits(filename=filename)

        self.assertTrue(os.path.exists(filename))
        with open(filename, "rb") as pickled_object_file:
            pickled_object = pickled_object_file.read()

        # Get and check the first opcode
        opcode, arg, _ = next(pickletools.genops(pickled_object))
        self.assertEqual(opcode.name, "PROTO")
        self.assertEqual(arg, 3)

    def test_filename_with_existing_file(self):
        # Create pre-existing pickle file.
        stored_model = Model(count=52)
        filename = os.path.join(self.tmpdir, "model.pkl")
        with open(filename, "wb") as pickled_object:
            pickle.dump(stored_model, pickled_object)

        model = Model(count=19)
        with mock.patch.object(self.toolkit, "view_application"):
            with self.assertWarns(DeprecationWarning):
                model.configure_traits(filename=filename)
        self.assertEqual(model.count, 52)

    def test_filename_with_invalid_existing_file(self):
        # Create file whose contents are not unpickleable.
        filename = os.path.join(self.tmpdir, "model.pkl")
        with open(filename, "wb") as pickled_object:
            pickled_object.write(b"this is not a valid pickle")

        model = Model(count=19)
        with mock.patch.object(self.toolkit, "view_application"):
            with self.assertRaises(pickle.PickleError):
                with self.assertWarns(DeprecationWarning):
                    model.configure_traits(filename=filename)

    def test_filename_with_existing_file_stores_updated_model(self):
        stored_model = Model(count=52)
        filename = os.path.join(self.tmpdir, "model.pkl")
        with open(filename, "wb") as pickled_object:
            pickle.dump(stored_model, pickled_object)

        def modify_model(*args, **kwargs):
            model.count = 23
            return mock.DEFAULT

        model = Model(count=19)
        with mock.patch.object(self.toolkit, "view_application") as mock_view:
            mock_view.side_effect = modify_model
            with self.assertWarns(DeprecationWarning):
                model.configure_traits(filename=filename)
        self.assertEqual(model.count, 23)

        with open(filename, "rb") as pickled_object:
            unpickled = pickle.load(pickled_object)

        self.assertIsInstance(unpickled, Model)
        self.assertEqual(unpickled.count, model.count)

    def test_edit_when_false(self):
        # Check for deprecation warning when *edit* is false.
        model = Model()
        with mock.patch.object(self.toolkit, "view_application") as mock_view:
            mock_view.return_value = True
            with self.assertWarns(DeprecationWarning):
                model.configure_traits(edit=False)
        mock_view.assert_not_called()

    def test_edit_when_true(self):
        # Check for deprecation warning when *edit* is false.
        model = Model()
        with mock.patch.object(self.toolkit, "view_application") as mock_view:
            mock_view.return_value = True
            with self.assertWarns(DeprecationWarning):
                model.configure_traits(edit=True)
        mock_view.assert_called_once()

    def test_edit_not_given(self):
        # Normal case where the *edit* argument is not supplied.
        model = Model()
        with mock.patch.object(self.toolkit, "view_application") as mock_view:
            mock_view.return_value = True
            with warnings.catch_warnings(record=True) as captured_warnings:
                warnings.simplefilter("always", DeprecationWarning)
                model.configure_traits()
        mock_view.assert_called_once()

        all_warnings = "".join(
            str(warning.message) for warning in captured_warnings
        )
        self.assertNotIn("edit argument", all_warnings)
