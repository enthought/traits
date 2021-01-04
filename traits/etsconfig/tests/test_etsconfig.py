# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Tests the 'ETSConfig' configuration object. """

# Standard library imports.
import contextlib
import os
import shutil
import sys
import tempfile
import time

import unittest

# Enthought library imports.
from traits.etsconfig.etsconfig import ETSConfig, ETSToolkitError


@contextlib.contextmanager
def temporary_directory():
    """
    Context manager to create and clean up a temporary directory.

    """
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


@contextlib.contextmanager
def restore_mapping_entry(mapping, key):
    """
    Context manager that restores a mapping entry to its previous
    state on exit.

    """
    missing = object()
    old_value = mapping.get(key, missing)
    try:
        yield
    finally:
        if old_value is missing:
            mapping.pop(key, None)
        else:
            mapping[key] = old_value


@contextlib.contextmanager
def temporary_home_directory():
    """
    Context manager that temporarily remaps HOME / APPDATA
    to a temporary directory.

    """
    # Use the same recipe as in ETSConfig._initialize_application_data
    # to determine the home directory.
    home_var = "APPDATA" if sys.platform == "win32" else "HOME"

    with temporary_directory() as temp_home:
        with restore_mapping_entry(os.environ, home_var):
            os.environ[home_var] = temp_home
            yield


@contextlib.contextmanager
def mock_sys_argv(args):
    old_args = sys.argv
    sys.argv = args
    try:
        yield
    finally:
        sys.argv = old_args


@contextlib.contextmanager
def mock_os_environ(args):
    old_environ = os.environ
    os.environ = args
    try:
        yield
    finally:
        os.environ = old_environ


