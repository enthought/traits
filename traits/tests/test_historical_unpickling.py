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

import pathlib
import pickle
import unittest

import pkg_resources


def find_pickles():
    """
    Iterate over the pickle files in the test_data directory.

    Skip files that correspond to a protocol not supported with
    the current version of Python.

    Yields paths to pickle files.
    """
    pickle_directory = pathlib.Path(
        pkg_resources.resource_filename(
            "traits.tests", "test-data/historical-pickles",
        )
    )

    for pickle_path in pickle_directory.glob("*.pkl"):
        header, _, protocol, _ = pickle_path.name.split("-", maxsplit=3)
        if header != "hipt":
            # Skip pickle files that don't follow the naming convention.
            continue

        if not protocol.startswith("p"):
            raise RuntimeError("Can't interpret protocol: {}".format(protocol))
        protocol = int(protocol[1:])
        if protocol > pickle.HIGHEST_PROTOCOL:
            # Protocol not understood by current Python; skip.
            continue

        yield pickle_path


class TestHistoricalPickles(unittest.TestCase):
    def test_unpickling_historical_pickles(self):
        # Just test that the pickle can be unpickled.
        for pickle_path in find_pickles():
            with self.subTest(filename=pickle_path.name):
                with pickle_path.open("rb") as f:
                    pickle.load(f)
