#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
# 
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
# 
#  Author: David C. Morrill
#  Date:   11/03/2007
#
#------------------------------------------------------------------------------

""" Defines the ImageLibrary object used to manage Traits UI image libraries.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os \
    import environ, listdir, remove, stat, makedirs, rename
    
from os.path \
    import join, isdir, isfile, join, splitext, abspath, basename, exists
    
from stat \
    import ST_MTIME
    
from platform \
    import system
    
from zipfile \
    import is_zipfile, ZipFile, ZIP_DEFLATED
    
from time \
    import time, sleep, localtime, strftime   

from thread \
    import allocate_lock
    
from threading \
    import Thread
    
from enthought.traits.api \
    import HasPrivateTraits, Property, Str, Int, List, Dict, File, Instance, \
           Bool, Tuple, TraitError, Float, Any, cached_property, on_trait_change
           
from enthought.traits.trait_base \
    import get_resource_path, traits_home
    
from ui_traits \
    import HasMargin, HasBorder, Alignment
    
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

# The image_cache root directory:
image_cache_path = join( traits_home(), 'image_cache' )

# Names of files that should not be copied when ceating a new library copy:
dont_copy_list = ( 'image_volume.py', 'image_info.py', 'license.txt' )

#-------------------------------------------------------------------------------
#  Returns the contents of the specified file:
#-------------------------------------------------------------------------------

def read_file ( file_name ):
    """ Returns the contents of the specified *file_name*.
    """
    fh = file( file_name, 'rb' )
    try:
        return fh.read()
    finally:
        fh.close()

#-------------------------------------------------------------------------------
#  Writes the specified data to the specified file:
#-------------------------------------------------------------------------------

def write_file ( file_name, data ):
    """ Writes the specified data to the specified file.
    """
    fh = file( file_name, 'wb' )
    try:
        fh.write( data )
    finally:
        fh.close()

#-------------------------------------------------------------------------------
#  Returns the value of a Python symbol loaded from a specified source code
#  string:
#-------------------------------------------------------------------------------
                
def get_python_value ( source, name ):
    """ Returns the value of a Python symbol loaded from a specified source
        code string.
    """
    temp = {}
    exec source.replace( '\r', '' ) in globals(), temp
    return temp[ name ]
        
#-------------------------------------------------------------------------------
#  Returns a specified time as a text string:
#-------------------------------------------------------------------------------

def time_stamp_for ( time ):
    """ Returns a specified time as a text string.
    """
    return strftime( '%Y%m%d%H%M%S', localtime( time ) )
    
#-------------------------------------------------------------------------------
#  Adds all traits from a specified object to a dictionary with a specified name
#  prefix:
#-------------------------------------------------------------------------------
        
def add_object_prefix ( dict, object, prefix ):
    """ Adds all traits from a specified object to a dictionary with a specified 
        name prefix.
    """
    for name, value in object.get().iteritems():
        dict[ prefix + name ] = value
        
#-------------------------------------------------------------------------------
#  'FastZipFile' class:  
#-------------------------------------------------------------------------------
                
class FastZipFile ( HasPrivateTraits ):
    """ Provides fast access to zip files by keeping the underlying zip file
        open across multiple uses.
    """
    
    # The path to the zip file:
    path = File
    
    # The open zip file object (if None, the file is closed):
    zf = Property
    
    # The time stamp of when the zip file was most recently accessed:
    time_stamp = Float
    
    # The lock used to manage access to the 'zf' trait between the two threads:
    access = Any
    
    #-- Public Methods ---------------------------------------------------------
    
    def namelist ( self ):
        """ Returns the names of all files in the top-level zip file directory.
        """
        self.access.acquire()
        try:
            return self.zf.namelist()
        finally:
            self.access.release()
        
    def read ( self, file_name ):
        """ Returns the contents of the specified **file_name** from the zip 
            file.
        """
        self.access.acquire()
        try:
            return self.zf.read( file_name )
        finally:
            self.access.release()
            
    def close ( self ):
        """ Temporarily closes the zip file (usually while the zip file is being
            replaced by a different version).
        """
        self.access.acquire()
        try:
            if self._zf is not None:
                self._zf.close()
                self._zf = None
        finally:
            self.access.release()
            
    #-- Default Value Implementations ------------------------------------------
    
    def _access_default ( self ):
        return allocate_lock()
        
    #-- Property Implementations -----------------------------------------------
    
    def _get_zf ( self ):
        # Restart the time-out:
        self.time_stamp = time()
        
        if self._zf is None:
            self._zf = ZipFile( self.path, 'r' )
            if self._running is None:
                Thread( target = self._process ).start()
                self._running = True
            
        return self._zf
        
    #-- Private Methods --------------------------------------------------------
    
    def _process ( self ):
        """ Waits until the zip file has not been accessed for a while, then
            closes the file and exits.
        """
        while True:
            sleep( 1 )
            self.access.acquire()
            if time() > (self.time_stamp + 2.0):
                if self._zf is not None:
                    self._zf.close()
                    self._zf = None
                
                self._running = False
                self.access.release()
                break
                
            self.access.release()
        
#-------------------------------------------------------------------------------
#  'ImageInfo' class:
#-------------------------------------------------------------------------------

class ImageInfo ( HasPrivateTraits ):
    """ Defines a class that contains information about a specific Traits UI 
        image.
    """
    
    # The volume this image belongs to:
    volume = Instance( 'ImageVolume' )
    
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
    
    # The border inset:
    border = HasBorder
    
    # The margin to use around the content:
    content = HasMargin
    
    # The margin to use around the label:
    label = HasMargin
    
    # The alignment to use for the label:
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
        image = self.volume.image_resource( self.image_name )
        if image is None:
            self.height = 0
            
            return 0
            
        width, self.height = toolkit().image_size( image.create_image() )
        
        return width
        
    def _height_default ( self ):
        image = self.volume.image_resource( self.image_name )
        if image is None:
            self.width = 0
            
            return 0
            
        self.width, height = toolkit().image_size( image.create_image() )
        
        return height
    
    def _theme_default ( self ):
        return Theme( self.volume.image_resource( self.image_name ),
                      border    = self.border,
                      content   = self.content,
                      label     = self.label,
                      alignment = self.alignment )
    
    #-- Property Implementations -----------------------------------------------
        
    @cached_property
    def _get_image_info_code ( self ):
        data = dict( [ ( name, repr( value ) ) 
                       for name, value in self.get( 'name', 'image_name',
                       'description', 'category', 'keywords' ).iteritems() ] )
        data.update( self.get( 'width', 'height' ) )
        theme = self.theme
        data[ 'alignment' ] = repr( theme.alignment )
        add_object_prefix( data, theme.border,  'b' )
        add_object_prefix( data, theme.content, 'c' )
        add_object_prefix( data, theme.label,   'l' )
        
        return (ImageInfoTemplate % data)
        
    def _get_copyright ( self ):
        return self._volume_info( 'copyright' )
        
    def _get_license ( self ):
        return self._volume_info( 'license' )
        
    #-- Private Methods --------------------------------------------------------
    
    def _volume_info ( self, name ):
        """ Returns the VolumeInfo object that applies to this image.
        """
        info = self.volume.volume_info( self.image_name )
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
    
    # The FastZipFile object used to access the underlying zip file:
    zip_file = Instance( FastZipFile )
    
    # The list of images available in the volume:
    images = List( ImageInfo )
    
    # A dictionary mapping image names to ImageInfo objects:
    catalog = Property( depends_on = 'images' )
    
    # The time stamp of when the image library was last modified:
    time_stamp = Str
    
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
    
    def update ( self ):
        """ Updates the contents of the image volume from the underlying 
            image store, and saves the results.
        """
        # Unlink all our current images:
        for image in self.images:
            image.volume = None
                
        # Make sure the images are up to date by deleting any current value:
        del self.images
        
        # Save the new image volume information:
        self.save()
    
    def save ( self ):
        self.images
        """ Saves the contents of the image volume using the current contents 
            of the **ImageVolume**. 
        """
        path = self.path
            
        # Pre-compute the images code, because it can require a long time
        # to load all of the images so that we can determine their size, and we
        # don't want that time to interfere with the time stamp of the image
        # volume:
        images_code = self.images_code
        
        if not self.is_zip_file:
            # We need to time stamp when this volume info was generated, but
            # it needs to be the same or newer then the time stamp of the file
            # it is in. So we use the current time plus a 'fudge factor' to
            # allow for some slop in when the OS actually time stamps the file:
            self.time_stamp = time_stamp_for( time() + 5.0 )
            
            # Write the volume manifest source code to a file:
            write_file( join( path, 'image_volume.py' ), 
                        self.image_volume_code )
            
            # Write the image info source code to a file:
            write_file( join( path, 'image_info.py' ), images_code )
            
            # Write a separate license file for human consumption:
            write_file( join( path, 'license.txt' ), self.license_text )
            
        # Create a temporary name for the new .zip file:
        file_name = path + '.###'
        
        # Create the new zip file:
        new_zf = ZipFile( file_name, 'w', ZIP_DEFLATED )
        
        try:
            # Get the current zip file:
            cur_zf = self.zip_file
            
            # Copy all of the image files from the current zip file to the new
            # zip file:
            for name in cur_zf.namelist():
                if name not in dont_copy_list:
                    new_zf.writestr( name, cur_zf.read( name ) )
            
            # Temporarily close the current zip file while we replace it with 
            # the new version:
            cur_zf.close()
            
            # We need to time stamp when this volume info was generated, but
            # it needs to be the same or newer then the time stamp of the file
            # it is in. So we use the current time plus a 'fudge factor' to
            # allow for some slop in when the OS actually time stamps the file:
            self.time_stamp = time_stamp_for( time() + 10.0 )
            
            # Write the volume manifest source code to the zip file:
            new_zf.writestr( 'image_volume.py', self.image_volume_code )
            
            # Write the image info source code to the zip file:
            new_zf.writestr( 'image_info.py', images_code )
            
            # Write a separate license file for human consumption:
            new_zf.writestr( 'license.txt', self.license_text )
            
            # Done creating the new zip file:
            new_zf.close()
            new_zf = None
            
            # Rename the original file to a temporary name, so we can give the
            # new file the original name. Note that unlocking the original zip
            # file after the previous close sometimes seems to take a while,
            # which is why we repeatedly try the rename until it either succeeds
            # or takes so long that it must have failed for another reason:
            temp_name = path + '.$$$'
            for i in range( 50 ):
                try:
                    rename( path, temp_name )
                    break
                except:
                    sleep( 0.1 )
                
            try:
                rename( file_name, path )
                file_name = temp_name
            except:
                rename( temp_name, path )
                raise
            
            # Indicate no errors occurred:
            error = False
        finally:
            if new_zf is not None:
                new_zf.close()
                
            remove( file_name )
    
    def image_resource ( self, image_name ):
        """ Returns the ImageResource object for the specified **image_name**.
        """
        # Get the name of the image file:
        volume_name, file_name = split_image_name( image_name )
            
        if self.is_zip_file:
            # See if we already have the image file cached in the file system:
            cache_file = self._check_cache( file_name )
            if cache_file is None:
                # If not cached, then create a zip file reference:
                ref = ZipFileReference( 
                          resource_factory = resource_manager.resource_factory,
                          zip_file         = self.zip_file,
                          path             = self.path,
                          volume_name      = self.name,
                          file_name        = file_name )
            else:
                # Otherwise, create a cache file reference:
                ref = ImageReference( resource_manager.resource_factory,
                                      filename = cache_file )
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
            return self.zip_file.read( file_name )
        else:
            return read_file( join( self.path, file_name ) )
        
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
        return self._load_image_info()
        
    #-- Property Implementations -----------------------------------------------
    
    @cached_property
    def _get_catalog ( self ):
        return dict( [ ( image.image_name, image ) for image in self.images ] )
        
    def _get_image_volume_code ( self ):
        data = dict( [ ( name, repr( value ) ) 
                       for name, value in self.get( 'description', 'category',
                           'keywords', 'aliases', 'time_stamp', 'licenses'
                           ).iteritems() ] )
        data['info'] = ',\n'.join( [ info.image_volume_info_code
                                     for info in self.info ] )
                           
        return (ImageVolumeTemplate % data)
        
    def _get_images_code ( self ):
        images = ',\n'.join( [ info.image_info_code for info in self.images ] )
        
        return (ImageVolumeImagesTemplate % images)
        
    def _get_license_text ( self ):
        return (('\n\n%s\n' % ('-' * 79)).join( [ info.image_volume_info_text
                                                  for info in self.info ] ))
                                                  
    #-- Private Methods --------------------------------------------------------
    
    def _load_image_info ( self ):
        """ Returns the list of ImageInfo objects for the images in the volume.
        """
        time_stamp  = time_stamp_for( stat( self.path )[ ST_MTIME ] )
        volume_name = self.name
        old_images  = []
        cur_images  = []
        
        if self.is_zip_file:
            zf = self.zip_file
            
            # Get the names of all top-level entries in the zip file:
            names = zf.namelist()
            
            # Check to see if there is an image info manifest file:
            if 'image_info.py' in names:
                # Load the manifest code and extract the images list:
                old_images = get_python_value( zf.read( 'image_info.py' ), 
                                               'images' )

            # Check to see if our time stamp is up to data with the file:
            if self.time_stamp < time_stamp:
                
                # If not, create an ImageInfo object for all image files 
                # contained in the .zip file:
                for name in names:
                    root, ext = splitext( name )
                    if ext in ImageFileExts:
                        cur_images.append( ImageInfo(
                           name       = root,
                           image_name = join_image_name( volume_name, name ) ) )
                 
        else:
            image_info_path = join( self.path, 'image_info.py' )
            if exists( image_info_path ):
                # Load the manifest code and extract the images list:
                old_images = get_python_value( read_file( image_info_path ),
                                               'images' )
                                               
            # Check to see if our time stamp is up to data with the file:
            if self.time_stamp < time_stamp:
                
                # If not, create an ImageInfo object for each image file
                # contained in the path:
                for name in listdir( self.path ):
                    root, ext = splitext( name )
                    if ext in ImageFileExts:
                        cur_images.append( ImageInfo( 
                           name       = root, 
                           image_name = join_image_name( volume_name, name ) ) )
                           
        # Merge the old and current images into a single up to data list:
        if len( old_images ) == 0:
            images = cur_images
        elif len( cur_images ) == 0:
            images = old_images
        else:
            old_image_set = set( [ image.image_name for image in old_images ] )
            cur_image_set = set( [ image.image_name for image in cur_images ] )
            images        = ([ image for image in old_images
                                     if image.image_name in cur_image_set ] +
                             [ image for image in cur_images 
                                     if image.image_name not in old_image_set ])
        
        # Set the new time stamp of the volume:
        self.time_stamp = time_stamp
                           
        # Return the resulting sorted list as the default value:
        images.sort( key = lambda item: item.image_name )
        
        # Make sure all images reference this volume:
        for image in images:
            image.volume = self
        
        return images
    
    def _check_cache ( self, file_name ):
        """ Checks to see if the specified zip file name has been saved in the
            image cache. If it has, it returns the fully-qualified cache file
            name to use; otherwise it returns None.
        """
        cache_file = join( image_cache_path, self.name, file_name )
        if (exists( cache_file ) and 
           (time_stamp_for( stat( cache_file )[ ST_MTIME ] ) >
            self.time_stamp)):
            return cache_file
        
        return None
        
#-------------------------------------------------------------------------------
#  'ZipFileReference' class:  
#-------------------------------------------------------------------------------
                
class ZipFileReference ( ResourceReference ):
    
    # The zip file to read;
    zip_file = Instance( FastZipFile )
    
    # The volume name:
    volume_name = Str
    
    # The file within the zip file:
    file_name = Str
    
    # The name of the cached image file:
    cache_file = File
    
    #-- ResourceReference Interface Implementation -----------------------------

    def load ( self ):
        """ Loads the resource. 
        """
        # Check if the cache file has already been created:
        cache_file = self.cache_file
        if cache_file == '':
            # Extract the data from the zip file:
            data = self.zip_file.read( self.file_name )
                
            # Make sure the correct image cache directory exists:
            cache_dir = join( image_cache_path, self.volume_name )
            if not exists( cache_dir ):
                makedirs( cache_dir )
    
            # Write the image data to the cache file:            
            cache_file = join( cache_dir, self.file_name )
            fh         = file( cache_file, 'wb' )
            try:
                fh.write( data )
            finally:
                fh.close()
                
            # Save the cache file name in case we are called again:
            self.cache_file = cache_file
            
            # Release our reference to the zip file object:
            self.zip_file = None
            
        # Return the image data from the image cache file:
        return self.resource_factory.image_from_file( cache_file )
    
#-------------------------------------------------------------------------------
#  'ImageLibrary' class:
#-------------------------------------------------------------------------------

class ImageLibrary ( HasPrivateTraits ):
    """ Manages Traits UI image libraries.
    """
    
    # The list of available image volumes in the library:
    volumes = List( ImageVolume )
    
    # The volume dictionary (the keys are volume names, and the values are the
    # corresponding ImageVolume objects):
    catalog = Dict( Str, ImageVolume )
    
    # The list of available images in the library:
    images = Property( List, depends_on = 'volumes.images' )
    
    #-- Private Traits ---------------------------------------------------------
    
    # Mapping from a 'virtual' library name to a 'real' library name:
    aliases = Dict

    #-- Public methods ---------------------------------------------------------
    
    def image_info ( self, image_name ):
        """ Returns the ImageInfo object corresponding to a specified 
            **image_name**.
        """
        volume = self.find_volume( image_name )
        if volume is not None:
            return volume.catalog.get( image_name )
            
        return None
    
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
        image_volume_path = join( path, 'image_volume.py' )
        if exists( image_volume_path ):
            volume = get_python_value( read_file( image_volume_path ),
                                       'volume' )
        else:    
            volume = ImageVolume()
            
        # Set up the rest of the volume information:
        volume.set( name        = volume_name,
                    path        = path,
                    is_zip_file = False )
                    
        # Try to bring the volume information up to date if necessary:
        if volume.time_stamp < time_stamp_for( stat( path )[ ST_MTIME ] ):
            volume.save()
                    
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
    
    #-- Default Value Implementations ------------------------------------------
    
    def _volumes_default ( self ):
        # Get all volumes in the standard Traits UI image library directory:
        result = self._add_path( join( get_resource_path( 1 ), 'library' ) )
        
        # Check to see if there is an environment variable specifying a list
        # of paths containing image libraries:
        paths = environ.get( 'TRAITS_IMAGES' )
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

    def _catalog_default ( self ):
        return dict( [ ( volume.name, volume ) for volume in self.volumes ] )
        
    #-- Property Implementations -----------------------------------------------
    
    @cached_property
    def _get_images ( self ):
        return self._get_images_list()
        
    #-- Private Methods --------------------------------------------------------
    
    def _get_images_list ( self ):
        """ Returns the list of all library images.
        """
        # Merge the list of images from each volume:
        images = []
        for volume in self.volumes:
            images.extend( volume.images )
        
        # Sort the result:
        images.sort( key = lambda image: image.image_name )
        
        # Return the images list:
        return images
    
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
        path = abspath( path )
        
        # Make sure the path is a valid zip file:
        if is_zipfile( path ):
            
            # Create a fast zip file for reading:
            zf = FastZipFile( path = path )
            
            # Extract the volume name from the path:
            volume_name = splitext( basename( path ) )[0]
            
            # Get the names of all top-level entries in the zip file:
            names = zf.namelist()
            
            # Check to see if there is a manifest file:
            if 'image_volume.py' in names: 
                # Load the manifest code and extract the volume object:
                volume = get_python_value( zf.read( 'image_volume.py' ), 
                                           'volume' )
                    
                # Set the volume name:
                volume.name = volume_name
                    
                # Try to add all of the external volume references as
                # aliases for this volume:
                self._add_aliases( volume )
                
                # Set the path to this volume:
                volume.path = path
                
                # Save the reference to the zip file object we are using:
                volume.zip_file = zf
                
            else:
                # Create a new volume from the zip file:
                volume =  ImageVolume( name     = volume_name, 
                                       path     = path,
                                       zip_file = zf )
                 
            # If this volume is not up to date, update it:
            if volume.time_stamp < time_stamp_for( stat( path )[ ST_MTIME ] ):
                volume.save()
                
            # Return the volume:
            return volume
                
        # Indicate no volume was found:
        return None
        
    def _add_aliases ( self, volume ):
        """ Try to add all of the external volume references as aliases for 
            this volume.
        """
        aliases     = self.aliases
        volume_name = volume.name
        for vname in volume.aliases:
            if ((vname in aliases) and
                (volume_name != aliases[ vname ])):
                raise TraitError( ("Image library error: "
                    "Attempt to alias '%s' to '%s' when it is "
                    "already aliased to '%s'") %
                    ( vname, volume_name, aliases[ name ] ) )
            aliases[ vname ] = volume_name

    def _duplicate_volume ( self, volume_name ):
        """ Raises a duplicate volume name error.
        """
        raise TraitError( ("Attempted to add an image volume called '%s' when "
                  "a volume with that name is already defined.") % volume_name )
        
# Create the singleton image object:        
ImageLibrary = ImageLibrary()        
        
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
    time_stamp  = %(time_stamp)s,
    info        = [
%(info)s
    ]
)"""    

# Template for creating an ImageVolume 'images' list:
ImageVolumeImagesTemplate = \
"""from enthought.traits.ui.image     import ImageInfo
from enthought.traits.ui.ui_traits import Margin, Border 
    
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
        border      = Border( %(bleft)d, %(bright)d, %(btop)d, %(bbottom)d ),
        content     = Margin( %(cleft)d, %(cright)d, %(ctop)d, %(cbottom)d ),
        label       = Margin( %(lleft)d, %(lright)d, %(ltop)d, %(lbottom)d ),
        alignment   = %(alignment)s
    )"""
            
