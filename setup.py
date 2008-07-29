#!/usr/bin/env python
#
# Copyright (c) 2008 by Enthought, Inc.
# All rights reserved.
#

"""
Explicitly typed Python attributes package.

The Traits package is at the center of all ETS development and has changed the
mental model we use for programming in the already extremely efficient Python
programming language. We encourage everyone to join us in enjoying the
productivity gains from using such a powerful approach.

A trait is a type definition that can be used for normal Python object
attributes, giving the attributes some additional characteristics:

    * Initialization: A trait has a default value, which is automatically set
      as the initial value of an attribute before its first use in a program.
    * Validation: A trait attribute's type is explicitly declared . The type is
      evident in the code, and only values that meet a programmer-specified set
      of criteria (i.e., the trait definition) can be assigned to that
      attribute. Note that the default value need not meet the criteria defined
      for assignment of values.
    * Delegation: The value of a trait attribute can be contained either in the
      defining object or in another object delegated to by the trait.
    * Notification: Setting the value of a trait attribute can notify other
      parts of the program that the value has changed.
    * Visualization: User interfaces that allow a user to interactively modify
      the value of a trait attribute can be automatically constructed using the
      trait's definition.

A class can freely mix trait-based attributes with normal Python attributes,
or can opt to allow the use of only a fixed or open set of trait attributes
within the class. Trait attributes defined by a classs are automatically
inherited by any subclass derived from the class.
"""


import os, zipfile
from setuptools import setup, Extension, find_packages
from setuptools.command.develop import develop
from distutils.command.build import build as distbuild
from distutils import log
from pkg_resources import DistributionNotFound, parse_version, require, VersionConflict

from setup_data import INFO
from make_docs import HtmlBuild


ctraits = Extension(
    'enthought.traits.ctraits',
    sources = ['enthought/traits/ctraits.c'],
    extra_compile_args = ['-DNDEBUG=1', '-O3'],
    )
speedups = Extension(
    'enthought.traits.protocols._speedups',
    # fixme: Use the generated sources until Pyrex 0.9.6 and setuptools can play
    # with each other. See #1364
    sources = ['enthought/traits/protocols/_speedups.c'],
    extra_compile_args = ['-DNDEBUG=1', '-O3'],
    )


# Pull the description values for the setup keywords from our file docstring.
DOCLINES = __doc__.split("\n")


# Function to convert simple ETS project names and versions to a requirements
# spec that works for both development builds and stable builds.  Allows
# a caller to specify a max version, which is intended to work along with
# Enthought's standard versioning scheme -- see the following write up:
#    https://svn.enthought.com/enthought/wiki/EnthoughtVersionNumbers
def etsdep(p, min, max=None, literal=False):
    require = '%s >=%s.dev' % (p, min)
    if max is not None:
        if literal is False:
            require = '%s, <%s.a' % (require, max)
        else:
            require = '%s, <%s' % (require, max)
    return require


# Declare our ETS project dependencies:
ENTHOUGHTBASE = etsdep('EnthoughtBase', '3.0.0b1')
TRAITSBACKENDWX = etsdep('TraitsBackendWX', '3.0.0b1')
TRAITSBACKENDQT = etsdep('TraitsBackendQt', '3.0.0b1')
TRAITSGUI = etsdep('TraitsGUI', '3.0.0b1')

# Notes:
# - enthought\traits\ui\handler.py and
#   enthought\traits\ui\dockable_view_element.py depend upon files in
#   TraitsGUI[dock]. But the dependencies are all due to calls made to those
#   modules from TraitsGUI[dock] or by features used by TraitsBackendWX. Since
#   TraitsBackendWX depends upon TraitsGUI[dock], and TraitsGUI[dock] depends
#   upon Traits, we opt to omit the TraitsGUI[dock] dependency, since in
#   practice it should not cause any  problems. Leaving the dependency in
#   pulls the TraitsBackendWX egg in, even if it is not needed.


