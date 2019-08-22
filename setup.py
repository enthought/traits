# Copyright (c) 2008-2019 by Enthought, Inc.
# All rights reserved.

import os
import runpy
import subprocess

import packaging.version
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

# Path to the autogenerated version file.
HERE = os.path.abspath(os.path.dirname(__file__))
VERSION_FILE = os.path.join(HERE, "traits", "_version.py")

# Template for the autogenerated version file.
VERSION_FILE_TEMPLATE = """\
# This file is autogenerated by the Traits setup.py script.
version = {version!r}
git_revision = {git_revision!r}
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
    version : packaging.version.Version
        Package version.
    git_revision : str
        The full commit hash for the current Git revision.

    Raises
    ------
    EnvironmentError
        If the version file does not exist.
    """
    version_info = runpy.run_path(VERSION_FILE)
    return (
        packaging.version.Version(version_info["version"]),
        version_info["git_revision"],
    )


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
    version = packaging.version.Version(
        (RELEASED_VERSION if IS_RELEASED else UNRELEASED_VERSION).format(
            major=MAJOR, minor=MINOR, micro=MICRO, dev=git_count
        )
    )
    return version, git_revision


def resolve_version():
    """
    Process version information and write a version file if necessary.

    Returns the version information. Raises if the version information
    already in the file appears to be incompatible with version information
    computed from Git and local information.
    """
    try:
        written_version = read_version_file()
    except EnvironmentError:
        written_version = None

    try:
        computed_version = git_version()
    except (EnvironmentError, subprocess.CalledProcessError):
        computed_version = None

    # Write the version file if it doesn't already exist, or if the
    # information it holds is out of date. Refuse to overwrite if
    # the information in the version file is newer.
    if computed_version is not None:
        if written_version is None or written_version < computed_version:
            write_version_file(*computed_version)
            written_version = computed_version
        elif computed_version < written_version:
            # Refuse to overwrite the version file with older information.
            # If developers run into this often, we may want to rethink.
            msg = (
                "The local version file at {} appears to be newer than this "
                "Git clone. Try deleting the version file and re-running."
            ).format(VERSION_FILE)
            raise RuntimeError(msg)
    elif written_version is None:
        msg = (
            "Unable to compute version information, and no version "
            "file found at {}. This may be a broken installation."
        ).format(VERSION_FILE)
        raise RuntimeError(msg)

    return written_version


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
