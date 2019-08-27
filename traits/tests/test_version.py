# Copyright (c) 2019 by Enthought, Inc.
# All rights reserved.

"""
Tests for the traits.__version__ attribute and the traits.version
module contents.
"""

from __future__ import absolute_import, print_function, unicode_literals

import unittest

import pkg_resources
import six

import traits


class TestVersion(unittest.TestCase):
    def test_dunder_version(self):
        self.assertIsInstance(traits.__version__, six.text_type)
        # Round-trip through parse_version; this verifies not only
        # that the version is valid, but also that it's properly normalised
        # according to the PEP 440 rules.
        parsed_version = pkg_resources.parse_version(traits.__version__)
        self.assertEqual(six.text_type(parsed_version), traits.__version__)

    def test_version_version(self):
        # Importing inside the test to ensure that we get a test error
        # in the case where the version module does not exist.
        from traits.version import version

        self.assertIsInstance(version, six.text_type)
        parsed_version = pkg_resources.parse_version(version)
        self.assertEqual(six.text_type(parsed_version), version)

    def test_version_git_revision(self):
        from traits.version import git_revision

        self.assertIsInstance(git_revision, six.text_type)

        # Check the form of the revision. Could use a regex, but that seems
        # like overkill.
        self.assertEqual(len(git_revision), 40)
        self.assertLessEqual(set(git_revision), set("0123456789abcdef"))

    def test_versions_match(self):
        import traits.version

        self.assertEqual(traits.version.version, traits.__version__)
