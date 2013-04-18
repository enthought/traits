#!/usr/bin/env python

## ex_traits_Introspection_02.py

## -- Notes -----------------------------------------------------------------
# suffixes on variables indicate the type of variable. For example, a
#   suffix of:
#   TL => Traits List
#   TE => Traits Enum
#   TR => Traits Range
#   A => numpy Array
#   MG => numpy MeshGrid
#   APD => ArrayPlotData
#   P = chaco Plot object

## -- Imports ---------------------------------------------------------------

# Enthought imports
from traits.api import HasTraits, Int

# Chaco imports
from chaco.api import ArrayPlotData

## -- Defines ---------------------------------------------------------------

## -- Let's Begin -----------------------------------------------------------

## -- Functions -------------------------------------------------------------

## -- Classes ---------------------------------------------------------------

class TraitedClass( HasTraits ):
  '''illustrates lazy initialization with Traits'''

  # a Traits Int
  myTI = Int( 3 )

  # a python Int, Float
  myInt = 5
  myFloat = 6.7

## -- Main ------------------------------------------------------------------

if __name__ == "__main__":

  # build the object
  traitedClass = TraitedClass()

  # Let's look for traitedClass objects that start with "my".
  # we find myInt and myFloat but not myTI.
  myObjects = [thisItem for thisItem in dir(traitedClass) if thisItem[0:2] == 'my']
  print( myObjects )

  # let's read myTI, then ask again. We now see myTI in the dir()
  print( "myTI = %i" % traitedClass.myTI )
  myObjects = [thisItem for thisItem in dir(traitedClass) if thisItem[0:2] == 'my']
  print( myObjects )

## -- EOF -------------------------------------------------------------------
