#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
# 
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#  Thanks for using Enthought open source!
# 
#  Author: David C. Morrill
#  Date:   11/03/2007
#
#------------------------------------------------------------------------------

""" Defines the Image object used to manage Traits UI image libraries.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os \
    import environ, listdir, remove
    
from os.path \
    import join, isdir, isfile, join, splitext, abspath, basename, exists
    
from platform \
    import system
    
from zipfile \
    import is_zipfile, ZipFile, ZIP_DEFLATED
    
from enthought.traits.api \
    import HasPrivateTraits, Property, Str, Int, List, Dict, File, Instance, \
           Bool, Tuple, TraitError, cached_property
           
from enthought.traits.trait_base \
    import get_resource_path
    
from ui_traits \
    import HasMargins, Margins, Alignment
    
from theme \
    import Theme

from enthought.pyface.api \
    import ImageResource
    
from enthought.pyface.resource_manager \
    import resource_manager
    
from enthought.resource.resource_reference \
    import ImageReference, ResourceReference
    
from toolkit \
    import toolkit
    
#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Standard image file extensions:
ImageFileExts = ( '.png', '.gif', '.jpg', 'jpeg' )
    
#-------------------------------------------------------------------------------
#  'ImageLibrary' class:
#-------------------------------------------------------------------------------

class ImageLibrary ( HasPrivateTraits ):
    """ Manages Traits UI image libraries.
    """
    
    # The list of available image volumes:
    volumes = Property
    
    # The volume dictionary (the keys are volume names, and the values are the
    # corresponding ImageVolume objects):
    catalog = Property
    
    #-- Private Traits ---------------------------------------------------------
    
    # Mapping from a 'virtual' library name to a 'real' library name:
    aliases = Dict

    #-- Public methods ---------------------------------------------------------
    
    def image_resource ( self, image_name ):
        """ Returns an ImageResource object for the specified image name.
        """
        # If no volume was specified, use the standard volume:
        if image_name.find( ':' ) < 0:
            image_name = '@images:%s' % image_name[1:]
            
        # Find the correct volume, possible resolving any aliases used:
        volume = self.find_volume( image_name )
        
        # Find the image within the volume and return its ImageResource object:
        if volume is not None:
            return volume.image_resource( image_name )
        
        # Otherwise, the volume was not found:
        return None
        
    def find_volume ( self, image_name ):
        """ Returns the ImageVolume object corresponding to the specified
            **image_name** or None if the volume cannot be found.
        """
        # Extract the volume name from the image name:
        volume_name, file_name = split_image_name( image_name )
        
        # Find the correct volume, possibly resolving any aliases used:
        catalog = self.catalog
        aliases = self.aliases
        while volume_name not in catalog:
            volume_name = aliases.get( volume_name )
            if volume_name is None:
                return None
                
        return catalog[ volume_name ] 
    
    def add_volume ( self, file_name = None ):
        """ If **file_name** is a file, it adds an image volume specified by
            **file_name** to the image library. If **file_name** is a 
            directory, it adds all image libraries contained in the directory 
            to the image library. If **file_name** is omitted, all image 
            libraries located in the *images* directory contained in the same 
            directory as the caller are added.
        """
        # If no file name was specfied, derive a path from the caller's
        # source code location:
        if file_name is None:
            file_name = join( get_resource_path( 2 ), 'images' )
            
        if isfile( file_name ):
            # Load an image volume from the specified file:
            volume = self._add_volume( file_name )
            if volume is None:
                raise TraitError( "'%s' is not a valid image volume." % 
                                  file_name )
                                  
            if volume.name in self.catalog:
                self._duplicate_volume( volume.name )
                
            self.catalog[ volume.name ] = volume
            self.volumes.append( volume )
            
        elif isdir( file_name ):
            # Load all image volumes from the specified path:
            catalog = self.catalog
            volumes = self._add_path( file_name )
            for volume in volumes:
                if volume.name in catalog:
                    self._duplicate_volume( volume.name )
                    
                catalog[ volume.name ] = volume
                
            self.volumes.extend( volumes )
        else:
            # Handle an unrecognized argument:
            raise TraitError( "The add method argument must be None or a file "
                      "or directory path, but '%s' was specified." % file_name )
                      
    def add_path ( self, volume_name, path = None ):
        """ Adds the directory specified by **path** as a *virtual* volume
            called **volume_name**. All image files contained within path 
            define the contents of the volume. If **path** is None, the 
            *images* contained in the 'images' subdirectory of the same 
            directory as the caller are is used as the path for the *virtual* 
            volume..
        """
        # Make sure we don't already have a volume with that name:
        if volume_name in self.catalog:
            raise TraitError( ("The volume name '%s' is already in the image "
                               "library.") % volume_name )
                               
        # If no path specified, derive one from the caller's source code
        # location:
        if path is None:
            path = join( get_resource_path( 2 ), 'images' )
            
        # Make sure that the specified path is a directory:
        if not isdir( path ):
            raise TraitError( "The image volume path '%s' does not exist." %
                              path )
                              
        # Create the ImageVolume to describe the path's contents:
        volume = ImageVolume( name        = volume_name,
                              path        = path,
                              is_zip_file = False )
                    
        # Add the new volume to the library:
        self.catalog[ volume_name ] = volume
        self.volumes.append( volume )
        
    def extract ( self, file_name, image_names ):
        """ Builds a new image volume called **file_name** from the list of
            image names specified by **image_names**. Each image name should be
            of the form: '@volume:name'.
        """
        # Get the volume name and file extension:
        volume_name, ext = splitext( basename( file_name ) )
        
        # If no extension specified, add the '.zip' file extension:
        if ext == '':
            file_name += '.zip'
            
        # Create the ImageVolume object to describe the new volume:
        volume = ImageVolume( name = volume_name )
            
        # Make sure the zip file does not already exists:
        if exists( file_name ):
            raise TraitError( "The '%s' file already exists." % file_name )
        
        # Create the zip file:
        zf = ZipFile( file_name, 'w', ZIP_DEFLATED )
        
        # Add each of the specified images to it and the ImageVolume:
        error    = True
        aliases  = set()
        keywords = set()
        images   = []
        info     = {}
        try:
            for image_name in set( image_names ):
                # Verify the image name is legal:
                if (image_name[:1] != '@') or (image_name.find( ':' ) < 0):
                    raise TraitError( ("The image name specified by '%s' is "
                                "not of the form: @volume:name.") % image_name )
                    
                # Get the reference volume and image file names:
                image_volume_name, image_file_name = \
                    split_image_name( image_name )
                                       
                # Get the volume for the image name:
                image_volume = self.find_volume( image_name )
                if image_volume is None:
                    raise TraitError( ("Could not find the image volume "
                                       "specified by '%s'.") % image_name )
                                       
                # Get the image info:
                image_info = image_volume.catalog.get( image_name )
                if image_info is None:
                    raise TraitError( ("Could not find the image specified by "
                                       "'%s'.") % image_name )
                                     
                # Add the image info to the list of images:
                images.append( image_info )
                
                # Add the image file to the zip file:
                zf.writestr( image_file_name, 
                             image_volume.image_data( image_name ) )
                
                # Add the volume alias needed by the image (if any):
                if image_volume_name != volume_name:
                    if image_volume_name not in aliases:
                        aliases.add( image_volume_name )
                        
                        # Add the volume keywords as well:
                        for keyword in image_volume.keywords:
                            keywords.add( keyword )
                    
                # Add the volume info for the image:
                volume_info = image_volume.volume_info( image_name )
                vinfo       = info.get( image_volume_name )
                if vinfo is None:
                    info[ image_volume_name ] = vinfo = volume_info.clone()
                    
                vinfo.image_names.append( image_name )
                
            # Create the list of images for the volume:
            images.sort( key = lambda item: item.image_name )
            volume.images = images
            
            # Create the list of aliases for the volume:
            volume.aliases = list( aliases )
            
            # Create the list of keywords for the volume:
            volume.keywords = list( keywords )
                                             
            # Create the final volume info list for the volume:
            volume.info = info.values()
            
            # Write the volume manifest source code to the zip file:
            zf.writestr( 'image_volume.py', volume.image_volume_code )
            
            # Write the image info source code to the zip file:
            zf.writestr( 'image_info.py', volume.images_code )
            
            # Write a separate licenses file for human consumption:
            zf.writestr( 'license.txt', volume.license_text ) 
            
            # Indicate no errors occurred:
            error = False
        finally:
            zf.close()
            if error:
                remove( file_name )
        
    #-- Property Implementations -----------------------------------------------
    
    @cached_property
    def _get_volumes ( self ):
        # Get all volumes in the standard Traits UI image library directory:
        result = self._add_path( join( get_resource_path( 1 ), 'library' ) )
        
        # Check to see if there is an environment variable specifying a list
        # of paths containing image libraries:
        paths  = environ.get( 'TRAITS_IMAGES' )
        if paths is not None:
            # Determine the correct OS path separator to use:
            separator = ';'
            if system() != 'Windows':
                separator = ':'
                
            # Add all image volumes found in each path in the environment
            # variable:
            for path in paths.split( separator ):
                result.extend( self._add_path( path ) )
                
        # Return the list of default volumes found:
        return result

    @cached_property
    def _get_catalog ( self ):
        return dict( [ ( volume.name, volume ) for volume in self.volumes ] )
        
    #-- Private Methods --------------------------------------------------------
    
    def _add_path ( self, path ):
        """ Returns a list of ImageVolume objects, one for each image library
            located in the specified **path**.
        """
        result = []
        
        # Make sure the path is a directory:
        if isdir( path ):
            
            # Find each zip file in the directory:
            for base in listdir( path ):
                if splitext( base )[1] == '.zip':
                    
                    # Try to create a volume from the zip file and add it to
                    # the result:
                    volume = self._add_volume( join( path, base ) )
                    if volume is not None:
                        result.append( volume )
                        
        # Return the list of volumes found:
        return result
            
    def _add_volume ( self, path ):
        """ Returns an ImageVolume object for the image library specified by
            **path**. If **path** does not specify a valid ImageVolume, None is
            returned.
        """
        # Make sure the path is a valid zip file:
        if is_zipfile( path ):
            
            # Open the zip file for reading:
            zf = ZipFile( path, 'r' )
            try:
                # Extract the volume name from the path:
                volume_name = splitext( basename( path ) )[0]
                
                # Get the names of all top-level entries in the zip file:
                names = zf.namelist()
                
                # Check to see if there is a manifest file:
                if 'image_volume.py' in names: 
                    # Load the manifest code and extract the volume object:
                    temp = {}
                    exec zf.read( 'image_volume.py' ) in globals(), temp
                    volume = temp.get( 'volume' )
                        
                    # Try to add all of the external volume references as
                    # aliases for this volume:
                    aliases = self.aliases
                    for vname in volume.aliases:
                        if ((vname in aliases) and
                            (volume_name != aliases[ vname ])):
                            raise TraitError( ("Image library error: "
                                "Attempt to alias '%s' to '%s' when it is "
                                "already aliased to '%s'") %
                                ( vname, volume_name, aliases[ name ] ) )
                        aliases[ vname ] = volume_name
                        
                    # Set the volume name:
                    volume.name = volume_name
                    
                    # Set the path to this volume:
                    volume.path = abspath( path )
                    
                    # Return the new volume:
                    return volume
                
                # Create a new volume from it:
                return ImageVolume( name = volume_name, path = abspath( path ) )
                
            finally:
                # Guarantee that the zip file is closed:
                zf.close()
            
        # Indicate no volume was found:
        return None

    def _duplicate_volume ( self, volume_name ):
        """ Raises a duplicate volume name error.
        """
        raise TraitError( ("Attempted to add an image volume called '%s' when "
                  "a volume with that name is already defined.") % volume_name )
        
# Create the singleton image object:        
ImageLibrary = ImageLibrary()        
        
#-------------------------------------------------------------------------------
#  'ImageInfo' class:
#-------------------------------------------------------------------------------

class ImageInfo ( HasPrivateTraits ):
    """ Defines a class that contains information about a specific Traits UI 
        image.
    """
    
    # The user friendly name of the image:
    name = Str
    
    # The full image name (e.g. '@standard:floppy'):
    image_name = Str
    
    # A description of the image:
    description = Str
    
    # The category that the image belongs to:
    category = Str( 'General' )
    
    # A list of keywords used to describe/categorize the image:
    keywords = List( Str )
    
    # The image width (in pixels):
    width = Int
    
    # The image height (in pixels):
    height = Int
    
    # The theme for this image:
    theme = Instance( Theme )
    
    # The margins to use around the content:
    margins = HasMargins( Margins( 4, 2 ) )
    
    # The offset to use to properly position content: 
    offset = Tuple( Int, Int )
    
    # The alignment to use for positioning content:
    alignment = Alignment
    
    # The copyright that applies to this image:
    copyright = Property
    
    # The license that applies to this image:
    license = Property
    
    # A read-only string containing the Python code needed to construct this
    # ImageInfo object:
    image_info_code = Property
    
    #-- Default Value Implementations ------------------------------------------
        
    def _name_default ( self ):
        return split_image_name( self.image_name )[1]
        
    def _width_default ( self ):
        image = ImageLibrary.image_resource( self.image_name )
        if image is None:
            self.height = 0
            
            return 0
            
        width, self.height = toolkit().image_size( image.create_image() )
        
        return width
        
    def _height_default ( self ):
        image = ImageLibrary.image_resource( self.image_name )
        if image is None:
            self.width = 0
            
            return 0
            
        self.width, height = toolkit().image_size( image.create_image() )
        
        return height
    
    def _theme_default ( self ):
        return Theme( self.image_name,
                      margins   = self.margins,
                      offset    = self.offset,
                      alignment = self.alignment )
    
    #-- Property Implementations -----------------------------------------------
        
    @cached_property
    def _get_image_info_code ( self ):
        data = dict( [ ( name, repr( value ) ) 
                       for name, value in self.get( 'name', 'image_name',
                       'description', 'category', 'keywords' ).iteritems() ] )
        data.update( dict( [ ( name, repr( value ) )
                       for name, value in self.theme.get( 'offset',
                                                 'alignment' ).iteritems() ] ) )
        data.update( self.get( 'width', 'height' ) )
        data.update( self.theme.margins.get() )
        
        return (ImageInfoTemplate % data)
        
    def _get_copyright ( self ):
        return self._volume_info( 'copyright' )
        
    def _get_license ( self ):
        return self._volume_info( 'license' )
        
    #-- Private Methods --------------------------------------------------------
    
    def _volume_info ( self, name ):
        """ Returns the VolumeInfo object that applies to this image.
        """
        volume = ImageLibrary.find_volume( self.image_name )
        if volume is not None:
            info = volume.volume_info( self.image_name )
            if info is not None:
                return getattr( info, name, 'Unknown' ) 
            
        return 'Unknown'
        
#-------------------------------------------------------------------------------
#  'ImageVolumeInfo' class:  
#-------------------------------------------------------------------------------
                
class ImageVolumeInfo ( HasPrivateTraits ):
    
    # A general description of the images:
    description = Str( 'No volume description specified.' )
    
    # The copyright that applies to the images:
    copyright = Str( 'No copyright information specified.' )
    
    # The license that applies to the images:
    license = Str( 'No license information specified.' )
    
    # The list of image names within the volume the information applies to.
    # Note that an empty list means that the information applies to all images
    # in the volume:
    image_names = List( Str )
    
    # A read-only string containing the Python code needed to construct this
    # ImageVolumeInfo object:
    image_volume_info_code = Property
    
    # A read-only string containing the text describing the volume info:
    image_volume_info_text = Property
    
    #-- Property Implementations -----------------------------------------------
        
    @cached_property
    def _get_image_volume_info_code ( self ):
        data = dict( [ ( name, repr( value ) ) 
                       for name, value in self.get( 'description', 'copyright',
                                     'license', 'image_names' ).iteritems() ] )
                             
        return (ImageVolumeInfoCodeTemplate % data)
        
    @cached_property
    def _get_image_volume_info_text ( self ):
        description = self.description.replace( '\n', '\n    ' )
        license     = self.license.replace(     '\n', '\n    ' ).strip()
        image_names = self.image_names
        image_names.sort()
        if len( image_names ) == 0:
            image_names = [ 'All' ]
        images = '\n'.join( [ '  - ' + image_name 
                              for image_name in image_names ] )
                             
        return (ImageVolumeInfoTextTemplate % ( description, self.copyright,
                                                license, images ))
        
    #-- Public Methods ---------------------------------------------------------
    
    def clone ( self ):
        """ Returns a copy of the ImageVolumeInfo object.
        """
        return self.__class__( **self.get( 'description', 'copyright', 
                                           'license' ) )
        
#-------------------------------------------------------------------------------
#  'ImageVolume' class:
#-------------------------------------------------------------------------------

class ImageVolume ( HasPrivateTraits ):

    # The canonical name of this volume:
    name = Str
    
    # The list of volume descriptors that apply to this volume:
    info = List( ImageVolumeInfo )
    
    # The category that the volume belongs to:
    category = Str( 'General' )
    
    # A list of keywords used to describe the volume:
    keywords = List( Str )
    
    # The list of aliases for this volume:
    aliases = List( Str )
    
    # The path of the file that defined this volume:
    path = File
    
    # Is the path a zip file?
    is_zip_file = Bool( True )
    
    # The list of images available in the volume:
    images = List( ImageInfo )
    
    # A dictionary mapping image names to ImageInfo objects:
    catalog = Property
    
    # A read-only string containing the Python code needed to construct this
    # ImageVolume object:
    image_volume_code = Property
    
    # A read-only string containing the Python code needed to construct the
    # 'images' list for this ImageVolume object:
    images_code = Property
    
    # A read-only string containing the text describing the contents of the
    # volume (description, copyright, license information, and the images they
    # apply to):
    license_text = Property
    
    #-- Public Methods ---------------------------------------------------------
    
    def image_resource ( self, image_name ):
        """ Returns the ImageResource object for the specified **image_name**.
        """
        # Get the name of the image file:
        volume_name, file_name = split_image_name( image_name )
            
        if self.is_zip_file:
            # If the volume is from a zip file, create a zip file reference:
            ref = ZipFileReference( 
                      resource_factory = resource_manager.resource_factory,
                      path             = self.path,
                      name             = file_name )
        else:
            # Otherwise, create a normal file reference:
            ref = ImageReference( resource_manager.resource_factory,
                                  filename = join( self.path, file_name ) )
                                  
        # Create the ImageResource object using the reference (note that the
        # ImageResource class will not allow us to specify the reference in the
        # constructor):
        resource = ImageResource( file_name )
        resource._ref = ref
        
        # Return the ImageResource:
        return resource
        
    def image_data ( self, image_name ):
        """ Returns the image data (i.e. file contents) for the specified image
            name.
        """
        volume_name, file_name = split_image_name( image_name )
        
        if self.is_zip_file:
            zf = ZipFile( self.path, 'r' )
            try:
                return zf.read( file_name )
            finally:
                zf.close()
        else:
            fh = file( join( self.path, file_name ), 'rb' )
            try:
                return fh.read()
            finally:
                fh.close()
        
    def volume_info ( self, image_name ):
        """ Returns the ImageVolumeInfo object that corresponds to the 
            image specified by **image_name**.
        """
        for info in self.info:
            if ((len( info.image_names ) == 0) or 
                (image_name in info.image_names)):
                return info
    
        # Should never occur:
        return None
    
    #-- Default Value Implementations ------------------------------------------
    
    def _info_default ( self ):
        return [ ImageVolumeInfo() ]
    
    def _images_default ( self ):
        volume_name = self.name
        
        if self.is_zip_file:
            zf = ZipFile( self.path, 'r' )
            try:
                # Get the names of all top-level entries in the zip file:
                names = zf.namelist()
                
                # Check to see if there is a image info manifest file:
                if 'image_info.py' in names: 
                    # Load the manifest code and extract the images list:
                    temp = {}
                    exec zf.read( 'image_info.py' ) in globals(), temp
                    images = temp[ 'images' ]
                else:    
                    # Create an ImageInfo object for all image files contained
                    # in the .zip file:
                    images = []
                    for name in names:
                        root, ext = splitext( name )
                        if ext in ImageFileExts:
                            images.append( ImageInfo(
                               name       = root,
                               image_name = join_image_name(volume_name, name) )
                            )
            finally:
                # Guarantee that the zip file is closed:
                zf.close()
        else:
            # Create an ImageInfo object for each image file containined in the
            # path:
            images = []
            for name in listdir( self.path ):
                root, ext = splitext( name )
                if ext in ImageFileExts:
                    images.append( ImageInfo( 
                        name       = root, 
                        image_name = join_image_name( volume_name, name ) ) )
                        
        # Return the resulting sorted list as the default value:
        images.sort( key = lambda item: item.image_name )
        
        return images
        
    #-- Property Implementations -----------------------------------------------
    
    @cached_property
    def _get_catalog ( self ):
        return dict( [ ( image.image_name, image ) for image in self.images ] )
        
    @cached_property
    def _get_image_volume_code ( self ):
        data = dict( [ ( name, repr( value ) ) 
                       for name, value in self.get( 'description', 'category',
                           'keywords', 'aliases', 'licenses' ).iteritems() ] )
        data['info'] = ',\n'.join( [ info.image_volume_info_code
                                     for info in self.info ] )
                           
        return (ImageVolumeTemplate % data)
        
    @cached_property
    def _get_images_code ( self ):
        images = ',\n'.join( [ info.image_info_code for info in self.images ] )
        
        return (ImageVolumeImagesTemplate % images)
        
    @cached_property
    def _get_license_text ( self ):
        return (('\n\n%s\n' % ('-' * 79)).join( [ info.image_volume_info_text
                                                  for info in self.info ] ))
        
#-------------------------------------------------------------------------------
#  'ZipFileReference' class:  
#-------------------------------------------------------------------------------
                
class ZipFileReference ( ResourceReference ):
    
    # The path name of the zip file:
    path = File
    
    # The file within the zip file:
    name = Str
    
    #-- ResourceReference Interface Implementation -----------------------------

    def load ( self ):
        """ Loads the resource. 
        """
        zf = ZipFile( self.path, 'r' )
        try:
            data = zf.read( self.name )
        finally:
            zf.close()
            
        return self.resource_factory.image_from_data( data )
        
#-- Utility functions ----------------------------------------------------------

def split_image_name ( image_name ):
    """ Splits a specified **image_name** into its constituent volume and file
        names and returns a tuple of the form: ( volume_name, file_name ).
    """
    col         = image_name.find( ':' )
    volume_name = image_name[ 1: col ]
    file_name   = image_name[ col + 1: ]
    if file_name.find( '.' ) < 0:
        file_name += '.png'
    
    return ( volume_name, file_name )
    
def join_image_name ( volume_name, file_name ):
    """ Joins a specified **volume_name** and **file_name** into an image name,
        and return the resulting image name.    
    """
    root, ext = splitext( file_name )
    if (ext == '.png') and (root.find( '.' ) < 0):
        file_name = root
        
    return '@%s:%s' % ( volume_name, file_name )
    
#-- Code Generation Templates --------------------------------------------------

# Template for creating an ImageVolumeInfo object:
ImageVolumeInfoCodeTemplate = \
"""        ImageVolumeInfo(
            description = %(description)s,
            copyright   = %(copyright)s,
            license     = %(license)s,
            image_names = %(image_names)s
        )"""

# Template for creating an ImageVolumeInfo license text:
ImageVolumeInfoTextTemplate = \
"""Description:
    %s

Copyright:
    %s

License:
    %s

Applicable Images:
%s"""    

# Template for creating an ImageVolume object:
ImageVolumeTemplate = \
"""from enthought.traits.ui.image import ImageVolume, ImageVolumeInfo
    
volume = ImageVolume(
    category    = %(category)s,
    keywords    = %(keywords)s,
    aliases     = %(aliases)s,
    info        = [
%(info)s
    ]
)"""    

# Template for creating an ImageVolume 'images' list:
ImageVolumeImagesTemplate = \
"""from enthought.traits.ui.image     import ImageInfo
from enthought.traits.ui.ui_traits import Margins 
    
images = [
%s
]"""    

# Template for creating an ImageInfo object:
ImageInfoTemplate = \
"""    ImageInfo(
        name        = %(name)s,
        image_name  = %(image_name)s,
        description = %(description)s,
        category    = %(category)s,
        keywords    = %(keywords)s,
        width       = %(width)d,
        height      = %(height)d,
        margins     = Margins( %(left)d, %(right)d, %(top)d, %(bottom)d ),
        offset      = %(offset)s,
        alignment   = %(alignment)s
    )"""
            
