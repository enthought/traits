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
Introduction to Traits
======================

To make the tutorial more practical, let's imagine that you are
writing some tools to organize and process image data, perhaps
to help you develop a machine learning algorithm, or to document
your research.  This image data might come from a camera, a scanning
electron microscope, or from some more exotic source.  No matter the
source, the image will have data associated with it, such as who
produced the image, the equipment that was used, the date and time
that the image was taken, and so forth.

In this tutorial, we'll consider an example where we have a collection
of greyscale SEM images, each of them stored in a file, along with other
information, such as the sample that was imaged, the size of the scanned
region, and the operator who took the image.

We would like to read in the image and provide a number of standard
analysis steps to the user, as well as making the raw image data
available as a NumPy array.

The sample code here shows how you might create a class in standard
object-oriented Python with NumPy for analysis and Pillow for image
loading.  Experiment with the code in the example to see how you can use it.

In the subsequent steps of the tutorial, we'll look at how we can use Traits
to simplify and improve the code here.
"""

import datetime
import os

import numpy as np
from PIL import Image as PILImage


class Image:
    """ An SEM image stored in a file. """

    def __init__(self, filename, sample_id, date_acquired, operator,
                 scan_size=(1e-5, 1e-5)):
        # initialize the primary attributes
        self.filename = filename
        self.sample_id = sample_id
        self.operator = operator
        self.date_acquired = operator
        self.scan_size = scan_size

        # useful secondary attributes
        self.scan_width, self.scan_height = self.scan_size

    def read_image(self):
        """ Read the image from disk. """
        pil_image = PILImage.open(self.filename).convert("L")
        self.image = np.array(pil_image)

        # compute some extra secondary attributes from the image
        if self.image.size > 0:
            self.pixel_area = (
                self.scan_height * self.scan_width / self.image.size
            )
        else:
            self.pixel_area = 0

    def histogram(self):
        """ Compute the normalized histogram of the image. """
        hist, bins = np.histogram(
            self.image,
            bins=256,
            range=(0, 256),
            density=True,
        )
        return hist

    def threshold(self, low=0, high=255):
        """ Compute a threshold mask for the array. """
        return (self.image >= low) & (self.image <= high)


# ---------------------------------------------------------------------------
# Demo code
# ---------------------------------------------------------------------------

this_dir = os.path.dirname(__file__)
image_dir = os.path.join(this_dir, "images")
filename = os.path.join(image_dir, "sample_0001.png")

# load the image
image = Image(
    filename=filename,
    operator="Hannes",
    sample_id="0001",
    date_acquired=datetime.datetime.today(),
    scan_size=(1e-5, 1e-5),
)

# read the image from disk
image.read_image()

# perform some sample computations
print(
    "The maximum intensity of {} is {}".format(
        image.sample_id,
        image.histogram().argmax(),
    )
)
pixel_count = image.threshold(low=200).sum()
print(
    "The area with intensity greater than 200 is {:0.3f} µm²".format(
        pixel_count * image.pixel_area * 1e12
    )
)
