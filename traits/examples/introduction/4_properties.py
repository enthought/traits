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
Property Traits
===============

The ``Image`` class has three traits which are closely related: ``scan_size``,
``scan_width`` and ``scan_height``.  We would ideally like to keep all of these
synchronized.  This can be done with trait observation, as shown in the
previous section, but this sort of pattern is common enough that Traits has
some in-built helpers.

Instead of declaring that ``scan_width = Float()`` we could instead declare it
to be a ``Property`` trait type.  Property traits are similar to ``@property``
decorators in standard Python in that rather than storing a value, they compute
a derived value via a "getter", and optionally store values via a "setter".
Traits uses specially named methods of the form ``_get_<property>`` and
``_set_property`` for these "getters" and "setters."  If there is a "getter"
but no "setter" then the property is read-only.

Additionally, we need to know when the value of the property might change, and
so we need to declare what traits to observe to know when the property might
change.  What all this means is that we can define ``scan_width`` as a
property by::

    class Image(HasTraits):
        ...

        scan_width = Property(Float, depends_on='scan_size')

        def _get_scan_width(self):
            return self.scan_size[0]

        def _set_scan_width(self, value):
            self.scan_size = (value, self.scan_height)

Traits will then take care of hooking up all the required observers to make
everything work as expected; and the `Property` can also be observed if
desired.

Simple `Property` traits like this are computed "lazily": the value is only
calculated when you ask for it.

Cached Properties
-----------------

It would be quite easy to turn the histogram function into a read-only
property.  This might look something like this::

    class Image(HasTraits):
        ...

        histogram = Property(Array, depends_on='image')

        def _get_histogram(self):
            hist, bins = np.histogram(
                self.image,
                bins=256,
                range=(0, 256),
                density=True,
            )
            return hist

This works, but it has a downside that the histogram is re-computed every
time the property is accessed.  For small images, this is probably OK, but
for larger images, or if you are working with many images at once, this may
impact performance.  In these cases, you can specify that the property
should **cache** the returned value and use that value until the trait(s)
the property depend on changes::

    class Image(HasTraits):
        ...

        histogram = Property(Array, depends_on='image')

        @cached_property
        def _get_histogram(self):
            hist, bins = np.histogram(
                self.image,
                bins=256,
                range=(0, 256),
                density=True,
            )
            return hist

This has the trade-off that the result of the computation is being stored
in memory, but in this case the memory is only a few hundred bytes, and so
is unlikely to cause problems; but you probably wouldn't want to do this
with a multi-gigabyte array.

Exercise
--------

Make ``pixel_area`` a read-only property.

"""

import os
import datetime

from PIL import Image as PILImage
import numpy as np

from traits.api import (
    Array, Date, File, Float, HasTraits, Property, Str, Tuple,
    cached_property, observe
)


class Image(HasTraits):
    """ An SEM image stored in a file. """

    filename = File(exists=True)
    sample_id = Str()
    operator = Str("N/A")
    date_acquired = Date()
    scan_size = Tuple(Float, Float)

    scan_width = Property(Float, depends_on='scan_size')
    scan_height = Property(Float, depends_on='scan_size')

    image = Array(shape=(None, None), dtype='uint8')
    histogram = Property(Array, depends_on='image')

    pixel_area = Float()

    # Trait observers

    @observe('filename')
    def read_image(self, event):
        pil_image = PILImage.open(self.filename).convert("L")
        self.image = np.array(pil_image)

        # compute some extra secondary attributes from the image
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

    # Trait property methods

    def _get_scan_width(self):
        return self.scan_size[0]

    def _set_scan_width(self, value):
        self.scan_size = (value, self.scan_size[1])

    def _get_scan_height(self):
        return self.scan_size[1]

    def _set_scan_height(self, value):
        self.scan_size = (self.scan_size[0], value)

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
            "The most frequent intensity of {} is {}".format(
                filename,
                image.histogram.argmax(),
            )
        )
