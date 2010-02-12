
from __future__ import absolute_import

from .toolkit import toolkit

def ColorTrait ( *args, **traits ):
    return toolkit().color_trait( *args, **traits )

def RGBColorTrait ( *args, **traits ):
    return toolkit().rgb_color_trait( *args, **traits )

def FontTrait ( *args, **traits ):
    return toolkit().font_trait( *args, **traits )

