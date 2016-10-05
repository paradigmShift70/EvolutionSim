import Params
from random import choice, randint, shuffle

class Chromosome( object ):
   def __init__( self ):
      pass
   
   def name( self ):
      pass
   
   def clone( self, mutate=False ):
      pass

   def express( self, cell, environment ):
      pass


# ###################
# Sensing Chromosomes
class SenseChromosome( Chromosome ):
   pass


# #####################
# Cognative Chromosomes
class CognitiveChromosome( Chromosome ):
   pass

class CoordinatingChromosome( Chromosome ):
   def __init__( self, *subordinates ):
      Chromosome.__init__( self )
      self._subordinates = subordinates
   
   def name( self ):
      return 'Coordinating Chromosome'

   def clone( self, mutate=False ):
      if mutate == True:
         mutationType = choice( ['shuffle', 'mutate sub', 'mutate sub', 'mutate sub'] )
      else:
         mutationType = None
      
      if mutationType == 'mutate sub':
         subToMutate = randint( 0, len(self._subordinates) - 1 )
      else:
         subToMutate = -1
      
      clonedSubordinates = [ ]
      for subIndex, sub in enumerate(self._subordinates):
         if subIndex == subToMutate:
            clonedSubordinates.append( sub.clone(True) )
         else:
            clonedSubordinates.append( sub.clone(False) )
      
      if mutationType == 'shuffle':
         shuffle( clonedSubordinates )
      
      return CoordinatingChromosome( *clonedSubordinates )

   def express( self, message, cell, environment ):
      from SimpleCellSim import Plant
      cell._store -= Params.ENERGY_PER_MOVE
      Plant.AVAILABLE_ENERGY += Params.ENERGY_PER_MOVE
      
      for sub in self._subordinates:
         try:
            sub.express( message, cell, environment )
            break
         except:
            pass


# ######################
# Behavioral Chromosomes
class BehaviorChromosome( Chromosome ):
   pass


class EatRandom_BehaviorChromosome( BehaviorChromosome ):
   def __init__( self, foodClass ):
      BehaviorChromosome.__init__( self )
      self._foodClass = foodClass
   
   def name( self ):
      return 'Behavior Eat'
   
   def clone( self, mutate=False ):
      return EatRandom_BehaviorChromosome( self._foodClass )
   
   def express( self, message, cell, environment ):
      neighbors = environment.cNeighborsOfType( cell._r, cell._c, self._foodClass )
      foodObj = choice( neighbors ) # <- throws if len(neighbors) == 0
      cell._store += foodObj.feed( )


class Move_BehaviorChromosome( BehaviorChromosome ):
   VALID_GENES = [ 'N', 'S', 'E', 'W', '_' ] #, 'R', 'F' ]
   
   def __init__( self, genes ):
      BehaviorChromosome.__init__( self )
      self._genes = genes
      self._next  = 0
      self._modSize = len(self._genes) - 1
   
   def name( self ):
      return 'Behavior Move'
   
   def clone( self, mutate=False ):
      daughterGenes = self._genes[:]
      
      #if mutate:
      daughterGenes[ randint(0,self._modSize) ] = choice( Move_BehaviorChromosome.VALID_GENES )
      
      return Move_BehaviorChromosome( daughterGenes )
   
   def express( self, message, cell, environment ):
      direction = self._genes[ self._next ]
      
      self._next += 1
      self._next %= self._modSize

      if direction == '_':
         raise Exception()
   
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
      newRow, newCol, content = environment.relativePosNeighbor( cell._r, cell._c, direction )
      if content is not None:
         raise Exception( )
      
      # Perform the move
      #self._moveTo( newRow, newCol ) Expanded here for performance
      environment.moveTo( cell._r, cell._c, newRow, newCol )
      cell._r, cell._c = newRow, newCol


class Clone_BehaviorChromosome( BehaviorChromosome ):
   def __init__( self ):
      BehaviorChromosome.__init__( self )
   
   def name( self ):
      return 'Behavior Clone'

   def clone( self, mutate=False ):
      return Clone_BehaviorChromosome( )
   
   def express( self, message, cell, environment ):
      if (cell._store < Params.WELL_FED_LEVEL) or (cell._age < Params.MATURITY) or (cell.POPULATION >= Params.MAX_CELL_POPULATION):
         raise Exception( )
      
      cell._behavior_clone( )
      
      #if (cell._store >= self._wellFedLevel) and (cell._age > self._maturityAge) and (cell.POPULATION < Params.MAX_CELL_POPULATION):
         #cell._behavior_clone( )       # <- throws if no place to put a daughter
      #else:
         #raise Exception( )


