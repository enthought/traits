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
    line_err_map = defaultdict(list)
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

        match = re.search(r'#[\s]*E:[\s]* (.*)', line)
        if match:
            err_codes = match.group(1)
            list_err_codes = err_codes.replace(' ', '').split(',')
            line_err_map[line_count] = list_err_codes

    return code_string, line_err_map


def parse_file(filepath):
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


def parse_output(output_str):
    line_errors_dict = defaultdict(set)
    error_line_regex = re.compile(r"([0-9]*): error:.*\[(.*)\]")
    for line in output_str.split("\n"):
        match = error_line_regex.search(line)
        if match:
            line_no_str, err_code = match.groups()
            line_errors_dict[int(line_no_str)].add(err_code)
    return line_errors_dict


def run_mypy(filepath):
    normal_report, error_report, exit_status = mypy_api.run(
        [filepath, '--show-error-code'])
    return normal_report, error_report, exit_status


class MypyAssertions(object):

    def assertNoMypyError(self, obj):
        code_string, _ = parse(obj)
        normal_report, error_report, exit_status = run_mypy(code_string)
        if exit_status != 0:
            raise AssertionError("Mypy Report: {}".format(normal_report))

    def assertRaisesMypyError(self, filepath):
        line_error_map, lines = parse_file(filepath)
        normal_report, error_report, exit_status = run_mypy(str(filepath))
        parsed_mypy_output = parse_output(normal_report)

        for line, error_codes in parsed_mypy_output.items():
            if sorted(line_error_map[line]) != sorted(list(error_codes)):
                s = "\n{}\n{}".format(filepath, normal_report)
                raise AssertionError(s)
