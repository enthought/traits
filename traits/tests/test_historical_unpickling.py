# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Tests for unpicking of pickles created using previous versions
of Traits.
"""

import glob
import os
import pickle
import unittest

import pkg_resources

from traits.api import BaseFloat


def find_test_pickles():
    """
    Iterate over the pickle files in the test_data directory.

    Yields paths to pickle files.
    """
    pickle_directory = pkg_resources.resource_filename(
        "traits.tests",
        "test-data/historical-pickles",
    )

    for filename in glob.glob(os.path.join(pickle_directory, "*.pkl")):
        yield filename


class TestHistoricalPickles(unittest.TestCase):
    def test_unpickling_historical_pickles(self):
        # Just test that the pickle can be unpickled.
        for pickle_path in find_test_pickles():
            filename = os.path.basename(pickle_path)
            with self.subTest(filename=filename):
                with open(pickle_path, "rb") as f:
                    pickle.load(f)
