# Copyright (c) 2019 by Enthought, Inc.
# All rights reserved.

"""
Tests for the traits.__version__ attribute and the traits.version
module contents.
"""

import unittest

import traits


class TestVersion(unittest.TestCase):
    def test_dunder_version(self):
        self.assertIsInstance(traits.__version__, str)

    def test_version_version(self):
        # Importing inside the test to ensure that we get a test error
        # in the case where the version module does not exist.
        import traits.version
        self.assertIsInstance(traits.version.version, str)

    def test_version_git_revision(self):
        import traits.version
        self.assertIsInstance(traits.version.git_revision, str)

    def test_versions_match(self):
        import traits.version
        self.assertEqual(traits.version.version, traits.__version__)
