""" A collection of command-line tools for building encoded update.xml
files.
"""

class InfoFile:

    update_file = ""
    version = None
    checksum = None

    # A multi-line HTML document describing the changes between
    # this version and the previous version
    description = ""

    @classmethod
    def from_info_file(filename):
        return


def files2xml(filenames):
    """ Given a list of filenames, extracts the app version and log
    information from accompanying files produces an output xml file.

    There are no constraints or restrictions on the names or extensions
    of the input files.  They just need to be accompanied by a sidecar
    file named similarly, but with a ".info" extension, that can be 
    loaded by the InfoFile class.
    """
    return



