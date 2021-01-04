# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Script to generate the historical pickle test data.
"""

import os
import pickle

from traits.api import Float
from traits import __version__

# Filename template.
PKL_FILENAME = "hipt-t{traits_version}-p{pickle_protocol}-{description}.pkl"

# Dictionary mapping description to object to be pickled.
PICKLEES = {
    "float-ctrait": Float(5.3).as_ctrait(),
}

# Supported pickle protocols on this Python version.
SUPPORTED_PICKLE_PROTOCOLS = range(pickle.HIGHEST_PROTOCOL + 1)


def write_pickle_file(description, picklee, protocol, output_dir):
    filename = PKL_FILENAME.format(
        traits_version=__version__,
        pickle_protocol=protocol,
        description=description,
    )
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "wb") as pickle_file:
        pickle.dump(picklee, pickle_file, protocol=protocol)


def generate_pickles():
    # Write to the current directory. Could make the output directory
    # an option.
    pickle_directory = os.path.abspath(".")

    for protocol in SUPPORTED_PICKLE_PROTOCOLS:
        for description, picklee in PICKLEES.items():
            write_pickle_file(description, picklee, protocol, pickle_directory)


if __name__ == "__main__":
    generate_pickles()
