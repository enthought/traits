# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!


import inspect
import re
from collections import defaultdict

from mypy import api as mypy_api


def parse(obj):
    line_err_map = {}
    code, _ = inspect.getsourcelines(obj)
    code = code[1:]  # Remove the method signature
    code_string = ''

    indent = None
    line_count = 0
    for line in code:
        stripped_line = line.strip()

        if stripped_line == '':
            continue

        if indent is None:
            first_valid_char_position = line.find(stripped_line[0])
            indent = first_valid_char_position

        code_string = code_string + line[indent:]
        line_count = line_count + 1

        if "{ERR}" in line:
            line_err_map[line_count] = "{ERR}"

    return code_string, line_err_map


def parse_file(filepath):
    line_err_map = {}

    with open(filepath) as fp:
        line_count = 0
        lines = fp.readlines()
        for line in lines:
            line_count += 1
            if "{ERR}" in line:
                line_err_map[line_count] = "{ERR}"
    return line_err_map, lines


def parse_output(output_str):
    line_errors_dict = defaultdict(list)
    for line in output_str.split("\n"):
        match = re.search(r"([0-9]*): error:", line)
        if match:
            line_no = int(match.group(1))
            line_errors_dict[line_no].append("{ERR}")
    return line_errors_dict


def run_mypy(filepath):
    normal_report, error_report, exit_status = mypy_api.run([filepath])
    return normal_report, error_report, exit_status


def show_diff(input_py_lines, expect_error_line_nums_list,
              actual_error_line_nums_list):
    s = '\n'
    s += ("Expected Errors----------\n")
    for line_num in expect_error_line_nums_list:
        s += (input_py_lines[line_num - 1])

    s += ("\nActual Errors-----------\n")
    for line_num in actual_error_line_nums_list:
        s += (input_py_lines[line_num - 1])
    s += '\n'

    return s


class MypyAssertions(object):

    def assertNoMypyError(self, obj):
        code_string, _ = parse(obj)
        normal_report, error_report, exit_status = run_mypy(code_string)
        if exit_status != 0:
            raise AssertionError("Mypy Report: {}".format(normal_report))

    def assertRaisesMypyError(self, filepath):
        line_error_map, lines = parse_file(filepath)
        normal_report, error_report, exit_status = run_mypy(str(filepath))
        out = parse_output(normal_report)

        if not out.keys() == line_error_map.keys():
            s = "\n" + str(filepath)
            s += show_diff(lines, line_error_map.keys(), out.keys())
            s += normal_report
            raise AssertionError(s)
