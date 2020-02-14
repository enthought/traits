from collections import defaultdict
import inspect
import re
import tempfile

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


def parse_output(output_str):
    line_errors_dict = defaultdict(list)
    for line in output_str.split("\n"):
        match = re.search(r"([0-9]*): error:", line)
        if match:
            line_no = int(match.group(1))
            line_errors_dict[line_no].append("{ERR}")
    return line_errors_dict


def run_mypy(code_string):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                     delete=True) as f:
        f.write(code_string)
        f.flush()
        normal_report, error_report, exit_status = mypy_api.run([f.name])

    return normal_report, error_report, exit_status


def getlines(multiline_string, list_line_nos):
    lines = multiline_string.split("\n")
    return [lines[i - 1] for i in list_line_nos]


class MypyAssertions(object):

    def assertNoMypyError(self, obj):
        code_string, _ = parse(obj)
        normal_report, error_report, exit_status = run_mypy(code_string)
        if exit_status != 0:
            raise AssertionError(
                f"{normal_report} {error_report} {exit_status}")

    def assertRaisesMypyError(self, obj):
        code_string, line_error_map = parse(obj)
        normal_report, error_report, exit_status = run_mypy(code_string)
        out = parse_output(normal_report)
        print(f"Expected Errors: {getlines(code_string, line_error_map.keys())}")
        print(f"Actual Errors: {getlines(code_string, out.keys())}")
        if not out.keys() == line_error_map.keys():
            raise AssertionError(f'{normal_report}')
