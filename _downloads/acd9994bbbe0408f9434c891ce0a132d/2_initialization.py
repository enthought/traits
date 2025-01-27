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
Initialization
==============

If you have done any significant amount of object-oriented Python
programming, you may have noticed that your ``__init__`` methods often
have a lot of boilerplate.  In our original example, the code copies all of
the ``__init__`` arguments to corresponding attributes before doing any
real work::

    def __init__(self, filename, sample_id, date_acquired, operator,
                 scan_size=(1e-5, 1e-5)):
        # initialize the primary attributes
        self.filename = filename
        self.sample_id = sample_id
        self.operator = operator
        self.scan_size = scan_size

Traits lets you avoid this boilerplate by defining a default ``__init__``
method that accepts keyword arguments that correspond to the declared
traits.  The Traits version of the ``Image`` class could potentially skip
the ``__init__`` method entirely::

    class Image(HasTraits):
        filename = File(exists=True)
        sample_id = Str()
        date_acquired = Date()
        operator = Str()
        scan_size = Tuple(Float, Float)


    # this works!
    image = Image(
        filename=filename,
        operator="Hannes",
        sample_id="0001",
        date_acquired=datetime.datetime.today(),
        scan_size=(1e-5, 1e-5),
    )

Default Values
--------------

There are a couple of complications in the example that we need to take into
account.  The first is what happens if a user forgets to provide an initial
value::

    >>> image = Image(
    ...     filename=filename,
    ...     sample_id="0001",
    ...     date_acquired=datetime.datetime.today(),
    ...     scan_size=(1e-5, 1e-5),
    ... )
    >>> image.operator
    ""

As this example shows, the operator gets given a default value of the empty
string ``""``.  In fact every trait type comes with an default value.  For
numeric trait types, like ``Int`` and ``Float``, the default is 0.  For
``Str`` trait types it is the empty string, for ``Bool`` traits it is
``False``, and so on.

However, that might not be what you want as your default value.  For example,
you might want to instead flag that the operator has not been provided with
the string ``"N/A"`` for "not available".  Most trait types allow you to
specify a default value as part of the declaration.  So we could say::

    operator = Str("N/A")

and now if we omit ``operator`` from the arguments, we get::

    >>> image.operator
    "N/A"


Dynamic Defaults
----------------

The second complication comes from more complex initial values.  For example,
we could declare some arbitrary fixed date as the default value for
``date_acquired``::

    date_acquired = Date(datetime.date(2020, 1, 1))

But it would be better if we could set it to a dynamic value.  For example,
a reasonable default would be today's date.  You can provide this sort of
dynamically declared default by using a specially-named method which has
the pattern ``_<trait-name>_default`` and which returns the default value.
So we could write::

    def _date_acquired_default(self):
        return datetime.datetime.today()

Dynamic defaults are best used for values which don't depend on other traits.
For example, it might be tempting to have the ``image`` trait have a dynamic
default which loads in the data.  As we will see, this is almost always
better handled by Traits observation and/or properties, which are discussed
in subsequent sections of the tutorial.


The ``traits_init`` Method
--------------------------

Although you aren't required to write an ``__init__`` method in a
``HasTraits`` subclass, you can always choose to do so.  If you do, you
**must** call ``super()`` to ensure that Traits has a chance to set up
its machinery.  In our example the ``__init__`` method is also used to set
up some auxiliary values. This doesn't have to change::

    def __init__(self, **traits):
        super().__init__(**traits)

        # useful secondary attributes
        self.scan_width, self.scan_height = self.scan_size

However Traits offers a slightlty more convenient way of doing this sort of
post-initialization setup of state: you can define a ``traits_init`` method
which the ``HasTraits`` class ensures is called as part of the main
initialization process.  When it has been called, all initial values will
have been set::

    def traits_init(self):
        # useful secondary attributes
        self.scan_width, self.scan_height = self.scan_size


Exercise
--------

In our original example, the ``scan_size`` atribute had a default value of
``(1e-5, 1e-5)``.  Modify the code in the example so that the trait is
initialized to this default using a dynamic default method.

"""


import datetime
import os

from traits.api import Array, Date, HasTraits, File, Float, Str, Tuple


class Image(HasTraits):
    """ An SEM image stored in a file. """

    filename = File(exists=True)

    sample_id = Str()

    date_acquired = Date()

    operator = Str("N/A")

    scan_size = Tuple(Float, Float)

    image = Array(shape=(None, None), dtype='uint8')

    def traits_init(self):
        # useful secondary attributes
        self.scan_width, self.scan_height = self.scan_size

    def _date_acquired_default(self):
        return datetime.datetime.today()


# ---------------------------------------------------------------------------
# Demo code
# ---------------------------------------------------------------------------

this_dir = os.path.dirname(__file__)
image_dir = os.path.join(this_dir, "images")
filename = os.path.join(image_dir, "sample_0001.png")

# load the image
image = Image(
    filename=filename,
    sample_id="0001",
    scan_size=(1e-5, 1e-5),
)

# show all the defined traits
image.print_traits()
