
class VersionInfo:
    """ Represents the information about a particular version of an 
    application.
    """
    
    # The version string of this version
    version = ""

    # Customer-facing notes about this version.  Typically this is an
    # HTML document containing the changelog between this version and 
    # the previous version
    notes = ""

    # The location of where to obtain this version.  Typically this will
    # be an HTTP URL, but this can be a URI for a local or LAN item.
    location = ""

    # A function that takes a string (self.version) and returns something
    # that can be used to compare against the version-parsed version of
    # another VersionInfo object.
    version_parser = None

    #========================================================================
    # Constructors
    #========================================================================

    @classmethod
    def from_xml(cls, bytes):
        """ Returns a new VersionInfo instance from a multi-line string of
        XML data
        """
        raise NotImplementedError

    def __init__(self, **kwargs):
        # Do a strict Traits-like construction
        for attr in ("version", "notes", "location", "version_parser"):
            if attr in kwargs:
                setattr(self, attr, kwargs[attr])
        return

    #========================================================================
    # Public methods
    #========================================================================

    def to_xml(self):
        """ Returns a multi-line string of XML representing the information in
        this object.
        """

        raise NotImplementedError

    def __cmp__(self, other):
        """ Allows for comparing two VersionInfo objects so they can
        be presented in version-sorted order.  This is where we parse
        and interpretation of the **version** string attribute.
        """
        # TODO: Do something more intelligent here
        if self.version_parser is not None:
            self_ver = self.version_parser(self.version)
        else:
            self_ver = self.version
        if other.version_parser is not None:
            other_ver = other.version_parser(other.version)
        else:
            other_ver = other.version
        if self_ver < other_ver:
            return -1
        elif self.ver == other_ver:
            return 0
        else:
            return 1


class UpdateInfo:
    """ Encapsulates the information about the available update or
    updates.  An update can consist of multiple versions, with each
    version containing its own information and download URL.
    """

    # A list of VersionInfo objects
    updates = None

    #========================================================================
    # Constructors
    #========================================================================

    @classmethod
    def from_uri(cls, uri):
        """ Returns a new UpdateInfo, with a populated list of VersionInfo
        objects
        """
        raise NotImplementedError


    def __init__(self, updates=None):
        if updates:
            self.updates = updates
        return

