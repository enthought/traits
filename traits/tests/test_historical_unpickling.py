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


def find_test_pickles():
    """
    Iterate over the pickle files in the test_data directory.

    Skip files that correspond to a protocol not supported with
    the current version of Python.

    Yields paths to pickle files.
    """
    pickle_directory = pkg_resources.resource_filename(
        "traits.tests", "test-data/historical-pickles",
    )

    for pickle_path in glob.glob(os.path.join(pickle_directory, "*.pkl")):
        filename = os.path.basename(pickle_path)
        header, traitver, protocol, _ = filename.split("-", maxsplit=3)
        if header != "hitp":
            # Skip pickle files that don't follow the naming convention.
            continue

        if not protocol.startswith("p"):
            raise RuntimeError("Can't interpret protocol: {}".format(protocol))
        protocol = int(protocol[1:])
        if protocol > pickle.HIGHEST_PROTOCOL:
            # Protocol not understood by current Python; skip.
            continue

        yield filename


class TestHistoricalPickles(unittest.TestCase):
    def test_unpickling_historical_pickles(self):
        # Just test that the pickle can be unpickled.
        for pickle_path in find_test_pickles():
            filename = os.path.basename(pickle_path)
            with self.subTest(filename=filename):
                with open(pickle_path, "rb") as f:
                    pickle.load(f)