class ETSConfigTestCase(unittest.TestCase):
    """ Tests the 'ETSConfig' configuration object. """

    ###########################################################################
    # 'TestCase' interface.
    ###########################################################################

    #### public methods #######################################################

    def setUp(self):
        """
        Prepares the test fixture before each test method is called.

        """

        # Make a fresh instance each time.
        self.ETSConfig = type(ETSConfig)()

    def run(self, result=None):
        # Extend TestCase.run to use a temporary home directory.
        with temporary_home_directory():
            super().run(result)

    ###########################################################################
    # 'ETSConfigTestCase' interface.
    ###########################################################################

    #### public methods #######################################################

    def test_application_data(self):
        """
        application data

        """

        dirname = self.ETSConfig.application_data

        self.assertEqual(os.path.exists(dirname), True)
        self.assertEqual(os.path.isdir(dirname), True)

    def test_set_application_data(self):
        """
        set application data

        """

        old = self.ETSConfig.application_data

        self.ETSConfig.application_data = "foo"
        self.assertEqual("foo", self.ETSConfig.application_data)

        self.ETSConfig.application_data = old
        self.assertEqual(old, self.ETSConfig.application_data)

    def test_application_data_is_idempotent(self):
        """
        application data is idempotent

        """

        # Just do the previous test again!
        self.test_application_data()
        self.test_application_data()

    def test_write_to_application_data_directory(self):
        """
        write to application data directory

        """

        self.ETSConfig.company = "Blah"
        dirname = self.ETSConfig.application_data

        path = os.path.join(dirname, "dummy.txt")
        data = str(time.time())

        with open(path, "w", encoding="utf-8") as f:
            f.write(data)

        self.assertEqual(os.path.exists(path), True)

        with open(path, "r", encoding="utf-8") as f:
            result = f.read()

        os.remove(path)

        self.assertEqual(data, result)

    def test_default_company(self):
        """
        default company

        """

        self.assertEqual(self.ETSConfig.company, "Enthought")

    def test_set_company(self):
        """
        set company

        """

        old = self.ETSConfig.company

        self.ETSConfig.company = "foo"
        self.assertEqual("foo", self.ETSConfig.company)

        self.ETSConfig.company = old
        self.assertEqual(old, self.ETSConfig.company)

    def _test_default_application_home(self):
        """
        application home

        """

        # This test is only valid when run with the 'main' at the end of this
        # file: "python app_dat_locator_test_case.py", in which case the
        # app_name will be the directory this file is in ('tests').
        app_home = self.ETSConfig.application_home
        (dirname, app_name) = os.path.split(app_home)

        self.assertEqual(dirname, self.ETSConfig.application_data)
        self.assertEqual(app_name, "tests")

    def test_toolkit_environ(self):
        test_args = ["something"]
        test_environ = {"ETS_TOOLKIT": "test"}
        with mock_sys_argv(test_args):
            with mock_os_environ(test_environ):
                toolkit = self.ETSConfig.toolkit

        self.assertEqual(toolkit, "test")

    def test_toolkit_environ_missing(self):
        test_args = ["something"]
        test_environ = {}
        with mock_sys_argv(test_args):
            with mock_os_environ(test_environ):
                toolkit = self.ETSConfig.toolkit

        self.assertEqual(toolkit, "")

    def test_set_toolkit(self):
        test_args = []
        test_environ = {"ETS_TOOLKIT": "test_environ"}

        with mock_sys_argv(test_args):
            with mock_os_environ(test_environ):
                self.ETSConfig.toolkit = "test_direct"
                toolkit = self.ETSConfig.toolkit

        self.assertEqual(toolkit, "test_direct")

    def test_provisional_toolkit(self):
        test_args = []
        test_environ = {}

        with mock_sys_argv(test_args):
            with mock_os_environ(test_environ):
                repr(self.ETSConfig.toolkit)
                with self.ETSConfig.provisional_toolkit("test_direct"):
                    toolkit = self.ETSConfig.toolkit
                    self.assertEqual(toolkit, "test_direct")

        # should stay set, since no exception raised
        toolkit = self.ETSConfig.toolkit
        self.assertEqual(toolkit, "test_direct")

    def test_provisional_toolkit_exception(self):
        test_args = []
        test_environ = {"ETS_TOOLKIT": ""}

        with mock_sys_argv(test_args):
            with mock_os_environ(test_environ):
                try:
                    with self.ETSConfig.provisional_toolkit("test_direct"):
                        toolkit = self.ETSConfig.toolkit
                        self.assertEqual(toolkit, "test_direct")
                        raise ETSToolkitError("Test exception")
                except ETSToolkitError as exc:
                    if not exc.message == "Test exception":
                        raise

                # should be reset, since exception raised
                toolkit = self.ETSConfig.toolkit
                self.assertEqual(toolkit, "")

    def test_provisional_toolkit_already_set(self):
        test_args = []
        test_environ = {"ETS_TOOLKIT": "test_environ"}

        with mock_sys_argv(test_args):
            with mock_os_environ(test_environ):
                with self.assertRaises(ETSToolkitError):
                    with self.ETSConfig.provisional_toolkit("test_direct"):
                        pass

                # should come from the environment
                toolkit = self.ETSConfig.toolkit
                self.assertEqual(toolkit, "test_environ")

    def test_user_data(self):
        """
        user data

        """

        dirname = self.ETSConfig.user_data

        self.assertEqual(os.path.exists(dirname), True)
        self.assertEqual(os.path.isdir(dirname), True)

    def test_set_user_data(self):
        """
        set user data

        """

        old = self.ETSConfig.user_data

        self.ETSConfig.user_data = "foo"
        self.assertEqual("foo", self.ETSConfig.user_data)

        self.ETSConfig.user_data = old
        self.assertEqual(old, self.ETSConfig.user_data)

    def test_user_data_is_idempotent(self):
        """
        user data is idempotent

        """

        # Just do the previous test again!
        self.test_user_data()

    def test_write_to_user_data_directory(self):
        """
        write to user data directory

        """

        self.ETSConfig.company = "Blah"
        dirname = self.ETSConfig.user_data

        path = os.path.join(dirname, "dummy.txt")
        data = str(time.time())

        with open(path, "w", encoding="utf-8") as f:
            f.write(data)

        self.assertEqual(os.path.exists(path), True)

        with open(path, "r", encoding="utf-8") as f:
            result = f.read()

        os.remove(path)

        self.assertEqual(data, result)


# For running as an individual set of tests.
if __name__ == "__main__":

    # Add the non-default test of application_home...non-default because it
    # must be run using this module as a script to be valid.
    suite = unittest.TestLoader().loadTestsFromTestCase(ETSConfigTestCase)
    suite.addTest(ETSConfigTestCase("_test_default_application_home"))

    unittest.TextTestRunner(verbosity=2).run(suite)
