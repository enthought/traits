#! /usr/bin/env python
"""
USAGE: from the traits source tree:

    rm -rf build
    python setup.py clean
    python tools/c_coverage.py

This generates an html C coverage report in cover_report
"""
import os
import os.path as op

from subprocess import check_call

def blow_path(p):
    tail = p
    parts = []
    while tail != "/":
        head = op.basename(tail)
        tail = op.dirname(tail)
        parts.append(head)
    return list(reversed(parts))

def gcov_environment():
    parts = blow_path(os.getcwd())
    new_env = {
        "CFLAGS": "--coverage",
        "LDFLAGS": "--coverage",
        # Take about stupid interface to control output...
        "GCOV_PREFIX_STRIP": str(len(parts) + 2),
        "DISTUTILS_WITH_COVERAGE": "1",
    }
    new_env.update(os.environ)
    return new_env

ENV = gcov_environment()
check_call("python setup.py build_ext -i", env=ENV, shell=True)
check_call("python -m nose.core .", env=ENV, shell=True)

check_call("lcov --capture --directory . --output-file coverage.info", shell=True)
check_call("genhtml coverage.info --output-directory cover_report", shell=True)
