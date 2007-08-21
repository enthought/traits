from setuptools import setup, find_packages


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


# Declare our ETS project dependencies.
MODEL = etsdep('enthought.model', '2.0.0b1')
TRAITS = etsdep('enthought.traits', '3.0.0b1')


setup(
    author = 'Phil Thompson',
    author_email = 'phil@riverbankcomputing.co.uk',
    description = 'PyQt backend for enthought.traits',
    include_package_data = True,
    install_requires = [
        "enthought.model >=2.0.0b1, <3.0.0",
        "enthought.traits >=3.0.0b1, <4.0.0",
        ],
    license = 'GPL',
    name = 'enthought.traits.ui.qt4',
    namespace_packages = [
        "enthought",
        "enthought.traits",
        "enthought.traits.ui",
        ],
    packages = find_packages(),
    url = 'http://code.enthought.com/traits',
    version = '3.0.0b1',
    zip_safe = False,
    )

