from ModelSim import *
from random import randint, choice


ALL_DIRECTIONS = [ 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW' ]
DIRECTIONS = [ 'N', 'E', 'S', 'W' ]

class World( object ):
   DELTAS = {
      'N' :  (-1,  0),
      'NE':  (-1, +1),
      'E' :  ( 0, +1),
      'SE':  (+1, +1),
      'S' :  (+1,  0),
      'SW':  (+1, -1),
      'W' :  ( 0, -1),
      'NW':  (-1, -1)
      }
   
   def __init__( self, numRows, numCols ):
      self._numRows = numRows
      self._numCols = numCols
      
      self._locations = [ [ None for col in range(numCols) ] for row in range(numRows) ]
      
      self._neighborhood = [ ]
         # dict of precomputed coords for each of the 8 neighbors such that
         # self._neighborhood[x][y] returns the mapping:
         #                             directionString -> (neighborX,neighborY)
         # e.g. in a world 60x60 self._neighborhood[30][30] returns the dict:
         #           'NW': (29,29),  'N': (29,30),  'NE': (29,31)
         #           'W':  (30,29),   ----------    'E':  (30,31)
         #           'SW': (31,29),  'S': (31,30),  'SE': (31,31)
      
      for rowNum in range(numRows):
         columnVals = [ ]
         for colNum in range(numCols):
            neighborMap = { }
            for dirStr, dRowCol in World.DELTAS.items():
               dRow,dCol = dRowCol
               nRow,nCol = (rowNum + dRow) % numRows, (colNum + dCol) % numCols
               neighborMap[ dirStr ] = (nRow,nCol)
            columnVals.append( neighborMap )
         self._neighborhood.append( columnVals )

      self._cneighborhood = [ ]
         # dict of precomputed coords for each of the 4 neighbors such that
         # self._cneighborhood[x][y] returns the mapping:
         #                             directionString -> (neighborX,neighborY)
         # e.g. in a world 60x60 self._cneighborhood[30][30] returns the dict:
         #                           'N': (29,30)
         #           'W':  (30,29),   ----------    'E':  (30,31)
         #                           'S': (31,30)
      
      for rowNum in range(numRows):
         columnVals = [ ]
         for colNum in range(numCols):
            neighborMap = { }
            for dirStr in DIRECTIONS:
               dRowCol = World.DELTAS[ dirStr ]
               dRow,dCol = dRowCol
               nRow,nCol = (rowNum + dRow) % numRows, (colNum + dCol) % numCols
               neighborMap[ dirStr ] = (nRow,nCol)
            columnVals.append( neighborMap )
         self._cneighborhood.append( columnVals )

   # Extension
   def size( self ):
      return ( self._numRows, self._numCols )

   def setAt( self, r, c, val ):
      self._locations[r][c] = val

   def getAt( self, r, c ):
      return self._locations[r][c]

   def remove( self, r, c, what ):
      self._locations[r][c] = None

   def moveTo( self, oldR, oldC, newR, newC ):
      self._locations[newR][newC] = self._locations[oldR][oldC]
      self._locations[oldR][oldC] = None
      
   def getPosNeighbor( self, row, col, direction ):
      '''Return the contents of the neighboring position.'''
      nRow,nCol = self._neighborhood[row][col][direction]
      return nRow, nCol, self._locations[nRow][nCol]

   def randPos( self ):
      # Return a cell x, y at random
      row = randint( 0, self._numRows - 1 )
      col = randint( 0, self._numCols - 1 )
      return ( row, col, self._locations[row][col] )
   
   def setAtRandomPos( self, anObj, maxAttempts=100 ):
      attempts = 0
      row, col, content = self.randPos( )
      while (content is not None) and (attempts < maxAttempts):
         row, col, content = self.randPos( )
         attempts += 1
      
      if attempts == maxAttempts:
         raise Exception( "Can't find a place to locate the new Entity." )
      
      self._locations[row][col] = anObj
      
      return row,col

   def findRandomFreePos( self, maxAttempts=100 ):
      row, col, content = self.randPos( )
      
      for count in range(maxAttempts):
         row, col, content = self.randPos( )
         if content is not None:
            return row,col
      
      raise Exception( "Can't find a place to locate the new Entity." )

   def findRandomObjectOfType( self, anObjType, maxAttempts=100 ):
      row, col, content = self.randPos( )
      
      for count in range(maxAttempts):
         row, col, content = self.randPos( )
         if isinstance(content, anObjType):
            return row, col
      
      raise Exception( "Can't find a place to locate the new Entity." )

   def relativePos( self, row, col, direction ):
      return self._neighborhood[row][col][direction]

   def relativePosNeighbor( self, row, col, direction ):
      nRow,nCol = self._neighborhood[row][col][direction]
      return nRow,nCol,self._locations[nRow][nCol]

   def neighborsOf( self, row, col ):
      result = { }
      for direction,rowCol in self._neighborhood[row][col].items(): # <- precomputed neighbor coords map: dirStr -> (nRow,nCol)
         nRow,nCol = rowCol
         result[direction] = nRow, nCol, self._locations[nRow][nCol]
      return result

   def cNeighborsOf( self, row, col ):
      result = { }
      for direction,rowCol in self._cneighborhood[row][col].items(): # <- precomputed neighbor coords map: dirStr -> (nRow,nCol)
         nRow,nCol = rowCol
         result[direction] = nRow, nCol, self._locations[nRow][nCol]
      return result

   def neighborsOfIn( self, row, col, dirSet=DIRECTIONS ):
      result = { }
      neighborhood = self._neighborhood[row][col] # <- precomputed neighbor coords map: dirStr -> (nRow,nCol)
      for direction in dirSet:
         nRow,nCol = neighborhood[direction]
         result[direction] = nRow, nCol, self._locations[nRow][nCol]
      return result

   def neighborsOfType( self, row, col, aType ):
      '''Similar to allNeighborsOfType() but returns a list of the objects
      in those locations rather than the coordinates.
      This version of the function uses precomputed coorediates for each neighbor.'''
      result = [ ]
      for direction, rowCol in self._neighborhood[row][col].items(): # <- precomputed neighbor coords map: dirStr -> (nRow,nCol)
         nRow,nCol = rowCol
         contents = self._locations[nRow][nCol]
         if isinstance( contents, aType ):
            result.append( contents )
      return result

   def cNeighborsOfType( self, r, c, aType ):
      '''Similar to allNeighborsOfType() but returns a list of the objects
      in those locations rather than the coordinates.
      This version of the function uses precomputed coorediates for each neighbor.'''
      result = [ ]
      for direction, rowCol in self._cneighborhood[r][c].items(): # <- precomputed neighbor coords map: dirStr -> (nRow,nCol)
         nRow,nCol = rowCol
         contents = self._locations[nRow][nCol]
         if isinstance( contents, aType ):
            result.append( contents )
      return result

   def neighborsOfTypeIn( self, row, col, aType, dirSet=DIRECTIONS ):
      '''Similar to allNeighborsOfType() but returns a list of the objects
      in those locations rather than the coordinates.
      This version of the function uses precomputed coorediates for each neighbor.'''
      result = [ ]
      neighborhood = self._neighborhood[row][col] # <- precomputed neighbor coords map: dirStr -> (nRow,nCol)
      for direction in dirSet:
         nRow,nCol = neighborhood[direction]
         contents = self._locations[nRow][nCol]
         if isinstance( contents, aType ):
            result.append( contents )
      return result

   def emptyNeighbors( self, r, c ):
      result = [ ]
      for direction,rowCol in self._neighborhood[r][c].items(): # <- precomputed neighbor coords map: dirStr -> (nRow,nCol)
         nRow,nCol = rowCol
         if self._locations[nRow][nCol] is None:
            result.append( (nRow,nCol) )
      return result

   def emptyCNeighbors( self, row, col ):
      result = [ ]
      for direction,rowCol in self._cneighborhood[row][col].items(): # <- precomputed neighbor coords map: dirStr -> (nRow,nCol)
         nRow,nCol = rowCol
         if self._locations[nRow][nCol] is None:
            result.append( (nRow,nCol) )
      return result

   def emptyNeighborsIn( self, row, col, dirSet=ALL_DIRECTIONS ):
      result = [ ]
      neighborhood = self._neighborhood[row][col] # <- precomputed neighbor coords map: dirStr -> (nRow,nCol)
      for direction in dirSet:
         nRow,nCol = neighborhood[direction]
         if self._locations[nRow][nCol] is None:
            result.append( (nRow,nCol) )
      return result

   def newPos( self, row, col, direction, distance ):
      if 0 <= distance <= 2:
         nRow,nCol = row,col
         for ct in range(distance):
            dRow,dCol = World.DELTAS[ direction ]
            nRow,nCol = (row+dRow) % self._numRows, (col+dCol) % self._numCols
         return nRow,nCol
      else:
         pass # error

   def __iter__( self ):
      return WorldIter( self )


class WorldIter( object ):
   def __init__( self, aWorld ):
      self._world = aWorld
      self._row   = 0
      self._col   = 0
      
      self._numRows, self._numCols = aWorld.size( )
   
   def __iter__( self ):
      return self
   
   def __next__( self ):
      if self._col == None:
         raise StopIteration( )
      
      content = self._world.getAt( self._row, self._col )
      
      self._col += 1
      
      if self._col >= self._numCols:
         self._row += 1
         self._col = 0
      
      if self._row >= self._numRows:
         self._row = None
         self._col = None
      
      return (self._row, self._col, content)

class WorldObject( Model ):
   def __init__( self, aWorld, r, c, ident=None ):
      '''If xPos is None, the WorldObject is not placed onto the board.'''
      Model.__init__( self, ident )
      self._world  = aWorld
      self._r      = r
      self._c      = c

      aWorld.setAt( r, c, self )

   # Extension
   def position( self ):
      return self._r, self._c

   def moveTo( self, newRow, newCol ):
      self._world.moveTo( self._r, self._c, newRow, newCol )
      self._r, self._c = newRow, newCol


class Monitor( Model ):
   def __init__( self, aWorld ):
      Model.__init__( self, 'Monitor' )
      self._world = aWorld
      self._msgs = [ ]

   # Specialization of Subscriber
   def handleMessage( self, aMsg ):
      print( aMsg )

   # Specialization of Model
   def subscriptionTopics( self ):
      return [ '*' ]

   def tick( self ):
      pass
   

class SpeciesGenome( object ):
   NEXT_GENOME_ID = 0

   def __init__( self, parentSpeciesId=None ):
      self._speciesId        = SpeciesGenome.NEXT_GENOME_ID
      self._parentSpeciesId  = parentSpeciesId
      self._birthTime        = None               # simTime first individual is born
      self._deathTime        = None               # simTime last individual dies
      self._living           = [ ]                # currently living individuals
      self._memberHistory    = { }                # entityID mapped to [ birth time, death time ]
      
      SpeciesGenome.NEXT_GENOME_ID += 1
   
   # Extension
   def ident( self ):
      return self._speciesId
   
   def parentSpeciesIdent( self ):
      return self._parentSpeciesId

   def membersAliveAt( self, aSimTime=None ):
      if aSimTime is None:
         return len(self._living)
      else:
         count = 0
         for entId,dates in self._memberHistory.items():
            if dates[1] is None:
               if dates[0] <= aSimTime:
                  count += 1
            else:
               if dates[0] <= aSimTime < dates[1]:
                  count += 1
         return count
   
   def totalMembers( self ):
      return len( self._memberHistory )

   def recordBirth( self, child ):
      self._living.append( child.ident() )
      self._memberHistory[ child.ident() ] = [ child.birthTime(), None ]
      if self._birthTime is None:
         self._birthTime = child.birthTime( )

   def recordDeath( self, entity ):
      self._deathTime = entity._sim.simTime( )
      
      self._living.remove( entity.ident() )
      self._memberHistory[ entity.ident() ][ 1 ] = self._deathTime

   # Interface
   def genes( self ):
      raise NotImplementedError( )
   
   def mutatedGenome( self ):
      raise NotImplementedError( )


class SpeciesTree( object ):
   def __init__( self ):
      self._species = { }                # speciesID to SpeciesGenome
   
   # Extension
   def recordNewSpecies( self, genome ):
      childSpeciesId = genome.ident()
      self._species[ childSpeciesId ] = genome

   def deriveNewSpecies( self, parentGenome  ):
      parentSpeciesId = parentGenome.ident()
      parentGenome    = self._species[ parentSpeciesId ]
      
      childGenome = parentGenome.mutatedGenome( )
      self.recordNewSpecies( childGenome )
      
      return childGenome
   
   def speciesGenome( self, speciesId ):
      return self._species[ speciesId ]

   def entitiesAliveAt( self, aSimTime=None ):
      count = 0
      for ident,info in self._species.items():
         count += info.membersAliveAt( aSimTime )
      return count


class Cell( WorldObject ):
   POPULATION = 0
   R_tracker = { 0:[0,0,0], 1:[0,0,0], 2:[0,0,0], 3:[0,0,0], 4:[0,0,0], 5:[0,0,0], 6:[0,0,0], 7:[0,0,0], 8:[0,0,0] }   
   N_tracker = { 0:[0,0,0], 1:[0,0,0], 2:[0,0,0], 3:[0,0,0], 4:[0,0,0], 5:[0,0,0], 6:[0,0,0], 7:[0,0,0], 8:[0,0,0] }   
   
   def __init__( self, aWorld, generation=0, ident=None, energy=0, row=None, col=None ):
      self._birthTime       = 0
      self._age             = 0
      self._generation      = generation
      self._store           = energy
      self._lastMove        = '_'
      WorldObject.__init__( self, aWorld, row, col, ident )
      
      Cell.POPULATION += 1

   # Specialization of Subscriber   
   def handleMessage( self, aMsg ):
      pass

   # Specialization of Model
   def subscriptionTopics( self ):
      return [ ]

   def _addedToSimulation( self, aSimulation ):
      WorldObject._addedToSimulation( self, aSimulation )
      self._birthTime = self._sim.simTime( )

   def tick( self ):
      if self._store <= 0:
         self._behavior_die( 'energy' )
      else:
         theChosenBehavior = self._chooseBehavior( )
         self._realizeBehavior( theChosenBehavior )
      self._age += 1
   
   # Extension
   def birthTime( self ):
      return self._birthTime

   def generation( self ):
      return self._generation

   def storedEnergy( self ):
      return self._store
   
   def _behavior_clone( self ):
      # Determine where to place the daughter cell
      try:
         neighbors = self._world.emptyNeighbors( self._r, self._c )
         daughterRow,daughterCol = choice( neighbors )  # <- throws if len(neighbors) == 0
      except:
         return False

      # Determine daughter/parent energy after clone
      daughterEnergy = self._store // 2
      daughter = self._clone( daughterEnergy, daughterRow, daughterCol )
      
      self._store -= daughterEnergy
      self._age    = 0  # <--- Optiona

      # set her aloft
      self._sim.add( daughter )
      
      return True

   def _behavior_die( self, reason=None ):
      # Adjust the population
      Cell.POPULATION -= 1
      
      # Remove the entity model from the simulation, and free the obj
      self._world.remove( self._r, self._c, self )
      self._sim.drop(self)
      
      # Perform analysis:
      # For n occurrences of a given gene in a cell's genetic code, compute:
      #    - tally of such cells died so far
      #    - Total of age of death for all such cells
      #    - Average age of death of all such cells
      
      #count = self._genes.count('R')
      #num, totAge, avgAge = Cell.R_tracker[ count ]
      #num += 1
      #totAge += self._age
      #avgAge = totAge / num
      #Cell.R_tracker[ count ] = [ num, totAge, avgAge ]
      #print( Cell.R_tracker )

      #count = self._genes.count('N')
      #num, totAge, avgAge = Cell.N_tracker[ count ]
      #num += 1
      #totAge += self._age
      #avgAge = totAge / num
      #Cell.N_tracker[ count ] = [ num, totAge, avgAge ]
      #print( Cell.N_tracker )
      #if self._age >= 40:
         #print( '   ', self._age, ':', self._genes )

   def _behavior_move( self, direction ):
      # Determine the new Coords and return if already occupied
      #if direction == 'R':
         #direction = choice( DIRECTIONS )
         
      #elif direction == 'F':
         #neighborSet = self._world.allNeighborsOfType2( self._row, self._col, Cell )
         #try:
            #aCellInst = choice( neighborSet )
            #direction = aCellInst._lastMove
         #except:
            #return False
      
      # Determine desired move coords
      #self._lastMove = direction
      newRow, newCol, content = self._world.relativePosNeighbor( self._r, self._c, direction )
      if content is not None:
         return False
      
      # Perform the move
      #self._moveTo( newRow, newCol ) Expanded here for performance
      self._world.moveTo( self._r, self._c, newRow, newCol )
      self._r, self._c = newRow, newCol
      
      return True

   def _behavior_eat( self, row=None, col=None ):
      if (row is None) or (col is None):
         row,col = self._r, self._c
      
      # Determine if there's actually something to eat there
      food = self._world.getAt( row, col )
      
      # perform the action
      self._store += food.feed( )

   # Interface
   def _chooseBehavior( self ):
      raise NotImplementedError( )
   
   def _realizeBehavior( self, aBehavior, **args ):
      raise NotImplementedError( )
   
   def _clone( self, daughterEnergy, daughterRow, daughterCol, mutate=False ):
      raise NotImplementedError( )

if __name__ == '__main__':
   import timeit
   
   w = World( 60, 60 )
   
   def testOld( ):
      for ct in range( 100 ):
         x, y, c = w.randPos( )
         w.allEmptyNeighbors2( x, y )
   
   def testNew( ):
      for ct in range( 100 ):
         x, y, c = w.randPos( )
         w.emptyNeighbors( x, y )

   print( 'New', timeit.timeit( 'testNew( )', setup='from __main__ import testNew', number=1000 ) )
   print( 'Old', timeit.timeit( 'testOld( )', setup='from __main__ import testOld', number=1000 ) )
   
