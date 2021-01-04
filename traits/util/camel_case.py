# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines utility functions for operating on camel case names.
"""

# Standard library imports.
import functools
import re

###############################################################################
# Classes
###############################################################################


class CamelCaseToPython:
    """ Simple functor class to convert names from camel case to idiomatic
    Python variable names.

    For example::
        >>> camel2python = CamelCaseToPython
        >>> camel2python('XMLActor2DToSGML')
        'xml_actor2d_to_sgml'
    """

    def __init__(self):
        self.patn = re.compile(r"([A-Z0-9]+)([a-z0-9]*)")
        self.nd_patn = re.compile(r"(\D[123])_D")

    def __call__(self, name):
        ret = self.patn.sub(self._repl, name)
        ret = self.nd_patn.sub(r"\1d", ret)
        if ret[0] == "_":
            ret = ret[1:]
        return ret.lower()

    def _repl(self, m):
        g1 = m.group(1)
        g2 = m.group(2)
        if len(g1) > 1:
            if g2:
                return "_" + g1[:-1] + "_" + g1[-1] + g2
            else:
                return "_" + g1
        else:
            return "_" + g1 + g2


###############################################################################
# Functions
###############################################################################

# Instantiate a converter.
camel_case_to_python = CamelCaseToPython()


def camel_case_to_words(s):
    """ Convert a camel case string into words separated by spaces.

    For example::
        >>> camel_case_to_words('CamelCase')
        'Camel Case'
    """

    def add_space_between_words(s, c):
        # We detect a word boundary if the character we are looking at is
        # upper case, but the character preceding it is lower case.
        if len(s) > 0 and s[-1].islower() and c.isupper():
            return s + " " + c

        return s + c

    return functools.reduce(add_space_between_words, s, "")
