import os, zipfile
from setuptools import setup, Extension, find_packages
from setuptools.command.develop import develop
from distutils.command.build import build as distbuild
from distutils import log
from pkg_resources import require, DistributionNotFound

from setup_data import INFO
from make_docs import HtmlBuild

ctraits = Extension(
    'enthought.traits.ctraits',
    sources = [ 'enthought/traits/ctraits.c' ],
    extra_compile_args = [ '-DNDEBUG=1', '-O3' ],
)

speedups = Extension(
    'enthought.traits.protocols._speedups',
    # fixme: Use the generated sources until Pyrex 0.9.6 and setuptools can play
    # with each other. See #1364
    sources = [ 'enthought/traits/protocols/_speedups.c' ],
    extra_compile_args = [ '-DNDEBUG=1', '-O3' ],
)


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
ENTHOUGHTBASE   = etsdep( 'EnthoughtBase',   '3.0.0b1' )
TRAITSBACKENDWX = etsdep( 'TraitsBackendWX', '3.0.0b1' )
TRAITSBACKENDQT = etsdep( 'TraitsBackendQt', '3.0.0b1' )
TRAITSGUI       = etsdep( 'TraitsGUI',       '3.0.0b1' )

# Notes:
# - enthought\traits\ui\handler.py and
#   enthought\traits\ui\dockable_view_element.py depend upon files in
#   TraitsGUI[dock]. But the dependencies are all due to calls made to those
#   modules from TraitsGUI[dock] or by features used by TraitsBackendWX. Since
#   TraitsBackendWX depends upon TraitsGUI[dock], and TraitsGUI[dock] depends
#   upon Traits, we opt to omit the TraitsGUI[dock] dependency, since in
#   practice it should not cause any  problems. Leaving the dependency in
#   pulls the TraitsBackendWX egg in, even if it is not needed.

def generate_docs():
    """If sphinx is installed, generate docs.
    """
    doc_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)),'docs',
                           'source')
    html_zip = os.path.join(os.path.abspath(os.path.dirname(__file__)),'docs',
                            'html.zip')
    dest_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            'docs')
    
    try:
        require("Sphinx>=0.4.1")
            
        log.info("Auto-generating documentation in %s/html" % dest_dir)
        doc_src = doc_dir
        target = dest_dir
        try:
            build = HtmlBuild()
            build.start({
                'commit_message': None,
                'doc_source': doc_src,
                'preserve_temp': True,
                'subversion': False,
                'target': target,
                'verbose': True,
                'versioned': False,
                }, [])
            del build
        except:
            log.error("The documentation generation failed."
                      " Installing from zip file.")
            
            # Unzip the docs into the 'html' folder.
            unzip_html_docs(html_zip, dest_dir)
            
    except DistributionNotFound:
        log.error("Sphinx is not installed, so the documentation could not be "
                  "generated.  Installing from zip file...")
        
        # Unzip the docs into the 'html' folder.
        unzip_html_docs(html_zip, dest_dir)

def unzip_html_docs(src_path, dest_dir):
    """Given a path to a zipfile, extract
    its contents to a given 'dest_dir'.
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
        # Generate the documentation.
        generate_docs()

class my_build(distbuild):
    def run(self):
        distbuild.run(self)
        # Generate the documentation.
        generate_docs()

setup(
    author       = 'David C. Morrill',
    author_email = 'dmorrill@enthought.com',
    cmdclass = {
        'develop': my_develop,
        'build': my_build
    },
    description  = 'Explicitly typed Python attributes package',

    extras_require = {

        # Extra denoting that the standard ETS configuration package should be
        # used. If omitted, Traits will use its own package local configuration,
        # which is a subset of ETS Config containing just the parts used by
        # Traits.

        # Completely optional, not triggered by imports:
        'etsconfig': [
            ENTHOUGHTBASE,
        ],

        # Extra denoting that the Traits UI backend for Qt 4.0 should be
        # installed.

        # Completely optional, not triggered by imports:
        'qt4': [
            TRAITSBACKENDQT,
        ],

        # The Traits UI package is always installed as part of the Traits core
        # egg. This is an extra denoting that the Traits UI should be functional
        # after installation (meaning that all Traits UI modules should load
        # without getting any import errors). Any actual UI's created will only
        # work with the default 'null' backend. You must also install one of
        # the 'real' backends (i.e. 'qt4' or 'wx') if you actually want to
        # create real user interfaces:
        'ui': [
            TRAITSGUI,
        ],

        # Extra denoting that the Traits UI backend for wxPython should be
        # installed.

        # Completely optional, not triggered by imports:
        'wx': [
            TRAITSBACKENDWX,
        ],

        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not:
        'nonets': [
            'numpy >= 1.0.0',
        ],
    },

    ext_modules          = [ ctraits, speedups ],
    include_package_data = True,
    install_requires = [
    ],
    license              = 'BSD',
    name                 = 'Traits',
    namespace_packages = [
        'enthought',
        'enthought.traits',
        'enthought.traits.ui',
    ],
    packages = find_packages( exclude = [
        'docs',
        'docs.*',
        'integrationtests',
        'integrationtests.*',
    ] ),
    tests_require = [
        'nose >= 0.10.3',
    ],
    test_suite = 'nose.collector',
    url        = 'http://code.enthought.com/traits',
    version    = INFO['version'],
    zip_safe   = False,
)

