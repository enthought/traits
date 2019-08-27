# Copyright (c) 2008-2019 by Enthought, Inc.
# All rights reserved.

import os
import runpy
import subprocess

import setuptools

# Version information; update this by hand when making a new bugfix or feature
# release. The actual package version is autogenerated from this information
# together with information from the version control system, and then injected
# into the package source.
MAJOR = 5
MINOR = 2
MICRO = 0
IS_RELEASED = False

# Templates for version strings.
RELEASED_VERSION = "{major}.{minor}.{micro}"
UNRELEASED_VERSION = "{major}.{minor}.{micro}.dev{dev}"

# Paths to the autogenerated version file and the Git directory.
HERE = os.path.abspath(os.path.dirname(__file__))
VERSION_FILE = os.path.join(HERE, "traits", "version.py")
GIT_DIRECTORY = os.path.join(HERE, ".git")

# Template for the autogenerated version file.
VERSION_FILE_TEMPLATE = """\
# Copyright (c) 2008-2019 by Enthought, Inc.
# All rights reserved.

\"""
Version information for this Traits distribution.

This file is autogenerated by the Traits setup.py script.
\"""

from __future__ import unicode_literals

#: The full version of the package, including a development suffix
#: for unreleased versions of the package.
version = '{version}'

#: The Git revision from which this release was made.
git_revision = '{git_revision}'
"""

# Git executable to use to get revision information.
GIT = "git"


def _git_output(args):
    """
    Call Git with the given arguments and return the output as (Unicode) text.
    """
    return subprocess.check_output([GIT] + args).decode("utf-8")


def _git_info(commit="HEAD"):
    """
    Get information about the given commit from Git.

    Parameters
    ----------
    commit : str, optional
        Commit to provide information for. Defaults to "HEAD".

    Returns
    -------
    git_count : int
        Number of revisions from this commit to the initial commit.
    git_revision : str
        Commit hash for HEAD.

    Raises
    ------
    EnvironmentError
        If Git is not available.
    subprocess.CalledProcessError
        If Git is available, but the version command fails (most likely
        because there's no Git repository here).
    """
    count_args = ["rev-list", "--count", "--first-parent", commit]
    git_count = int(_git_output(count_args))

    revision_args = ["rev-list", "--max-count", "1", commit]
    git_revision = _git_output(revision_args).rstrip()

    return git_count, git_revision


def write_version_file(version, git_revision):
    """
    Write version information to the version file.

    Overwrites any existing version file.

    Parameters
    ----------
    version : packaging.version.Version
        Package version.
    git_revision : str
        The full commit hash for the current Git revision.
    """
    with open(VERSION_FILE, "w") as version_file:
        version_file.write(
            VERSION_FILE_TEMPLATE.format(
                version=str(version), git_revision=git_revision
            )
        )


def read_version_file():
    """
    Read version information from the version file, if it exists.

    Returns
    -------
    version : unicode
        The full version, including any development suffix.
    git_revision : unicode
        The full commit hash for the current Git revision.

    Raises
    ------
    EnvironmentError
        If the version file does not exist.
    """
    version_info = runpy.run_path(VERSION_FILE)
    return (version_info["version"], version_info["git_revision"])


def git_version():
    """
    Construct version information from local variables and Git.

    Returns
    -------
    version : packaging.version.Version
        Package version.
    git_revision : str
        The full commit hash for the current Git revision.

    Raises
    ------
    EnvironmentError
        If Git is not available.
    subprocess.CalledProcessError
        If Git is available, but the version command fails (most likely
        because there's no Git repository here).
    """
    git_count, git_revision = _git_info()
    version_template = RELEASED_VERSION if IS_RELEASED else UNRELEASED_VERSION
    version = version_template.format(
        major=MAJOR, minor=MINOR, micro=MICRO, dev=git_count
    )
    return version, git_revision


def resolve_version():
    """
    Process version information and write a version file if necessary.

    Returns the current version information.

    Returns
    -------
    version : packaging.version.Version
        Package version.
    git_revision : str
        The full commit hash for the current Git revision.
    """
    if os.path.isdir(GIT_DIRECTORY):
        # This is a local clone; compute version information and write
        # it to the version file, overwriting any existing information.
        version = git_version()
        print("Computed package version: {}".format(version))
        print("Writing version to version file {}.".format(VERSION_FILE))
        write_version_file(*version)
    elif os.path.isfile(VERSION_FILE):
        # This is a source distribution. Read the version information.
        print("Reading version file {}".format(VERSION_FILE))
        version = read_version_file()
        print("Package version from version file: {}".format(version))
    else:
        raise RuntimeError(
            "Unable to determine package version. No local Git clone "
            "detected, and no version file found at {}.".format(VERSION_FILE)
        )

    return version


version, git_revision = resolve_version()

setuptools.setup(
    name="traits",
    version=str(version),
    url="http://docs.enthought.com/traits",
    author="Enthought",
    author_email="info@enthought.com",
    classifiers=[
        c.strip()
        for c in """
        Development Status :: 5 - Production/Stable
        Intended Audience :: Developers
        Intended Audience :: Science/Research
        License :: OSI Approved :: BSD License
        Operating System :: MacOS :: MacOS X
        Operating System :: Microsoft :: Windows
        Operating System :: POSIX :: Linux
        Programming Language :: C
        Programming Language :: Python
        Programming Language :: Python :: 2
        Programming Language :: Python :: 2.7
        Programming Language :: Python :: 3
        Programming Language :: Python :: 3.5
        Programming Language :: Python :: 3.6
        Programming Language :: Python :: 3.7
        Programming Language :: Python :: Implementation :: CPython
        Topic :: Scientific/Engineering
        Topic :: Software Development
        Topic :: Software Development :: Libraries
        Topic :: Software Development :: User Interfaces
        """.splitlines()
        if len(c.strip()) > 0
    ],
    description="Explicitly typed attributes for Python",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    download_url="https://github.com/enthought/traits",
    install_requires=["six"],
    ext_modules=[setuptools.Extension("traits.ctraits", ["traits/ctraits.c"])],
    license="BSD",
    maintainer="ETS Developers",
    maintainer_email="enthought-dev@enthought.com",
    packages=setuptools.find_packages(include=["traits", "traits.*"]),
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    zip_safe=False,
)
