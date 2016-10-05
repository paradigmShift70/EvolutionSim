from CellSim import *
import random
from collections import OrderedDict


class PlantCell( WorldObject ):
   WORLD           = None
   PLANT           = None
   ENERGY_PER_CELL = None
   
   def __init__( self, row, col ):
      WorldObject.__init__( self, PlantCell.WORLD, row, col )

   def feed( self ):
      PlantCell.PLANT.freePlantCell( self )
      return PlantCell.ENERGY_PER_CELL


class Plant( Model ):
   AVAILABLE_ENERGY = 0

   def __init__( self, aWorld, maxPlantSize, energyPerCell, randGrowthFactor ):
      Model.__init__( self )
      
      PlantCell.WORLD  = aWorld
      PlantCell.PLANT  = self
      PlantCell.ENERGY_PER_CELL = energyPerCell
      
      self._world            = aWorld
      self._maxSize          = maxPlantSize
      self._plantCells       = OrderedDict( )
      self._randGrowthFactor = randGrowthFactor
      self._availableGrowthEnergy = 0

   # Specialization of Subscriber
   def subscriptionTopics( self ):
      return [ ]
   
   def handleMessage( self, aMsg ):
      if aMsg.topic() == 'Energy Freed':
         self._availableGrowthEnergy += aMsg[ 'units' ]
      elif aMsg.topic() == 'Plant Cell Eaten':
         plantCell = aMsg[ 'cell' ]
         eater     = aMsg[ 'sender' ]
         sendMessage( 'Gain Energy', eater, units=10 )
         self.freePlantCell( plantCell )

   # Specialization of Model
   def tick( self ):
      numPlantCellsToTryToGrow = min( self._maxSize - len(self._plantCells), Plant.AVAILABLE_ENERGY // Params.ENERGY_PER_PLANT_CELL )
      
      if numPlantCellsToTryToGrow < 20:
         return 0
      
      numPlantCellsGrown = self.grow( numPlantCellsToTryToGrow )

      Plant.AVAILABLE_ENERGY -= (numPlantCellsGrown * Params.ENERGY_PER_PLANT_CELL)
   
   # Extension
   def size( self ):
      return len(self._plantCells)

   def startPlant( self, row, col ):
      c = PlantCell( row, col )
      self._plantCells[ c.ident() ] = c
      self.tick()   # <- enter a growth cycle to prime the Plant
   
   def grow( self ):
      raise NotImplementedError( )

   def freePlantCell( self, aCell ):
      del self._plantCells[ aCell._ident ]
      PlantCell.WORLD.remove( aCell._r, aCell._c, aCell )


class Plant_A( Plant ):
   def __init__( self, aWorld, maxPlantSize, energyPerCell, randGrowthFactor ):
      Plant.__init__( self, aWorld, maxPlantSize, energyPerCell, randGrowthFactor )
   
   def grow( self, numPlantCellsToTryToGrow ):
      numPlantCellsGrown = 0
      
      plantCellIds = list(self._plantCells.keys())
      for plantCellIdent in plantCellIds:
         plantRowCol = self._plantCells[ plantCellIdent ].position( )
         for row,col in self._world.emptyNeighbors( *plantRowCol ):
            if numPlantCellsGrown >= numPlantCellsToTryToGrow:
               return numPlantCellsGrown
            
            newCell = PlantCell( row, col )
            PlantCell.WORLD.setAt( row, col, newCell )
            self._plantCells[ newCell.ident() ] = newCell
            numPlantCellsGrown += 1
      
      return numPlantCellsGrown


class Plant_B( Plant ):
   def __init__( self, aWorld, maxPlantSize, energyPerCell, randGrowthFactor ):
      Plant.__init__( self, aWorld, maxPlantSize, energyPerCell, randGrowthFactor )
   
   def grow( self, numPlantCellsToTryToGrow ):
      numPlantCellsGrown = 0
      
      plantCellIds = sorted(self._plantCells.keys(), reverse=True)
      for plantCellIdent in plantCellIds:
         plantRowCol = self._plantCells[ plantCellIdent ].position( )
         for row,col in self._world.allNeighbors2( *plantRowCol ):
            if numPlantCellsGrown >= numPlantCellsToTryToGrow:
               return numPlantCellsGrown
            
            newCell = PlantCell( row, col )
            PlantCell.WORLD.setAt( row, col, newCell )
            self._plantCells[ newCell.ident() ] = newCell
            numPlantCellsGrown += 1

      return numPlantCellsGrown


class Plant_C( Plant ):
   def __init__( self, aWorld, maxPlantSize, energyPerCell, randGrowthFactor ):
      Plant.__init__( self, aWorld, maxPlantSize, energyPerCell, randGrowthFactor )
   
   def grow( self, numPlantCellsToTryToGrow ):
      numPlantCellsGrown = 0
      while numPlantCellsGrown < numPlantCellsToTryToGrow:
         for plantCellIdent in reversed(self._plantCells):
            plantRowCol = self._plantCells[ plantCellIdent ].position( )
            for row,col in self._world.emptyCNeighbors( *plantRowCol ):
               if numPlantCellsGrown >= numPlantCellsToTryToGrow:
                  return numPlantCellsGrown
               
               if random.random() < self._randGrowthFactor:        # 1.0 mimics Plant_A
                  newCell = PlantCell( row, col )
                  self._plantCells[ newCell.ident() ] = newCell
                  numPlantCellsGrown += 1
      
      return numPlantCellsGrown


class Plant_D( Plant ):
   def __init__( self, aWorld, maxPlantSize, energyPerCell, randGrowthFactor ):
      Plant.__init__( self, aWorld, maxPlantSize, energyPerCell, randGrowthFactor )
   
   def grow( self, numPlantCellsToTryToGrow ):
      numPlantCellsGrown = 0
      while numPlantCellsGrown < numPlantCellsToTryToGrow:
         revPlantCells = reversed(self._plantCells)
         for plantCellIdent in revPlantCells:                    ### REQUIRES PYTHON 3.2 OR 3.3
            plantCell = self._plantCells[ plantCellIdent ]
            plantRowCol = self._plantCells[ plantCellIdent ].position( )

            #try:
               #nbrRowCol = random.choice( self._world.emptyCNeighbors(*plantRowCol) )
               #newCell = PlantCell( *nbrRowCol )
               #self._plantCells[ newCell.ident() ] = newCell
               #numPlantCellsGrown += 1
            #except:
               #pass

            for row,col in self._world.emptyCNeighbors( *plantRowCol ):
               if numPlantCellsGrown >= numPlantCellsToTryToGrow:
                  return numPlantCellsGrown
               
               if random.random() < self._randGrowthFactor:        # 1.0 mimics Plant_A
                  newCell = PlantCell( row, col )
                  self._plantCells[ newCell.ident() ] = newCell
                  numPlantCellsGrown += 1
                  break    #  <--- C differs from D only by no 'break' here
      
      return numPlantCellsGrown


import Params

class SimpleCell( Cell ):
   def __init__( self, aWorld, genes, generation=0, ident=None, energy=0, row=None, col=None ):
      Cell.__init__( self, aWorld, generation, ident, energy, row, col )
      self._currentState = 0
      self._genes        = genes

   def tick( self ):
      if self._store <= 0:
         self._behavior_die( )
      else:
         self._store -= Params.ENERGY_PER_MOVE
         Plant.AVAILABLE_ENERGY += Params.ENERGY_PER_MOVE
         
         try:
            # Try to eat
            neighbors = self._world.cNeighborsOfType( self._r, self._c, PlantCell )
            plantCellInst = choice( neighbors ) # <- throws if len(neighbors) == 0
            self._store += plantCellInst.feed( )
         except:
            try:
               if (self._store >= Params.WELL_FED_LEVEL) and (self._age > Params.MATURITY) and (Cell.POPULATION < Params.MAX_CELL_POPULATION):
                  self._behavior_clone( )       # <- throws if no place to put a daughter
               else:
                  nextDir = self._genes[ self._currentState ]
                  if nextDir != '_':
                     self._behavior_move( nextDir )
                  self._currentState += 1
                  self._currentState %= Params.GENOME_LENGTH
            except:
               pass
         
         self._age += 1

   def _behavior_clone( self ):
      # Determine where to place the daughter cell
      try:
         neighbors = self._world.emptyNeighbors( self._r, self._c )
         daughterRow,daughterCol = choice( neighbors )  # <- throws if len(neighbors) == 0
      except:
         return False

      # Create the daughter's genes
      daughterGenes = self._genes[:] # <- copy the mother's genes
      daughterGenes[ randint(0,Params.GENOME_LENGTH-1) ] = choice( Params.GENES ) # <- mutate
      
      # Perform the clone
      daughter = SimpleCell( self._world, daughterGenes, self._generation + 1, energy=self._store // 2, row=daughterRow, col=daughterCol )
      
      # Turn the mother into a daughter
      self._store -= daughter._store
      self._age    = 0

      # set her aloft
      self._sim.add( daughter )
      
      return True


from chromosome import Chromosome
class CrCell( Cell ):
   def __init__( self, chromosomes, aWorld, generation=0, ident=None, energy=0, row=None, col=None ):
      self._chromosomes     = chromosomes
      Cell.__init__( self, aWorld, generation, ident, energy, row, col )

   # Specialization of Model
   def tick( self ):
      if self._store <= 0:
         self._behavior_die( 'energy' )
      else:
         self._chromosomes.express( None, self, self._world )
      self._age += 1
   
   # Extension
   def _behavior_clone( self ):
      # Determine where to place the daughter cell
      neighbors = self._world.emptyNeighbors( self._r, self._c )
      daughterRow,daughterCol = choice( neighbors )  # <- throws if len(neighbors) == 0

      # Create the daughter's genes
      daughterChromosomes = self._chromosomes.clone( mutate=True )
      
      # Determine daughter/parent energy after clone
      daughterEnergy = self._store // 2
      daughter = CrCell( daughterChromosomes, self._world, self._generation + 1, energy=daughterEnergy, row=daughterRow, col=daughterCol )
      
      self._store -= daughterEnergy
      self._age    = 0

      # set her aloft
      self._sim.add( daughter )

