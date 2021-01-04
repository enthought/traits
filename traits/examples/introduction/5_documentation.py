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
Documentation
=============

Another advantage of using Traits is that you code becomes clearer and easier
for yourself and other people to work with.  If you look at the original
version of the image class, it isn't clear what attributes are available on
the class and, worse yet, it isn't clear *when* those attributes are available.

Self-Documenting Code
---------------------

By using Traits, all your attributes are declared up-front, so anyone reading
your class knows exactly what your class is providing::

    class Image(HasTraits):
        filename = File(exists=True)
        sample_id = Str()
        operator = Str("N/A")
        date_acquired = Date()
        scan_size = Tuple(Float, Float)
        scan_width = Property(Float, depends_on='scan_size')
        scan_height = Property(Float, depends_on='scan_size')
        image = Array(shape=(None, None), dtype='uint8')
        pixel_area = Property(Float, depends_on='scan_height,scan_width,image')
        histogram = Property(Array, depends_on='image')

This goes a long way towards the ideal of "self-documenting code."  It is
common in production-quality Traits code to also document each trait with a
special ``#:`` comment so that auto-documentation tools like Sphinx can
generate API documentation for you::

    class Image(HasTraits):

        #: The filename of the image.
        filename = File(exists=True)

        #: The ID of the sample that is being imaged.
        sample_id = Str()

        #: The name of the operator who acquired the image.
        operator = Str("N/A")

        ...


HasStrictTraits
---------------

One common class of errors in Python are typos when accessing an attribute
of a class.  For example, if we typed::

    >>> image.fileanme = "sample_0002.png"

Python will not throw an error, but the code will not have the effect that
the user expects.  Some development tools can help you detect these
sorts of errors, but most of these are not available when writing code
interactively, such as in a Jupyter notebook.

Traits provides a special subclass of ``HasTraits`` called ``HasStrictTraits``
which restricts the allowed attributes to **only** the traits on the class.
If we use::

    class Image(HasStrictTraits):
        ...

then if we type::

    >>> image.fileanme = "sample_0002.png"
    TraitError: Cannot set the undefined 'fileanme' attribute of a 'Image'
    object.

We get an immediate error which flags the problem.

"""

import os
import datetime

from PIL import Image as PILImage
import numpy as np

from traits.api import (
    Array, Date, File, Float, HasStrictTraits, Property, Str, Tuple,
    cached_property, observe
)


class Image(HasStrictTraits):
    """ An SEM image stored in a file. """

    #: The filename of the image.
    filename = File(exists=True)

    #: The ID of the sample that is being imaged.
    sample_id = Str()

    #: The name of the operator who acquired the image.
    operator = Str("N/A")

    #: The date the image was acquired.
    date_acquired = Date()

    #: The size of the image.
    scan_size = Tuple(Float, Float)

    #: The width of the image.
    scan_width = Property(Float, depends_on='scan_size')

    #: The height of the image.
    scan_height = Property(Float, depends_on='scan_size')

    #: The image as a 2D numpy array
    image = Array(shape=(None, None), dtype='uint8')

    #: The area of each pixel.
    pixel_area = Property(Float, depends_on='scan_height,scan_width,image')

    #: The histogram of pixel intensities.
    histogram = Property(Array, depends_on='image')

    def threshold(self, low=0, high=255):
        """ Compute a threshold mask for the array. """
        return (self.image >= low) & (self.image <= high)

    # Trait observers

    @observe('filename')
    def read_image(self, event):
        pil_image = PILImage.open(self.filename).convert("L")
        self.image = np.array(pil_image)

    # Trait default methods

    def _date_acquired_default(self):
        return datetime.date.today()

    def _scan_size_default(self):
        return (1e-5, 1e-5)

    # Trait property methods

    def _get_scan_width(self):
        return self.scan_size[0]

    def _set_scan_width(self, value):
        self.scan_size = (value, self.scan_size[1])

    def _get_scan_height(self):
        return self.scan_size[1]

    def _set_scan_height(self, value):
        self.scan_size = (self.scan_size[0], value)

    def _get_pixel_area(self):
        if self.image.size > 0:
            return self.scan_height * self.scan_width / self.image.size
        else:
            return 0

    @cached_property
    def _get_histogram(self):
        hist, bins = np.histogram(
            self.image,
            bins=256,
            range=(0, 256),
            density=True,
        )
        return hist


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

# perform some sample computations
print(
    "The maximum intensity of {} is {}".format(
        image.sample_id,
        image.histogram.argmax(),
    )
)
pixel_count = image.threshold(low=200).sum()
print(
    "The area with intensity greater than 200 is {:0.3f} µm²".format(
        pixel_count * image.pixel_area * 1e12
    )
)
