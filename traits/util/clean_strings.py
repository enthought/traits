# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Provides functions that mange strings to avoid characters that would be
    problematic in certain situations.
"""

# Standard library imports.
import copy
import datetime
import keyword
import re
import unicodedata


def clean_filename(name, replace_empty=""):
    """
    Make a user-supplied string safe for filename use.

    Returns an ASCII-encodable string based on the input string that's safe for
    use as a component of a filename or URL. The returned value is a string
    containing only lowercase ASCII letters, digits, and the characters '-' and
    '_'.

    This does not give a faithful representation of the original string:
    different input strings can result in the same output string.

    Parameters
    ----------
    name : str
        The string to be made safe.
    replace_empty : str, optional
        The return value to be used in the event that the sanitised
        string ends up being empty. No validation is done on this
        input - it's up to the user to ensure that the default is
        itself safe. The default is to return the empty string.

    Returns
    -------
    safe_string : str
        A filename-safe version of string.

    """
    # Code is based on Django's slugify utility.
    # https://docs.djangoproject.com/en/1.9/_modules/django/utils/text/#slugify
    name = (
        unicodedata.normalize('NFKD', name)
        .encode('ascii', 'ignore')
        .decode('ascii')
    )
    name = re.sub(r'[^\w\s-]', '', name).strip().lower()
    safe_name = re.sub(r'[-\s]+', '-', name)
    if safe_name == "":
        return replace_empty
    return safe_name


def clean_timestamp(dt=None, microseconds=False):
    """
    Return a timestamp that has been cleansed of characters that might
    cause problems in filenames, namely colons.  If no datetime object
    is provided, then uses the current time.

    The timestamp is in ISO-8601 format with the following exceptions:

    * Colons ':' are replaced by underscores '_'.
    * Microseconds are not displayed if the 'microseconds' parameter is
        False.

    Parameters
    ----------
    dt : None or datetime.datetime
        If None, then the current time is used.
    microseconds : bool
        Display microseconds or not.

    Returns
    -------
    A string timestamp.
    """
    if dt is None:
        dt = datetime.datetime.now()
    else:
        # Operate on a copy.
        dt = copy.copy(dt)

    if not microseconds:
        # The microseconds are largely uninformative but annoying.
        dt = dt.replace(microsecond=0)

    stamp = dt.isoformat().replace(":", "_")

    return stamp


def python_name(name):
    """ Attempt to make a valid Python identifier out of a name.
    """

    if len(name) > 0:
        # Replace spaces with underscores.
        name = name.replace(" ", "_").lower()

        # If the name is a Python keyword then prefix it with an
        # underscore.
        if keyword.iskeyword(name):
            name = "_" + name

        # If the name starts with a digit then prefix it with an
        # underscore.
        if name[0].isdigit():
            name = "_" + name

    return name
