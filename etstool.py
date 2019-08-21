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

This file is intended to be used in a Python environment equipped with the
click library, to automate the process of setting up test environments
and running the tests within them.  This improves repeatability and
reliability of tests be removing many of the variables around the
developer's particular Python environment.  Test environment setup and
package management is performed using `EDM http://docs.enthought.com/edm/`_

To use this to run your tests, you will need to install EDM and click
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
the install performs a ``pip install .`` rather than a ``pip install -e .``,
so changes in your code will not be automatically mirrored in the test
environment.  You can update with::

    python etstool.py update --runtime=...

You can run install, test and cleanup all at once with::

    python etstool.py test-clean --runtime=...

which will create, install, run tests, and then clean up the environment.  And
you can run tests in all supported runtimes::

    python etstool.py test-all

Currently supported runtime values are ``2.7``, ``3.5`` and ``3.6``.  Not all
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
import subprocess
import sys
from shutil import rmtree, copy as copyfile
from tempfile import mkdtemp
from contextlib import contextmanager

import click

# Dependencies common to both Python 2 and Python 3.
common_dependencies = {
    "coverage",
    "cython",
    "enthought_sphinx_theme",
    "nose",
    "numpy",
    "pyqt",
    "Sphinx",
    "traitsui",
}

# Dependencies we install from source for testing
source_dependencies = {
    "traitsui"
}

# Python 2-specific dependencies.
python2_dependencies = {
    "mock",
}

supported_runtimes = ["2.7", "3.5", "3.6"]
default_runtime = "3.6"

github_url_fmt = "git+http://github.com/enthought/{0}.git#egg={0}"


@click.group()
def cli():
    """
    Developer and CI support for Traits.
    """
    pass


edm_option = click.option(
    "--edm",
    help=(
        "Path to the EDM executable to use. The default is to use the first "
        "EDM found in the path. The EDM executable can also be specified "
        "by setting the ETSTOOL_EDM variable."
    ),
    envvar="ETSTOOL_EDM",
)

runtime_option = click.option(
    '--runtime',
    default=default_runtime,
    type=click.Choice(supported_runtimes),
    show_default=True,
    help="Python runtime version for the development environment",
)


@cli.command()
@edm_option
@runtime_option
@click.option('--environment', default=None)
@click.option('--docs/--no-docs', default=True)
@click.option('--source/--no-source', default=False)
def install(edm, runtime, environment, docs, source):
    """ Install project and dependencies into a clean EDM environment and
    optionally install further dependencies required for building
    documentation.

    """
    parameters = get_parameters(edm, runtime, environment)
    dependencies = common_dependencies.copy()
    if runtime.startswith("2."):
        dependencies.update(python2_dependencies)
    packages = ' '.join(dependencies)
    # edm commands to setup the development environment
    commands = [
        "{edm} environments create {environment} --force --version={runtime}",
        "{edm} install -y -e {environment} " + packages,
        "{edm} run -e {environment} -- python -m pip install --no-deps .",
    ]
    click.echo("Creating environment '{environment}'".format(**parameters))
    execute(commands, parameters)
    if source:
        commands = [
            "{edm} plumbing remove-package "
            "--environment {environment} --force "
            + ' '.join(source_dependencies)
        ]
        execute(commands, parameters)
        source_pkgs = [
            github_url_fmt.format(pkg) for pkg in source_dependencies]
        commands = [
            "python -m pip install {pkg} --no-deps".format(pkg=pkg)
            for pkg in source_pkgs
        ]
        commands = [
            "{edm} run -e {environment} -- " + command for command in commands]
        execute(commands, parameters)
    if docs:
        commands = [
            "{edm} run -e {environment} -- pip install -r "
            "ci-doc-requirements.txt --no-dependencies"
        ]
        execute(commands, parameters)
        click.echo("Installed enthought-sphinx-theme in '"
                   "{environment}'.".format(**parameters))
    click.echo('Done install')


