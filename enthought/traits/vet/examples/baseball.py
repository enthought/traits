#-------------------------------------------------------------------------------
#  
#  Some simple traits-based classes for use with the Traits UI presentation  
#  and class.
#  
#  Written by: David C. Morrill
#  
#  Date: 09/09/2005
#  
#  (c) Copyright 2005 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:  
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import HasPrivateTraits,  Str, Range, RGBColor, List, Enum, Instance
    
#-------------------------------------------------------------------------------
#  'Player' class:  
#-------------------------------------------------------------------------------
        
class Player ( HasPrivateTraits ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    first_name = Str( 'Dirk' )
    last_name  = Str( 'Johnson' )
    number     = Range( 1, 99, 11 )
    
players = [
    Player( first_name = 'Tom',      last_name = 'Smith',    number = 27 ),
    Player( first_name = 'Ralph',    last_name = 'Clarke',   number = 33 ),
    Player( first_name = 'Bill',     last_name = 'Barnes',   number = 54 ),
    Player( first_name = 'Sam',      last_name = 'Thomas',   number = 17 ),
    Player( first_name = 'Tiberius', last_name = 'Impaleza', number = 61 ),
]

mgr = Player( first_name = 'Wally', last_name = 'McGee', number = 9 )

#-------------------------------------------------------------------------------
#  'Team' class:  
#-------------------------------------------------------------------------------
        
class Team ( HasPrivateTraits ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    name    = Str
    color   = RGBColor
    mascot  = Enum( 'Bear', 'Cougar', 'Horse', 'Coyote', 'Frog', 'Gopher' )
    players = List( Player, players )
    manager = Instance( Player, mgr )
    
