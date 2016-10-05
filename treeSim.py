class Plant( object ):
   AVAILABLE_ENERGY = 0
   NEXT_ID = 0
   ROOT    = None
   WORLD   = None
   
   def __init__( self, x, y, parent=None ):
      self._parent   = parent
      self._branches = { }              # Map: child id -> branch inst
      self._id       = Branch.NEXT_ID
      self._x        = x
      self._y        = y
      
      Branch.NEXT_ID += 1
   
   def ident( self ):
      return self._id
   
   def grow( aSim, aWorld ):
      numPlantCellsToTryToGrow = min( MAX_PLANT_POPULATION - len(Plant.PLANT_CELLS), Plant.AVAILABLE_ENERGY // ENERGY_PER_PLANT_CELL )
      
      numUngrown = self._grow( numPlantCellsToTryToGrow )
      
      return numPlantCellsToTryToGrow - numUngrown

   def _grow( self, numToGrow ):
      if len(self._branches) >= 4:
         for child in self._branches:
            numToGrow = child._grow( numToGrow )
      else:
         for direction, posInfo in world.allNeighborsOf( self._x, self._y ).items():
            nx, ny, content = posInfo
            if content is None:
               child = Plant( nx, ny, self )
               self._branches[ child.ident() ] = child
               numToGrow -= 1
      return numToGrow
   
   def die( self ):
      if self._parent:
         self._parent._branches.update( self._branches )
      else:
         newRoot = choice( self._branches.keys() )
         newRoot._parent = None
         del self._branches[ newRoot.ident() ]
         newRoot._branches.update( self._branches )
         Plant.ROOT = newRoot


