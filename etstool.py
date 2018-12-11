#
#  Copyright (c) 2017, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
"""
Tasks for Test Runs
===================

This file is intended to be used with a python environment with the
click library to automate the process of setting up test environments
and running the test within them.  This improves repeatability and
reliability of tests be removing many of the variables around the
developer's particular Python environment.  Test environment setup and
package management is performed using `EDM
http://docs.enthought.com/edm/`_

To use this to run you tests, you will need to install EDM and click
into your working environment.  You will also need to have git
installed to access required source code from github repositories.
You can then do::

    python etstool.py install --runtime=...

to create a test environment from the current codebase and::

    python etstool.py test --runtime=...

to run tests in that environment.  You can remove the environment with::

    python etstool.py cleanup --runtime=...

If you make changes you will either need to remove and re-install the
environment or manually update the environment using ``edm``, as
the install performs a ``python setup.py install`` rather than a ``develop``,
so changes in your code will not be automatically mirrored in the test
environment.  You can update with a command like::

    edm run --environment ... -- python setup.py install

You can run all three tasks at once with::

    python etstool.py test_clean --runtime=...

which will create, install, run tests, and then clean-up the environment.  And
you can run tests in all supported runtimes::

    python etstool.py test_all

Currently supported runtime values are ``2.7`` and ``3.5``.  Not all
combinations of runtimes will work, but the tasks will fail with
a clear error if that is the case.

Tests can still be run via the usual means in other environments if that suits
a developer's purpose.

Changing This File
------------------

To change the packages installed during a test run, change the dependencies
variable below.  To install a package from github, or one which is not yet
available via EDM, add it to the `ci-src-requirements.txt` file (these will be
installed by `pip`).

Other changes to commands should be a straightforward change to the listed
commands for each task. See the EDM documentation for more information about
how to run commands within an EDM enviornment.

"""

import glob
import os
import platform
import subprocess
import sys
from shutil import rmtree, copy as copyfile
from tempfile import mkdtemp
from contextlib import contextmanager

import click

dependencies = {
    "coverage",
    "cython",
    "Sphinx",
    "mock",
    "nose",

}

supported_runtimes = ["2.7.13", "3.5.2", "3.6.0"]

@click.group()
def cli():
    pass


@cli.command()
@click.option('--runtime', default='3.6')
@click.option('--environment', default=None)
def install(runtime, environment):
    """ Install project and dependencies into a clean EDM environment.

    """
    parameters = get_parameters(runtime, environment)
    packages = ' '.join(dependencies)
    # edm commands to setup the development environment
    commands = [
        "edm environments create {environment} --force --version={runtime}",
        "edm install -y -e {environment} " + packages,
        "edm run -e {environment} -- pip install -r ci-src-requirements.txt --no-dependencies",
        "edm run -e {environment} -- python setup.py clean --all",
        "edm run -e {environment} -- python setup.py install",
    ]
    # pip install pyqt5 and pyside2, because we don't have them in EDM yet

    click.echo("Creating environment '{environment}'".format(**parameters))
    execute(commands, parameters)
    click.echo('Done install')


@cli.command()
@click.option('--runtime', default='3.6')
@click.option('--environment', default=None)
def test(runtime, environment):
    """ Run the test suite in a given environment.

    """
    parameters = get_parameters(runtime, environment)

    environ =  {}
    environ['PYTHONUNBUFFERED'] = "1"

    commands = [
        "edm run -e {environment} -- coverage run -p -m nose.core -v traits --nologcapture"
    ]

    # We run in a tempdir to avoid accidentally picking up wrong traits
    # code from a local dir.  We need to ensure a good .coveragerc is in
    # that directory, plus coverage has a bug that means a non-local coverage
    # file doesn't get populated correctly.
    click.echo("Running tests in '{environment}'".format(**parameters))
    with do_in_tempdir(
        files=['.coveragerc'],
        capture_files=[os.path.join('.', '.coverage*')],
    ):
        os.environ.update(environ)
        execute(commands, parameters)
    click.echo('Done test')


@cli.command()
@click.option('--runtime', default='3.6')
@click.option('--environment', default=None)
def cleanup(runtime, environment):
    """ Remove a development environment.

    """
    parameters = get_parameters(runtime, environment)
    commands = [
        "edm run -e {environment} -- python setup.py clean",
        "edm environments remove {environment} --purge -y"
    ]
    click.echo("Cleaning up environment '{environment}'".format(**parameters))
    execute(commands, parameters)
    click.echo('Done cleanup')


@cli.command()
@click.option('--runtime', default='3.6')
def test_clean(runtime):
    """ Run tests in a clean environment, cleaning up afterwards

    """
    args = ['--runtime={}'.format(runtime)]
    try:
        install(args=args, standalone_mode=False)
        test(args=args, standalone_mode=False)
    finally:
        cleanup(args=args, standalone_mode=False)


@cli.command()
@click.option('--runtime', default='3.6')
@click.option('--environment', default=None)
def update(runtime, environment):
    """ Update/Reinstall package into environment.

    """
    parameters = get_parameters(runtime, environment)
    commands = ["edm run -e {environment} -- python setup.py install"]
    click.echo("Re-installing in  '{environment}'".format(**parameters))
    execute(commands, parameters)
    click.echo('Done update')


@cli.command()
def test_all():
    """ Run test_clean across all supported environment combinations.

    """
    error = False
    for runtime in supported_runtimes:
        args = ['--runtime={}'.format(runtime)]
        try:
            test_clean(args, standalone_mode=True)
        except SystemExit as exc:
            if exc.code not in (None, 0):
                error = True
                click.echo(str(exc))

    if error:
        sys.exit(1)

# ----------------------------------------------------------------------------
# Utility routines
# ----------------------------------------------------------------------------


def get_parameters(runtime, environment):
    """ Set up parameters dictionary for format() substitution """
    parameters = {
        'runtime': runtime,
        'environment': environment
    }
    if environment is None:
        parameters['environment'] = 'traits-test-{runtime}'.format(
            **parameters
        )
    return parameters


@contextmanager
def do_in_tempdir(files=(), capture_files=()):
    """ Create a temporary directory, cleaning up after done.

    Creates the temporary directory, and changes into it.  On exit returns to
    original directory and removes temporary dir.

    Parameters
    ----------
    files : sequence of filenames
        Files to be copied across to temporary directory.
    capture_files : sequence of filenames
        Files to be copied back from temporary directory.
    """
    path = mkdtemp()
    old_path = os.getcwd()

    # send across any files we need
    for filepath in files:
        click.echo('copying file to tempdir: {}'.format(filepath))
        copyfile(filepath, path)

    os.chdir(path)
    try:
        yield path
        # retrieve any result files we want
        for pattern in capture_files:
            for filepath in glob.iglob(pattern):
                click.echo('copying file back: {}'.format(filepath))
                copyfile(filepath, old_path)
    finally:
        os.chdir(old_path)
        rmtree(path)


def execute(commands, parameters):
    for command in commands:
        click.echo("[EXECUTING] {}".format(command.format(**parameters)))
        try:
            subprocess.check_call([
                arg.format(**parameters) for arg in command.split()
            ])
        except subprocess.CalledProcessError as exc:
            print(exc)
            sys.exit(1)


if __name__ == '__main__':
    cli()
