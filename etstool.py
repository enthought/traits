# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

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

    python etstool.py clean --runtime=...

If you make changes you will either need to remove and re-install the
environment or manually update the environment using ``edm``, as
the install performs a ``pip install .`` rather than a ``pip install -e .``,
so changes in your code will not be automatically mirrored in the test
environment.  You can update with::

    python etstool.py update --runtime=...

You can run install, test and clean all at once with::

    python etstool.py test-clean --runtime=...

which will create, install, run tests, and then clean up the environment.  And
you can run tests in all supported runtimes::

    python etstool.py test-all

Currently supported runtime values are ``3.6``.  Not all
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
how to run commands within an EDM environment.

"""

import glob
import os
import subprocess
import sys
from shutil import rmtree, copy as copyfile
from tempfile import mkdtemp
from contextlib import contextmanager

import click

# Dependencies common to all configurations.
common_dependencies = {
    "configobj",
    "coverage",
    "cython",
    "enthought_sphinx_theme",
    "flake8",
    "lark_parser",
    "mypy",
    "numpy",
    "pyqt5",
    "Sphinx",
    "traitsui",
}

# Dependencies we install from source for testing
source_dependencies = {"traitsui"}

# Unix-specific dependencies.
unix_dependencies = {
    "gnureadline",
}

supported_runtimes = ["3.6"]
default_runtime = "3.6"

github_url_fmt = "git+http://github.com/enthought/{0}.git#egg={0}"

# Click options shared by multiple commands.
edm_option = click.option(
    "--edm",
    help=(
        "Path to the EDM executable to use. The default is to use the first "
        "EDM found in the path. The EDM executable can also be specified "
        "by setting the ETSTOOL_EDM environment variable."
    ),
    envvar="ETSTOOL_EDM",
)
runtime_option = click.option(
    "--runtime",
    default=default_runtime,
    type=click.Choice(supported_runtimes),
    show_default=True,
    help="Python runtime version for the development environment",
)
editable_option = click.option(
    "--editable/--not-editable",
    default=False,
    help="Install main package in 'editable' mode?  [default: --not-editable]",
)
verbose_option = click.option(
    "--verbose/--quiet",
    default=True,
    help="Run tests in verbose mode? [default: --verbose]",
)


@click.group()
def cli():
    """
    Developer and CI support commands for Traits.
    """
    pass


@cli.command()
@edm_option
@runtime_option
@click.option(
    "--environment",
    default=None,
    help="Name of the EDM environment to install",
)
@editable_option
@click.option("--source/--no-source", default=False)
def install(edm, runtime, environment, editable, source):
    """ Install project and dependencies into a clean EDM environment and
    optionally install further dependencies required for building
    documentation and mini-language parser.

    """
    parameters = get_parameters(edm, runtime, environment)
    dependencies = common_dependencies.copy()
    if sys.platform != "win32":
        dependencies.update(unix_dependencies)

    packages = " ".join(dependencies)

    # EDM commands to set up the development environment. The installation
    # of TraitsUI from EDM installs Traits as a dependency, so we need
    # to explicitly uninstall it before re-installing from source.
    install_traits = _get_install_command_string(".", editable=editable)
    install_stubs = _get_install_command_string(
        "./traits-stubs/", editable=editable
    )
    install_copyright_checker = _get_install_command_string(
        "copyright_header/", editable=False, no_deps=False
    )
    commands = [
        "{edm} environments create {environment} --force --version={runtime}",
        "{edm} --config edm.yaml install -y -e {environment} " + packages,
        "{edm} plumbing remove-package -e {environment} traits",
        install_traits,
        install_stubs,
        install_copyright_checker,
    ]

    click.echo("Creating environment '{environment}'".format(**parameters))
    execute(commands, parameters)
    if source:
        commands = [
            "{edm} plumbing remove-package "
            "--environment {environment} --force "
            + " ".join(source_dependencies)
        ]
        execute(commands, parameters)
        source_pkgs = [
            github_url_fmt.format(pkg) for pkg in source_dependencies
        ]
        commands = [
            "python -m pip install {pkg} --no-deps".format(pkg=pkg)
            for pkg in source_pkgs
        ]
        commands = [
            "{edm} run -e {environment} -- " + command for command in commands
        ]
        execute(commands, parameters)

    click.echo("Done install")


@cli.command()
@edm_option
@runtime_option
@click.option(
    "--environment", default=None, help="Name of EDM environment to check."
)
def flake8(edm, runtime, environment):
    """ Run a flake8 check in a given environment.

    """
    parameters = get_parameters(edm, runtime, environment)
    commands = ["{edm} run -e {environment} -- python -m flake8"]
    execute(commands, parameters)


@cli.command()
@edm_option
@runtime_option
@verbose_option
@click.option(
    "--environment", default=None, help="Name of EDM environment to test."
)
def test(edm, runtime, verbose, environment):
    """ Run the test suite in a given environment.

    """
    parameters = get_parameters(edm, runtime, environment)

    environ = {}
    environ["PYTHONUNBUFFERED"] = "1"

    options = "--verbose " if verbose else ""
    commands = [
        "{edm} run -e {environment} -- coverage run -p -m "
        "unittest discover " + options + "traits",
    ]
    commands += [
        "{edm} run -e {environment} -- coverage run -p -m "
        "unittest discover " + options + "traits_stubs_tests",
    ]

    # We run in a tempdir to avoid accidentally picking up wrong traits
    # code from a local dir.  We need to ensure a good .coveragerc is in
    # that directory, plus coverage has a bug that means a non-local coverage
    # file doesn't get populated correctly.
    click.echo("Running tests in '{environment}'".format(**parameters))
    with do_in_tempdir(
        files=[".coveragerc"], capture_files=[os.path.join(".", ".coverage*")],
    ):
        os.environ.update(environ)
        execute(commands, parameters)
    click.echo("Done test")


@cli.command()
@edm_option
@runtime_option
@click.option(
    "--environment",
    default=None,
    help="Name of EDM environment to build docs for.",
)
@click.option(
    "--error-on-warn/--no-error-on-warn",
    default=True,
    help="Turn warnings into errors?  [default: --error-on-warn] ",
)
def docs(edm, runtime, environment, error_on_warn):
    """ Build the html documentation.

    """
    parameters = get_parameters(edm, runtime, environment)
    build_docs = (
        "{edm} run -e {environment} -- sphinx-build -b html "
        + ("-W " if error_on_warn else "")
        + "-d build/doctrees source build/html"
    )
    commands = [build_docs]
    with do_in_existingdir(os.path.join(os.getcwd(), "docs")):
        execute(commands, parameters)


@cli.command()
@edm_option
@runtime_option
@click.option(
    "--environment", default=None, help="Name of EDM environment to remove."
)
def clean(edm, runtime, environment):
    """ Remove a development environment.

    """
    parameters = get_parameters(edm, runtime, environment)
    commands = [
        "{edm} environments remove {environment} --purge -y",
    ]
    click.echo("Removing environment '{environment}'".format(**parameters))
    execute(commands, parameters)
    click.echo("Environment removed.")


@cli.command(name="test-clean")
@edm_option
@runtime_option
def test_clean(edm, runtime):
    """ Run tests and build documentation in a clean environment.

    A clean EDM environment is created for the test run, and removed
    again afterwards.
    """
    args = ["--runtime={}".format(runtime)]
    if edm is not None:
        args.append("--edm={}".format(edm))

    try:
        install(args=args, standalone_mode=False)
        test(args=args, standalone_mode=False)
        docs(args=args, standalone_mode=False)
    finally:
        clean(args=args, standalone_mode=False)


@cli.command()
@edm_option
@runtime_option
@click.option(
    "--environment", default=None, help="Name of EDM environment to update."
)
@editable_option
def update(edm, runtime, environment, editable):
    """ Update/Reinstall package into environment.

    """
    parameters = get_parameters(edm, runtime, environment)
    if editable:
        install_cmd = (
            "{edm} run -e {environment} -- "
            "python -m pip install --editable . --no-dependencies"
        )
    else:
        install_cmd = (
            "{edm} run -e {environment} -- "
            "python -m pip install . --no-dependencies"
        )
    commands = [install_cmd]
    click.echo("Re-installing in  '{environment}'".format(**parameters))
    execute(commands, parameters)
    click.echo("Done update")


@cli.command(name="test-all")
@edm_option
def test_all(edm):
    """ Run test-clean across all supported environment combinations.

    """
    error = False
    for runtime in supported_runtimes:
        args = ["--runtime={}".format(runtime)]
        if edm is not None:
            args.append("--edm={}".format(edm))

        try:
            test_clean(args, standalone_mode=True)
        except SystemExit as exc:
            if exc.code not in (None, 0):
                error = True
                click.echo(str(exc))

    if error:
        sys.exit(1)


@cli.command(name="generate-parser")
@edm_option
@runtime_option
@click.option(
    "--environment", default=None, help="Name of EDM environment to use."
)
def generate_parser(edm, runtime, environment):
    """ Regenerate the mini-language parser for the observe framework.
    """
    parameters = get_parameters(edm, runtime, environment)

    root_dir = os.path.dirname(__file__)
    observers_dir = os.path.join(root_dir, "traits", "observation")

    # parser file to be generated.
    out_path = os.path.join(observers_dir, "_generated_parser.py")

    # grammar file.
    parameters["grammar_path"] = os.path.join(
        observers_dir, "_dsl_grammar.lark")

    command = (
        "{edm} run -e {environment} -- "
        "python -m lark.tools.standalone "
        "{grammar_path}"
    )

    with open(out_path, "w", encoding="utf-8") as out_file:
        execute([command], parameters, stdout=out_file)
    click.echo("Written to {out_path!r}".format(out_path=out_path))


# Utility routines

def get_parameters(edm, runtime, environment):
    """ Set up parameters dictionary for format() substitution. """

    if edm is None:
        edm = locate_edm()

    if environment is None:
        environment = "traits-test-{runtime}".format(runtime=runtime)

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
        click.echo("copying file to tempdir: {}".format(filepath))
        copyfile(filepath, path)

    os.chdir(path)
    try:
        yield path
        # retrieve any result files we want
        for pattern in capture_files:
            for filepath in glob.iglob(pattern):
                click.echo("copying file back: {}".format(filepath))
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


def execute(commands, parameters, stdout=None):
    for command in commands:
        click.echo("[EXECUTING] {}".format(command.format(**parameters)))
        try:
            subprocess.check_call(
                [arg.format(**parameters) for arg in command.split()],
                stdout=stdout,
            )
        except subprocess.CalledProcessError as exc:
            print(exc)
            sys.exit(1)


def locate_edm():
    """
    Locate an EDM executable if it exists, else raise an exception.

    Returns the first EDM executable found on the path. On Windows, if that
    executable turns out to be the "edm.bat" batch file, replaces it with the
    executable that it wraps: the batch file adds another level of command-line
    mangling that interferes with things like specifying version restrictions.

    Returns
    -------
    edm : str
        Path to the EDM executable to use.

    Raises
    ------
    click.ClickException
        If no EDM executable is found in the path.
    """
    # Once Python 2 no longer needs to be supported, we should use
    # shutil.which instead.
    which_cmd = "where" if sys.platform == "win32" else "which"
    try:
        cmd_output = subprocess.check_output([which_cmd, "edm"])
    except subprocess.CalledProcessError:
        raise click.ClickException(
            "This script requires EDM, but no EDM executable was found."
        )

    # Don't try to be clever; just use the first candidate.
    edm_candidates = cmd_output.decode("utf-8").splitlines()
    edm = edm_candidates[0]

    # Resolve edm.bat on Windows.
    if sys.platform == "win32" and os.path.basename(edm) == "edm.bat":
        edm = os.path.join(os.path.dirname(edm), "embedded", "edm.exe")

    return edm


def _get_install_command_string(pkg_or_location, editable, no_deps=True):
    """ Create and return a command string configured by the provided
    parameters.

    Parameters
    ----------
    pkg_or_location : str
        Either a location in the filesystem containing setup.py or the
        name of a package.
    editable : bool
        Whether to add --editable flag
    no_deps : bool
        Whether to add --no-dependencies flag

    Returns
    -------
    cmd : str
        A command string, which if executed will install the package or run
        the setup script at the provided location.

    """
    cmd = "{edm} run -e {environment} -- python -m pip install"
    if editable:
        cmd += " --editable"
    cmd += " {}".format(pkg_or_location)
    if no_deps:
        cmd += " --no-dependencies"
    return cmd


if __name__ == "__main__":
    cli(prog_name="python etstool.py")
