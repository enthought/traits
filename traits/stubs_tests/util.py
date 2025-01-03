# (C) Copyright 2020-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!


from collections import defaultdict
import os
import shutil
import re
import tempfile


def parse_py_file(filepath):
    """ This function parses a python file that have been annotated with error
    codes that mypy may generate and returns a mapping from line number to
    a list of those codes.

    File annotations may be done by adding a comment to the line that begins
    with "E:" followed by a list of comma separated error codes
    Eg::

        obj.var = False  # E: assignment, list-item

    Parameters
    ----------
    filepath : pathlib.Path
        The filepath of the python file

    Returns
    -------
    line_err_map : dict
        A mapping from line number to the list of error codes on that line
    """
    line_err_map = {}
    regex = re.compile(r'#[\s]*E:[\s]* (.*)')

    with filepath.open(encoding="utf-8") as fp:
        line_count = 0
        lines = fp.readlines()
        for line in lines:
            line_count += 1
            match = regex.search(line)
            if match:
                err_codes = match.group(1)
                list_err_codes = err_codes.replace(' ', '').split(',')
                line_err_map[line_count] = list_err_codes
    return line_err_map


def parse_mypy_output(output_str):
    """ Parses the output generated by mypy and returns a dict of mappings from
    line number to a list of error codes

    Parameters
    ----------
    output_str: str
        The output generated by mypy on stdout.

    Returns
    -------
    line_errors_dict : dict
        A mapping from line number to a list of error codes

    """
    line_errors_dict = defaultdict(set)
    error_line_regex = re.compile(r"([0-9]*): error:.*\[(.*)\]")
    for line in output_str.split("\n"):
        match = error_line_regex.search(line)
        if match:
            line_no_str, err_code = match.groups()
            line_errors_dict[int(line_no_str)].add(err_code)
    return line_errors_dict


def run_mypy(filepath):
    """ Runs mypy on the file using mypy api and returns the generated output.

    Parameters
    ----------
    filepath : pathlib.path
        The path to of the file to run mypy on.

    Returns
    -------
    normal_report : str
        Output on stdout
    error_report : str
        Output on stderr
    exit_status : int
        The exit status

    """
    # Local import to make it easier to skip tests if mypy is not in
    # the environment.
    from mypy import api as mypy_api

    # Need to use  tempdir since mypy complains that:
    # "site-packages is in PYTHONPATH. Please change directory so it is not."
    filepath = str(filepath)

    with tempfile.TemporaryDirectory() as tempdir:
        dest_filename = os.path.basename(filepath)
        dest = shutil.copyfile(filepath, os.path.join(tempdir, dest_filename))
        normal_report, error_report, exit_status = mypy_api.run(
            [dest, '--show-error-code', '--follow-imports=skip'])
    return normal_report, error_report, exit_status


class MypyAssertions:

    def assertNoMypyError(self, filepath):
        """ Raises an AssertionError if mypy raises any error.

        Parameters
        ----------
        filepath : pathlib.Path
            The path to the file to run mypy on.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If my generates any error

        """
        normal_report, error_report, exit_status = run_mypy(filepath)
        if exit_status != 0:
            s = "\n{}\n{}".format(str(filepath), normal_report)
            raise AssertionError(s)

    def assertRaisesMypyError(self, filepath):
        """ Raises an AssertionError if the errors raised by mypy are different
        from the expected errors annotated in the file. Any difference from
        expected errors, whether more or less errors will raise an
        Assertion Error

        Parameters
        ----------
        filepath : pathlib.Path
            The path to the file to run mypy on.

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If errors generated by mypy are different from expected errors.

        """
        line_error_map = parse_py_file(filepath)
        normal_report, error_report, exit_status = run_mypy(filepath)
        parsed_mypy_output = parse_mypy_output(normal_report)

        for line, error_codes in parsed_mypy_output.items():
            if line not in line_error_map or sorted(
                    line_error_map[line]) != sorted(list(error_codes)):
                s = "Unexpected error on line {}\n{}\n{}".format(
                    line, str(filepath), normal_report)
                raise AssertionError(s)
