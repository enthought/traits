# Copyright (c) 2008-2013 by Enthought, Inc.
# All rights reserved.
import os
import re
import subprocess
import sys

from setuptools import setup, Extension, find_packages

MAJOR = 5
MINOR = 1
MICRO = 1

IS_RELEASED = True

VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)


# Return the git revision as a string
def git_version():
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, env=env,
        ).communicate()[0]
        return out

    try:
        encoded_git_revision = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
    except OSError:
        git_revision = "Unknown"
    else:
        git_revision = encoded_git_revision.decode("ascii").strip()

    try:
        out = _minimal_ext_cmd(['git', 'describe', '--tags'])
    except OSError:
        out = ''

    git_description = out.decode('ascii').strip()
    expr = r'.*?\-(?P<count>\d+)-g(?P<hash>[a-fA-F0-9]+)'
    match = re.match(expr, git_description)
    if match is None:
        git_count = '0'
    else:
        git_count = match.group('count')

    return git_revision, git_count


def write_version_py(filename='traits/_version.py'):
    template = """\
# THIS FILE IS GENERATED FROM TRAITS SETUP.PY
version = '{version}'
full_version = '{full_version}'
git_revision = '{git_revision}'
is_released = {is_released}

if not is_released:
    version = full_version
"""
    # Adding the git rev number needs to be done inside
    # write_version_py(), otherwise the import of traits._version messes
    # up the build under Python 3.
    fullversion = VERSION
    if os.path.exists('.git'):
        git_rev, dev_num = git_version()
    elif os.path.exists('traits/_version.py'):
        # must be a source distribution, use existing version file
        try:
            from traits._version import git_revision as git_rev
            from traits._version import full_version as full_v
        except ImportError:
            raise ImportError("Unable to import git_revision. Try removing "
                              "traits/_version.py and the build directory "
                              "before building.")

        match = re.match(r'.*?\.dev(?P<dev_num>\d+)', full_v)
        if match is None:
            dev_num = '0'
        else:
            dev_num = match.group('dev_num')
    else:
        git_rev = 'Unknown'
        dev_num = '0'

    if not IS_RELEASED:
        fullversion += '.dev{0}'.format(dev_num)

    with open(filename, "wt") as fp:
        fp.write(template.format(version=VERSION,
                                 full_version=fullversion,
                                 git_revision=git_rev,
                                 is_released=IS_RELEASED))


def check_python_version():
    """
    Check that this version of Python is supported.

    Raise SystemExit for unsupported Python versions.
    """
    supported_python_version = (
        (2, 7) <= sys.version_info < (3,)
        or (3, 4) <= sys.version_info
    )
    if not supported_python_version:
        sys.exit(
            (
                "Python version {0} is not supported by Traits. "
                "Traits requires Python >= 2.7 or Python >= 3.4."
            ).format(sys.version_info)
        )


if __name__ == "__main__":
    check_python_version()
    write_version_py()
    from traits import __version__, __requires__

    ctraits = Extension(
        'traits.ctraits',
        sources=['traits/ctraits.c'],
        extra_compile_args=['-DNDEBUG=1', '-O3'],
        )

    def additional_commands():
        # Pygments 2 isn't supported on Python 3 versions earlier than 3.3, so
        # don't make the documentation command available there.
        if (3,) <= sys.version_info < (3, 3):
            return {}

        try:
            from sphinx.setup_command import BuildDoc
        except ImportError:
            return {}
        else:
            return {'documentation': BuildDoc}

    setup(
        name='traits',
        version=__version__,
        url='http://docs.enthought.com/traits',
        author='David C. Morrill, et. al.',
        author_email='info@enthought.com',
        classifiers=[c.strip() for c in """\
            Development Status :: 5 - Production/Stable
            Intended Audience :: Developers
            Intended Audience :: Science/Research
            License :: OSI Approved :: BSD License
            Operating System :: MacOS
            Operating System :: Microsoft :: Windows
            Operating System :: OS Independent
            Operating System :: POSIX
            Operating System :: Unix
            Programming Language :: C
            Programming Language :: Python
            Programming Language :: Python :: 2
            Programming Language :: Python :: 2.7
            Programming Language :: Python :: 3
            Programming Language :: Python :: 3.4
            Programming Language :: Python :: 3.5
            Programming Language :: Python :: 3.6
            Programming Language :: Python :: Implementation :: CPython
            Topic :: Scientific/Engineering
            Topic :: Software Development
            Topic :: Software Development :: Libraries
            """.splitlines() if len(c.strip()) > 0],
        description='explicitly typed attributes for Python',
        long_description=open('README.rst').read(),
        download_url='https://github.com/enthought/traits',
        install_requires=__requires__,
        ext_modules=[ctraits],
        license='BSD',
        maintainer='ETS Developers',
        maintainer_email='enthought-dev@enthought.com',
        packages=find_packages(),
        platforms=["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
        zip_safe=False,
        use_2to3=False,
        cmdclass=additional_commands(),
    )
