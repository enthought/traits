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
Visualization
=============

Traits allows you to instantly create a graphical user interface
for your ``HasTraits`` classes.  If you have TraitsUI and a suitable
GUI toolkit (such as PyQt5 or PySide2) installed in your Python
environment then you can create a dialog view of an instance of
your class by simply doing::

    >>> image.configure_traits()

This gives you a default UI out of the box with no further effort,
but it usually is not what you would want to provide for your users.

With a little more effort using the features of TraitsUI, you can
design a dialog which is more pleasing::

    from traitsui.api import Item, View

    class Image(HasStrictTraits):
        ...

        view = View(
            Item('filename'),
            Item('sample_id', label='Sample ID'),
            Item('operator'),
            Item('date_acquired'),
            Item('scan_width', label='Width (m):'),
            Item('scan_height', label='Height (m):')
        )

TraitsUI can be used as the building block for complete scientific
applications, including 2D and 3D plotting.

"""

import os
import datetime

from PIL import Image as PILImage
import numpy as np

from traits.api import (
    Array, Date, File, Float, HasStrictTraits, Property, Str, Tuple,
    cached_property, observe
)
from traitsui.api import Item, View


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

    # TraitsUI view declaration

    view = View(
        Item('filename'),
        Item('sample_id', label='Sample ID'),
        Item('operator'),
        Item('date_acquired'),
        Item('scan_width', label='Width (m):'),
        Item('scan_height', label='Height (m):'),
        Item(
            'pixel_area',
            format_func=lambda area: "{:0.3f} µm²".format(area * 1e18),
            style='readonly',
        ),
    )


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

demo = image

if __name__ == "__main__":
    demo.configure_traits()
