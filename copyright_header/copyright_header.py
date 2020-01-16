# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import re

# Minimum end year for the copyright statement.
MINIMUM_END_YEAR = 2020

# Regular expression to match things of the form "2019" or of the form
# "2010-2019".
YEAR_RANGE = r"(?P<start_year>\d{4})(?:\-(?P<end_year>\d{4}))?"

# Generic copyright, used for searching for multiple copyright headers.
GENERIC_COPYRIGHT = re.compile("# .*Copyright .*Enthought", re.IGNORECASE)

# Template for a regular expression for the copyright header.
PRODUCT_CODE_HEADER_TEMPLATE = r"""
# \(C\) Copyright {year_range} {company_name}
# All rights reserved\.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE\.txt and may be redistributed only under
# the conditions described in the aforementioned license\. The license
# is also available online at http://www\.enthought\.com/licenses/BSD\.txt
#
# Thanks for using Enthought open source!
""".lstrip()

ENTHOUGHT_PRODUCT_CODE_HEADER = re.compile(
    PRODUCT_CODE_HEADER_TEMPLATE.format(
        company_name=r"Enthought, Inc\., Austin, TX", year_range=YEAR_RANGE,
    )
)


def parse_years(header_text):
    """
    Parse a copyright year range from a header string.

    Looks for a year range of the form "2019" or "2010-2019", and
    returns the start and end year.

    If there are multiple year ranges, parses only the first.

    Parameters
    ----------
    header_text : str
        The text to be parsed. Could be the entire copyright header,
        or a single line from the copyright header.

    Returns
    -------
    start_year, end_year : int
        Start year and end year described by the range.
    match_pos : int
        Position within the string at which the match occurred.

    Raises
    ------
    ValueError
        If no year range is recognised from the given string.
    """
    years_match = re.search(YEAR_RANGE, header_text)
    if not years_match:
        raise ValueError("No year range found in the given string.")

    start_year = int(years_match.group("start_year"))
    end_year_str = years_match.group("end_year")
    end_year = int(end_year_str) if end_year_str is not None else start_year
    return start_year, end_year, years_match.start()


class HeaderError:
    """
    Base class for the copyright header errors.
    """

    def __init__(self, lineno, col_offset):
        self.lineno = lineno
        self.col_offset = col_offset

    @property
    def full_message(self):
        """
        Full message in the form expected by flake8 (including the error code).
        """
        return "{} {}".format(self.code, self.message)


class MissingCopyrightHeaderError(HeaderError):
    """
    Error reported when no copyright header can be identified.
    """

    code = "H101"
    message = "Missing copyright header"


class DuplicateCopyrightHeaderError(HeaderError):
    """
    Error reported if multiple copyright headers found.
    """

    code = "H102"
    message = "Multiple copyright headers found"


class IncorrectCopyrightHeaderError(HeaderError):
    """
    Error reported if a copyright header is found, but its wording
    doesn't match the officially approved wording.
    """

    code = "H103"
    message = "Wrong copyright header found"


class OutdatedCopyrightYearError(HeaderError):
    """
    Error reported if the copyright header doesn't have the correct
    year information in it.
    """

    code = "H104"

    def __init__(self, lineno, col_offset, end_year):
        super().__init__(lineno=lineno, col_offset=col_offset)
        self.end_year = end_year

    @property
    def message(self):
        return (
            "Copyright end year ({}) out of date. The year should be at "
            "least {}.".format(self.end_year, MINIMUM_END_YEAR)
        )


def copyright_header(lines):
    """
    Check copyright header presence and accuracy in a Python file.
    """
    file_contents = "".join(lines)

    # Empty files don't need a copyright header.
    if not file_contents:
        return

    # Not an empty file. See if we have a copyright header at all.
    copyrights_found = []
    for lineno, line in enumerate(lines, start=1):
        if re.match(GENERIC_COPYRIGHT, line):
            copyrights_found.append(lineno)

    if not copyrights_found:
        yield MissingCopyrightHeaderError(
            lineno=1, col_offset=0,
        )
        return

    if len(copyrights_found) > 1:
        # Multiple possible copyright statements; report each one
        # beyond the first, but we still check the first for
        # correctness below.
        for lineno in copyrights_found[1:]:
            yield DuplicateCopyrightHeaderError(
                lineno=lineno, col_offset=0,
            )

    # Check that the first copyright statement is the right one.
    header_match = ENTHOUGHT_PRODUCT_CODE_HEADER.match(file_contents)
    if header_match is None:
        yield IncorrectCopyrightHeaderError(
            lineno=1, col_offset=0,
        )
        return

    # Check the year range in the header.
    for lineno, line in enumerate(lines, start=1):
        try:
            start_year, end_year, match_pos = parse_years(line)
        except ValueError:
            pass
        else:
            break

    if end_year < MINIMUM_END_YEAR:
        yield OutdatedCopyrightYearError(
            lineno=lineno, col_offset=match_pos, end_year=end_year,
        )


class CopyrightHeaderExtension(object):
    """
    Flake8 extension for checking ETS copyright headers.
    """

    name = "headers"
    version = "1.1.0"

    def __init__(self, tree, lines):
        self.lines = lines

    def run(self):
        for error in copyright_header(self.lines):
            yield (
                error.lineno,
                error.col_offset,
                error.full_message,
                type(self),
            )
