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
Validation
==========

A common issue faced by scientists is ensuring that the data that is
entered matches the sort of data that is expected.  For example, we expect
that the filename is a string (or perhaps a pathlib **Path**, for advanced
users), the operator name is a string, the acquisition date is a
datetime.date object, and so on.  Many languages allow (or even require)
you to specify these data types as part of your program, but even then these
data types tend to reflect what the computer stores in memory, and not what
the data actually *represents*.

For example, not only should the file be a string, but we would like to
validate that the string is in fact a valid path name, and ideally that the
file can actually be found.  A sample ID may be expected to follow some pattern
based on lab protocols.  The image data is expected to be a 2D array of values
rather than just any NumPy array.  And so on.

Traits provides a way to ensure that values are validated when assigned in your
classes: as part of your class definition you _declare_ what you expect your
data to be.  To do this, the first thing you want to do is inherit from the
base ``HasTraits`` class which enables all of the validation machinery::

    from traits.api import HasTraits

    class Image(HasTraits):
        ''' An SEM image stored in a file. '''

Having done this, we can declare the types of data that we expect for the
attributes of an ``Image`` class.  For example, we expect that the operator
name should be a string, so we can use the standard Traits ``Str`` trait
type::

    from traits.api import HasTraits, Str

    class Image(HasTraits):
        ''' An SEM image stored in a file. '''

        operator = Str()

Now, if we try and assign any other value to the ``operator`` attribute, we
find that the class will raise a ``TraitError``::

    >>> image = Image()
    >>> image.operator = 3
    TraitError: The 'operator' trait of an Image instance must be a
    string, but a value of 3 <class 'int'> was specified.

Traits has trait types corresponding to all the basic Python data types:
``Int``, ``Float``, ``Complex``, ``Bool``, and ``Str``.  It also has trait
types for the standard containers: ``List``, ``Dict``, ``Set`` and ``Tuple``.
There is an ``Instance`` trait type for values which are instances of a
Python class.  Traits also provides a rich set of trait types that cover
many common data types, for example:

- we can use a ``Date`` trait type for the date_acquired
- we can specify that the scan size is not just a tuple, but a pair of
  floating point values by specifying ``Tuple(Float, Float)``.
- we can use a ``File`` trait for the filename, and we can require that the
  path refer to an existing file by using ``File(exists=True)``.
- we can specify that the image data is a 2D NumPy array of unsigned integers
  with ``Array(shape=(None, None), dtype='uint8')``

Everything else can remain unchanged in the class, and it will still work as
expected, however just as with regular Python classes, we need to remember
to call ``super()`` in the ``__init__`` method::

    def __init__(self, filename, sample_id, date_acquired, operator,
                 scan_size=(1e-5, 1e-5)):
        super().__init__()

        # initialize the primary attributes
        ...

When we talk about an attribute which is declared by a trait type, it is
common to call it a _trait_ rather than an attribute.


Traits and Static Types
-----------------------

The first version of Traits was written over 15 years ago.  In the last 5
years or so, Python has started to gain the ability to perform static type
checking using tools like MyPy and certain integrated development
environments.  The ``dataclass`` module introduced in recent Python versions
can do similar sorts of type declaration for classes.  Advanced Python users
may be aware of, and using these classes already.

As we will see, the capabilities of Traits are much greater than these type
checking systems, however if you have the traits-stubs package installed,
most of your trait type declarations will be recognised and can be used with
these new Python type systems.


Exercise
--------

The example code hasn't declared trait types for all the attributes used by
the class.  Declare trait types for ``scan_width``, ``scan_height`` and
``pixel_area``.

"""

import datetime
import os

from traits.api import Array, Date, HasTraits, File, Float, Str, Tuple


class Image(HasTraits):
    """ An SEM image stored in a file. """

    filename = File(exists=True)

    sample_id = Str()

    date_acquired = Date()

    operator = Str()

    scan_size = Tuple(Float, Float)

    image = Array(shape=(None, None), dtype='uint8')

    def __init__(self, filename, sample_id, date_acquired, operator,
                 scan_size=(1e-5, 1e-5)):
        super().__init__()

        # initialize the primary attributes
        self.filename = filename
        self.sample_id = sample_id
        self.scan_size = scan_size
        self.operator = operator

        # useful secondary attributes
        self.scan_width, self.scan_height = self.scan_size


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

# show all the defined traits
image.print_traits()

# we can't set the operator name to a number
print(set)
try:
    image.operator = 3
except Exception as exc:
    print(exc)

# we can't create an image which uses a non-existent path
non_existent_filename = os.path.join(image_dir, "does_not_exist.png")

try:
    image = Image(
        filename=filename,
        operator="Hannes",
        sample_id="0001",
        date_acquired=datetime.datetime.today(),
        scan_size=(1e-5, 1e-5),
    )
except Exception as exc:
    print(exc)
