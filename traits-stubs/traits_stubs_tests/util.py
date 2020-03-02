# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
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

from mypy import api as mypy_api


def parse_py_file(filepath):
    line_err_map = {}
    regex = re.compile(r'#[\s]*E:[\s]* (.*)')

    with open(filepath) as fp:
        line_count = 0
        lines = fp.readlines()
        for line in lines:
            line_count += 1
            match = regex.search(line)
            if match:
                err_codes = match.group(1)
                list_err_codes = err_codes.replace(' ', '').split(',')
                line_err_map[line_count] = list_err_codes
    return line_err_map, lines


def parse_mypy_output(output_str):
    line_errors_dict = defaultdict(set)
    error_line_regex = re.compile(r"([0-9]*): error:.*\[(.*)\]")
    for line in output_str.split("\n"):
        match = error_line_regex.search(line)
        if match:
            line_no_str, err_code = match.groups()
            line_errors_dict[int(line_no_str)].add(err_code)
    return line_errors_dict


def run_mypy(filepath):
    # Need to use  tempdir since mypy complains that:
    # "site-packages is in PYTHONPATH. Please change directory so it is not."

    with tempfile.TemporaryDirectory() as tempdir:
        dest_filename = os.path.basename(filepath)
        dest = shutil.copyfile(filepath, os.path.join(tempdir, dest_filename))
        normal_report, error_report, exit_status = mypy_api.run(
            [dest, '--show-error-code'])
    return normal_report, error_report, exit_status


class MypyAssertions:

    def assertNoMypyError(self, filepath):
        normal_report, error_report, exit_status = run_mypy(str(filepath))
        if exit_status != 0:
            s = "\n{}\n{}".format(filepath, normal_report)
            raise AssertionError(s)

    def assertRaisesMypyError(self, filepath):
        line_error_map, lines = parse_py_file(filepath)
        normal_report, error_report, exit_status = run_mypy(str(filepath))
        parsed_mypy_output = parse_mypy_output(normal_report)

        for line, error_codes in parsed_mypy_output.items():
            if line not in line_error_map or sorted(
                    line_error_map[line]) != sorted(list(error_codes)):
                s = "\n{}\n{}".format(filepath, normal_report)
                raise AssertionError(s)
