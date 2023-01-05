# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Tests for the traits.__version__ attribute and the traits.version
module contents.
"""

import unittest

from traits.testing.optional_dependencies import (
    pkg_resources,
    requires_pkg_resources,
)

import traits


class TestVersion(unittest.TestCase):
    @requires_pkg_resources
    def test_dunder_version(self):
        self.assertIsInstance(traits.__version__, str)
        # Round-trip through parse_version; this verifies not only
        # that the version is valid, but also that it's properly normalised
        # according to the PEP 440 rules.
        parsed_version = pkg_resources.parse_version(traits.__version__)
        self.assertEqual(str(parsed_version), traits.__version__)

    @requires_pkg_resources
    def test_version_version(self):
        # Importing inside the test to ensure that we get a test error
        # in the case where the version module does not exist.
        from traits.version import version

        self.assertIsInstance(version, str)
        parsed_version = pkg_resources.parse_version(version)
        self.assertEqual(str(parsed_version), version)

    def test_version_git_revision(self):
        from traits.version import git_revision

        self.assertIsInstance(git_revision, str)

        # Check the form of the revision. Could use a regex, but that seems
        # like overkill.
        self.assertEqual(len(git_revision), 40)
        self.assertLessEqual(set(git_revision), set("0123456789abcdef"))

    def test_versions_match(self):
        import traits.version

        self.assertEqual(traits.version.version, traits.__version__)
