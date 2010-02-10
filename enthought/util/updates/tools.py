""" A collection of command-line tools for building encoded update.xml
files.
"""

#Requires Python 2.6 (for format string notation)

import os
import re
import md5

_version_in_name = re.compile("(\S*)[-](\d+\.\d+\.*\d*)\S*")

def _get_name(filename):
    match = _version_in_name.search(filename)
    if match is None:
        raise ValueError, "Could not find name in filename: {0}".format(filename)
    return match.group(1)

def _get_version(filename):
    match = _version_in_name.search(filename)
    if match is None:
        raise ValueError, "Could not find version in filename: {0}".format(filename)
    return match.group(2)

def _get_checksum(filename):
    base, ext = os.path.splitext(filename)
    data = open(base).read()
    return md5.new(data).hexdigest()


name_re = re.compile('name:\s*(.*)\n')
version_re = re.compile('version:\s*(.*)\n')
checksum_re = re.compile('checksum:\s*(.*)\n')
html_re = re.compile('\nhtml:')

codedict = {'name':{'re':name_re,
                    'get':_get_name},
            'version': {'re':version_re,
                        'get':_get_version},
            'checksum': {'re':checksum_re,
                         'get':_get_checksum}
            }

class InfoFile(object):
    """Representation of an .info file

    Important methods: 
    
    @classmethod
    from_info_file(filename)

      construct an InfoFile object from a filename --- simple parser

      name: %filename% (if not present extracted from .info filename)
      version: %filename% (if not present it is extracted from name of file)
      checksum: md5hash (if not present it is computed from the basefile)
      html: (everything else in the file from the next line to the end)
    
    get_xml()
      return a list of xml elements for this file       
    """

    # The name of the update_file
    name = ""
    version = None
    checksum = None

    # A multi-line HTML document describing the changes between
    # this version and the previous version
    description = ""

    @classmethod
    def from_info_file(cls, filename):
        # TODO: Change this at some point to parse using elementtree
        str = open(filename).read()        
        obj = cls()
        for attr in ['name', 'version', 'checksum']:
            funcdict = codedict[attr]
            match = funcdict['re'].search(str)
            if match is None:
                value = funcdict['get'](filename)
            else:
                value = match.group(1)
            setattr(obj, attr, value)
            
        match = html_re.search(str)
        beg, end = match.span()
        start = str.find('\n', end)
        obj.description = str[start:]
        return obj

    def get_xml(self):
        xml_elements = []
        for attr in ['name', 'version', 'checksum', 'description']:
            value = getattr(self, attr)
            #str = "{spaces}<{attr}>{value}</{attr}>"
            #xml_elements.append(str.format(spaces=" "*4,attr=attr, value=value))
            str = "%(spaces)s<%(attr)s>%(value)s</%(attr)s>"
            xml_elements.append(str % dict(spaces=" "*4,attr=attr, value=value))
        return xml_elements

# TODO: Change this at some point to use elementtree or something to 
# generate real, validated XML.
_xmlheader = """<?xml version="1.0" encoding="ISO-8859-1"?>
<!-- DO NOT EDIT MANUALLY -->
<!-- Automatically generated file using enthought.util.updates -->
"""

def files2xml(filenames):
    """ Given a list of filenames, extracts the app version and log
    information from accompanying files produces an output xml string.

    There are no constraints or restrictions on the names or extensions
    of the input files.  They just need to be accompanied by a sidecar
    file named similarly, but with a ".info" extension, that can be 
    loaded by the InfoFile class.

    If there is no .info file for a filename or an error occurs while constructing it
    a warning message is printed. 
    """
    xmlparts = [_xmlheader]
    for file in filenames:
        #info_file_name = "{0}.info".format(file)
        info_file_name = "%s.info" % (file,)
        if not os.path.exists(info_file_name):
            #print "Warning: {0} was not found.".format(info_file_name)
            print "Warning: %s was not found." % (info_file_name,)
            continue
        try:
            info = InfoFile.from_info_file(info_file_name)
            xml_list = info.get_xml()
        except:
            #print "Warning: Failure in creating XML for {0}".format(info_file_name)
            print "Warning: Failure in creating XML for %s" % (info_file_name,)
            continue
        xmlparts.append('<update_file>') 
        xmlparts.extend(xml_list)
        xmlparts.append('</update_file>')

    return "\n".join(xmlparts)