@cli.command()
@edm_option
@runtime_option
@click.option('--environment', default=None)
def test(edm, runtime, environment):
    """ Run the test suite in a given environment.

    """
    parameters = get_parameters(edm, runtime, environment)

    environ = {}
    environ['PYTHONUNBUFFERED'] = "1"

    commands = [
        "{edm} run -e {environment} -- coverage run -p -m nose.core -v traits "
        "--nologcapture"
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
@edm_option
@runtime_option
@click.option('--environment', default=None)
def docs(edm, runtime, environment):
    """ Build the html documentation.

    """
    parameters = get_parameters(edm, runtime, environment)
    commands = [
        "{edm} run -e {environment} -- sphinx-build -b html "
        "-d build/doctrees source build/html",
    ]
    with do_in_existingdir(os.path.join(os.getcwd(), 'docs')):
        execute(commands, parameters)


@cli.command()
@edm_option
@runtime_option
@click.option('--environment', default=None)
def cleanup(edm, runtime, environment):
    """ Remove a development environment.

    """
    parameters = get_parameters(edm, runtime, environment)
    commands = [
        "{edm} run -e {environment} -- python setup.py clean",
        "{edm} environments remove {environment} --purge -y",
    ]
    click.echo("Cleaning up environment '{environment}'".format(**parameters))
    execute(commands, parameters)
    click.echo('Done cleanup')


@cli.command(name='test-clean')
@runtime_option
def test_clean(runtime):
    """ Run tests in a clean environment, cleaning up afterwards

    """
    args = ['--runtime={}'.format(runtime)]
    try:
        install(args=args, standalone_mode=False)
        test(args=args, standalone_mode=False)
        docs(args=args, standalone_mode=False)
    finally:
        cleanup(args=args, standalone_mode=False)


@cli.command()
@edm_option
@runtime_option
@click.option('--environment', default=None)
def update(edm, runtime, environment):
    """ Update/Reinstall package into environment.

    """
    parameters = get_parameters(edm, runtime, environment)
    commands = [
        "{edm} run -e {environment} -- python -m pip install --no-deps .",
    ]
    click.echo("Re-installing in  '{environment}'".format(**parameters))
    execute(commands, parameters)
    click.echo('Done update')


@cli.command(name='test-all')
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


def get_parameters(edm, runtime, environment):
    """ Set up parameters dictionary for format() substitution. """

    if edm is None:
        edm = locate_edm()

    if environment is None:
        environment = 'traits-test-{runtime}'.format(runtime=runtime)

    return {
        "edm": edm,
        "runtime": runtime,
        "environment": environment,
    }


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


@contextmanager
def do_in_existingdir(path):
    """ Changes into an existing directory given by path.
    On exit, changes back to the original directory.

    Parameters
    ----------
    path : str
        Path of the directory to be changed into.
    """
    old_path = os.getcwd()
    os.chdir(path)
    try:
        yield path
    finally:
        os.chdir(old_path)


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


def locate_edm():
    """
    Locate an EDM executable, and raise a click exception if not found.

    Returns
    -------
    edm : str
        Path to the EDM executable to use.
    """
    if sys.platform == "win32":
        cmd = ["where", "edm"]
    else:
        cmd = ["which", "edm"]

    try:
        cmd_output = subprocess.check_output(cmd)
    except subprocess.CalledProcessError:
        raise click.ClickException(
            "This script requires EDM, but no EDM executable was found.")

    # Don't try to be clever; just use the first candidate.
    edm_candidates = cmd_output.decode("utf-8").splitlines()
    edm = edm_candidates[0]

    # On Windows, resolve edm.bat to the executable it wraps (the edm.bat
    # wrapper mangles command lines in problematic ways).
    if sys.platform == "win32" and os.path.basename(edm) == "edm.bat":
        edm = os.path.join(os.path.dirname(edm), "embedded", "edm.exe")

    return edm


if __name__ == '__main__':
    cli(prog_name="python etstool.py")