# Methods to allow us to dynamically build html docs from RST sources.
def generate_docs():
    """ If sphinx is installed, generate docs.
    """
    doc_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'docs')
    source_dir = os.path.join(doc_dir, 'source')
    html_zip = os.path.join(doc_dir,  'html.zip')
    dest_dir = doc_dir

    required_sphinx_version = "0.4.1"
    sphinx_installed = False
    try:
        require("Sphinx>=%s" % required_sphinx_version)
        sphinx_installed = True
    except (DistributionNotFound, VersionConflict):
        log.warn('Sphinx install of version %s could not be verified.'
                    ' Trying simple import...' % required_sphinx_version)
        try:
            import sphinx
            if parse_version(sphinx.__version__) < parse_version(required_sphinx_version):
                log.error("Sphinx version must be >=%s." % required_sphinx_version)
            else:
                sphinx_installed = True
        except ImportError:
            log.error("Sphnix install not found.")

    if sphinx_installed:
        log.info("Generating %s documentation..." % INFO['name'])
        docsrc = source_dir
        target = dest_dir

        try:
            build = HtmlBuild()
            build.start({
                'commit_message': None,
                'doc_source': docsrc,
                'preserve_temp': True,
                'subversion': False,
                'target': target,
                'verbose': True,
                'versioned': False
                }, [])
            del build

        except:
            log.error("The documentation generation failed.  Falling back to "
                      "the zip file.")

            # Unzip the docs into the 'html' folder.
            unzip_html_docs(html_zip, doc_dir)
    else:
        # Unzip the docs into the 'html' folder.
        log.info("Installing %s documentaion from zip file.\n" % INFO['name'])
        unzip_html_docs(html_zip, doc_dir)

def unzip_html_docs(src_path, dest_dir):
    """ Given a path to a zipfile, extract its contents to a given 'dest_dir'.
    """
    file = zipfile.ZipFile(src_path)
    for name in file.namelist():
        cur_name = os.path.join(dest_dir, name)
        if not name.endswith('/'):
            out = open(cur_name, 'wb')
            out.write(file.read(name))
            out.flush()
            out.close()
        else:
            if not os.path.exists(cur_name):
                os.mkdir(cur_name)
    file.close()

class my_develop(develop):
    def run(self):
        develop.run(self)
        generate_docs()

class my_build(distbuild):
    def run(self):
        distbuild.run(self)
        generate_docs()


# Call the setup function.
setup(
    author = 'David C. Morrill, et. al.',
    author_email = 'dmorrill@enthought.com',
    classifiers = """\
        Development Status :: 4 - Production/Stable
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
        Topic :: Scientific/Engineering
        Topic :: Software Development
        Topic :: Software Development :: Libraries
        """.splitlines(),
    cmdclass = {
        'develop': my_develop,
        'build': my_build
        },
    dependency_links = [
        'http://code.enthought.com/enstaller/eggs/source',
        ],
    description = DOCLINES[0],
    extras_require = {

        # Extra denoting that the standard ETS configuration package should be
        # used. If omitted, Traits will use its own package local configuration,
        # which is a subset of ETS Config containing just the parts used by
        # Traits.  Completely optional, not triggered by any imports.
        'etsconfig': [
            ENTHOUGHTBASE,
            ],

        # Extra denoting that the Traits UI backend for Qt 4.0 should be
        # installed.  Completely optional, not triggered by any imports
        'qt4': [
            TRAITSBACKENDQT,
            ],

        # The Traits UI package is always installed as part of the Traits core
        # egg. This is an extra denoting that the Traits UI should be functional
        # after installation (meaning that all Traits UI modules should load
        # without getting any import errors). Any actual UI's created will only
        # work with the default 'null' backend. You must also install one of
        # the 'real' backends (i.e. 'qt4' or 'wx') if you actually want to
        # create real user interfaces.
        'ui': [
            TRAITSGUI,
            ],

        # Extra denoting that the Traits UI backend for wxPython should be
        # installed.  Completely optional, not triggered by any imports.
        'wx': [
            TRAITSBACKENDWX,
            ],

        # All non-ETS dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            'numpy >= 1.0.0',
            ],
        },
    ext_modules = [ctraits, speedups],
    include_package_data = True,
    install_requires = [
        ],
    license = 'BSD',
    long_description = '\n'.join(DOCLINES[2:]),
    maintainer = 'ETS Developers',
    maintainer_email = 'enthought-dev@enthought.com',
    name = 'Traits',
    namespace_packages = [
        'enthought',
        'enthought.traits',
        'enthought.traits.ui',
        ],
    packages = find_packages(exclude = [
        'docs',
        'docs.*',
        'integrationtests',
        'integrationtests.*',
        ]),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    tests_require = [
        'nose >= 0.10.3',
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/traits',
    version = INFO['version'],
    zip_safe = False,
    )

