# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Observation
===========

In our code so far, there is a problem that it is possible for certain related
values to get out of sync with one another.  For example, if we change the
filename after we have read the image into memory, then the data in memory
still refers to the old image.  It would be nice if we could automatically
re-load the image if the filename changes.  Traits allows you to do this.

The Observe Decorator
---------------------

We want to have the `read_image` method run whenever the ``filename`` trait
changes.  We can do this by adding an ``observe`` decorator to the method::


    class Image(HasTraits):
        ...

        @observe('filename')
        def read_image(self, event):
            ...

The observer passes an event object to the function which contains information
about what changed, such as the old value of the trait, but we don't need that
information to react to the change, so it is ignored in the body of the
function.

For most traits, the observer will run only when the trait's value *actually*
changes, not just when the value is set.  So if you do::

    >>> image.filename = "sample_0001.png"
    >>> image.filename = "sample_0001.png"

then the observer will only be run once.

Observing Multiple Traits
-------------------------

If you look at the computation of ``pixel_area`` in the original code, it
looks like this::

    self.pixel_area = self.scan_height * self.scan_width / self.image.size

It depends on the ``scan_width``, ``scan_height`` and the ``image``, so we
would like to listen to changes to *all* of these.  We could write three
``@observe`` functions, one for each trait, but the content would be the
same for each.  A better way to do this is to have the observer listen to
all the traits at once::


    class Image(HasTraits):
        ...

        @observe('scan_width, scan_height, image')
        def update_pixel_area(self, event):
            if self.image.size > 0:
                self.pixel_area = (
                    self.scan_height * self.scan_width / self.image.size
                )
            else:
                self.pixel_area = 0

Dynamic Observers
-----------------

Sometimes you want to be able to observe changes to traits from a different
object or piece of code.  The ``observe`` method on a ``HasTraits`` subclass
allows you to dynamically specify a function to be called if the value of a
trait changes::

    image = Image(
        filename="sample_0001.png",
        sample_id="0001",
    )

    def print_filename_changed(event):
        print("Filename changed")

    image.observe(print_filename_changed, 'filename')

    # will print "Filename changed" to the screen
    image.filename="sample_0002.png"

Dynamic observers can also be disconnected using the same method, by adding
the argument ``remove=True``::

    image.observe(print_filename_changed, 'filename', remove=True)

    # nothing will print
    image.filename="sample_0003.png"

Exercise
--------

Currently ``scan_height`` and ``scan_width`` are set from the parts of the
``scan_size`` trait as part of the ``traits_init`` method.  Remove the
``traits_init`` method and have ``scan_height`` and ``scan_width`` methods
update whenever ``scan_size`` changes.

"""

import os
import datetime

from PIL import Image as PILImage
import numpy as np

from traits.api import (
    Array, Date, File, Float, HasTraits, Str, Tuple, observe
)


class Image(HasTraits):
    """ An SEM image stored in a file. """

    filename = File(exists=True)
    sample_id = Str()
    operator = Str("N/A")
    date_acquired = Date()
    scan_size = Tuple(Float, Float)

    scan_width = Float
    scan_height = Float

    image = Array(shape=(None, None), dtype='uint8')

    pixel_area = Float()

    def traits_init(self):
        # useful secondary attributes
        self.scan_width, self.scan_height = self.scan_size

    # Trait observers

    @observe('filename')
    def read_image(self, event):
        pil_image = PILImage.open(self.filename).convert("L")
        self.image = np.array(pil_image)

    @observe('scan_width, scan_height, image')
    def update_pixel_area(self, event):
        if self.image.size > 0:
            self.pixel_area = (
                self.scan_height * self.scan_width / self.image.size
            )
        else:
            self.pixel_area = 0

    # Trait default methods

    def _date_acquired_default(self):
        return datetime.date.today()

    def _scan_size_default(self):
        return (1e-5, 1e-5)


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
)

# perform some sample computations
print("Scan size:", image.scan_size)

print("Change scan width to 1e-4")
image.scan_width = 1e-4

print("Scan size:", image.scan_size)

for filename in os.listdir(image_dir):
    if os.path.splitext(filename)[1] == '.png':
        print()
        print("Changing filename to {}".format(filename))
        image.filename = os.path.join(image_dir, filename)

        print(
            "The pixel size of {} is {:0.3f} nm²".format(
                filename,
                image.pixel_area * 1e18,
            )
        )
