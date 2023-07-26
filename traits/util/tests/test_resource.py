# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Tests for traits.util.resource. """

import os
import tempfile
import unittest

from traits.testing.optional_dependencies import requires_pkg_resources
from traits.util.resource import find_resource, store_resource


@requires_pkg_resources
class TestResource(unittest.TestCase):
    def test_find_resource_deprecated(self):
        with self.assertWarns(DeprecationWarning):
            find_resource(
                "traits",
                os.path.join("traits", "__init__.py"),
            )

    def test_store_resource_deprecated(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertWarns(DeprecationWarning):
                store_resource(
                    "traits",
                    os.path.join("traits", "__init__.py"),
                    os.path.join(tmpdir, "just_testing.py"),
                )
