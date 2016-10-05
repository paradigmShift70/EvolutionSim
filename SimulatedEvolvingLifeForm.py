from ModelSim import *
from CellSim import *
from random import choice, random, randint
from copy import copy, deepcopy

'''
Message Publication
Topic        Sender      Payload dictionary          Comments
-----------  ----------  --------------------------  ---------------------------
join         PostOffice  who:   newly joined object
                         xy:    xy location          optional
leave        PostOffice  who:   object leaving
move         Entity      oldxy: orig row, col        =None if new object
                         newxy: new row, col
                         dir:   movement dir         =None if object is new
eat          Entity      xy:    entity row,col
                         food_xy:food row,col
                         dir:       food dir from entity
die          Entity      xy:        entity row, col
clone        Entity      xy:        parent row, col
                         dxy:       daughter row, col
                         daughter:  daughter
                         d_mutated: True | False     Is the daugher mutated
horn of plenty  God                                  deploy lots of food
'''

class God( Model ):
   def __init__( self, aBoard ):
      super().__init__( 'God' )
      self._board = aBoard
      self._who   = { }   # map mod name str to list: [ mod, x, y ]
      
      self._nextSoonestRain = 11

   def subscriptionTopics( self ):
      return [ '*' ]

   def handleMessage( self, aMsg ):
      return

   def tick( self ):
      livingEntities = Entity.SPECIES.entitiesAliveAt( )
      if (SIM.simTime() >= self._nextSoonestRain) and (livingEntities <= 4):
         self.hornOfPlenty(20)
   
   def hornOfPlenty( self, numFoodToDeploy, massPerFood=1 ):
      for ct in range(numFoodToDeploy):
         try:
            f = Food(self._board)
            SIM.add( f, xy=f.position() )
         except:
            pass
      
      SIM.postMessage( Message('horn of plenty', self, self._sim.simTime()) )
      self._nextSoonestRain = SIM.simTime() + 30

class Rule( object ):
   def __init__( self, intCond, extCond, behavior ):
      self.intCond  = intCond
      self.extCond  = extCond
      self.behavior = behavior


class Entity( WorldObject ):
   # Physics: Mass vs energy
   ENERGY_PER_MASS                 =  100     # 100 energy units = 1 mass unit
   
   # Mortality
   BASE_MORTALITY                  =  100     # Cell starts with 80 ticks of life.
   ADDITIONAL_MORTALITY_UPON_EAT   =    0     # Cell gets 5 additional ticks of life if it eats.
   ADDITIONAL_MORTALITY_UPON_CLONE =   10     # Cell gets 20 additional ticks of life if it clones itself.
   
   # Activity Energy
   ENERGY_TO_SURVIVE_1_MASS        =    0.01  # energy needed per unit mass of cell just to survive one tick.
   ENERGY_TO_CLONE_1_MASS          =    0.5   # 1 energy clones 1 unit of mass
   ENERGY_TO_MOVE_1_MASS           =    0.03  # 1 energy moves 10 units of mass
   ENERGY_TO_EAT_1_MASS            =    1     # to eat 1 mass
   ENERGY_TO_DROP_1_MASS           =    1     # for any mass

   # Other Constants
   MIN_ENERGY_AFTER_CLONE          =  500     # After clon each daughter has at least 500 energy
   MUTATION_RATE                   =    0.1   # 10% of daughters will be mutated
   RAND_LOW_THREASHOLD             =    0.1   # 10% chance
   ENERGY_REMAINING_UPON_DEATH     =    0.5   # Half the entity's mass
   MASS_OF_1_RULE                  =   10     # Each rule is 20 units of mass
   
   CHOOSE_BEHAVIOR_METHOD          = 'PRIORITIZED'  # Values: RANDOM, PRIORITIZED
   
   MUTATIONS = [ 'DOUBLE RULE', 'OMITT RULE', 'CHANGE INT COND', 'CHANGE EXT COND', 'CHANGE BEHAVIOR' ]
   INT_CONDS = [ 'ANY', 'RAND_LOW', 'CAN_CLONE' ]
   EXT_CONDS = [ 'ANY', 'FOOD_FORWARD', 'EMPTY_FORWARD', 'EMPTY_NEIGHBOR_POS', 'NON_EMPTY_FORWARD' ]
   #EXT_CONDS = [ 'ANY', 'OBJ_FOOD_N_1', 'OBJ_FOOD_S_1', 'EMPTY_NEIGHBOR_POS' ] # BUMPED_<dir>, FOOD_ANYDIR
   BEHAVIORS = [ 'MOVE_FORWARD', 'EAT_FORWARD', 'TURN_RIGHT', 'TURN_LEFT', 'TURN_RAND', 'CLONE' ]
   #BEHAVIORS = [ 'MOVE_RAND', 'MOVE_LINE', 'EAT_N', 'EAT_S', 'CLONE' ]  # BUMP_<dir>, EAT_ANYDIR

   SPECIES = SpeciesTree( )
   
   def __init__( self, aBoard, speciesId, ident=None, parentID=None, energy=None, xy=None ):
      super().__init__( world, xy, ident )
      self._speciesId       = speciesId
      self._generation      = 0
      self._storeCapacity   = 200000
      self._store           = energy
      self._rules           = Entity.SPECIES.species( speciesId ).rules( )
      self._birthTime       = 0
      self._mortality       = 0
      self._parentId        = None
      
      self._userDict        = { }
      Entity.SPECIES.species( speciesId ).recordBirth( self )

   def subscriptionTopics( self ):
      return [ ]

   def _addedToSimulation( self, aSimulation ):
      super()._addedToSimulation( aSimulation )
      
      self._birthTime = self._sim.simTime( )
      self._mortality = self._birthTime + Entity.BASE_MORTALITY

   def _droppedFromSimulation( self, aSimulation ):
      pass

   def handleMessage( self, aMsg ):
      pass

   def tick( self ):
      try:
         if self._mortality <= SIM.simTime():
            self._action_die( self._userDict, reason='age' )
         
         self._consumeEnergy( self._basalTickEnergy() )
         theChosenBehavior = self._chooseBehavior( )
         if theChosenBehavior is not None:
            self._realizeBehavior( theChosenBehavior )
      except Die:
         pass
   
   def report( self ):
      print( 'Entity: {0}  of species {1}, mother {2}.'.format(self._ident, self._speciesId, self._parentId) )
      print( '   Generation:  {0:6d}'.format(self._generation) )
      print( '   Birth:       {0:6d}'.format(self._birthTime)  )
      print( '   Mortality:   {0:6d}'.format(self._mortality)  )
      print( '   Cell                  Mass       Energy' )
      print( '      Rules:             {0:6d}     {1:6d}'.format(int(self._massOfRules()), int(self._massOfRules()*Entity.ENERGY_PER_MASS)) )
      print( '      Cell Body:         {0:6d}     {1:6d}'.format(int(self._massOfCellBody()), int(self._massOfCellBody()*Entity.ENERGY_PER_MASS)) )
      print( '      Stored food:       {0:6d}     {1:6d}'.format(int(self._massOfStoredEnergy()), int(self._store)) )
      print( '         Tot Mass:       {0:6d}     {1:6d}'.format(int(self._totalCellMass()), int(self._totalCellMass() * Entity.ENERGY_PER_MASS)) )
      print( '      Basal tick:                   {0:6d}'.format(int(self._basalTickEnergy())) )
      print( '  Reproduction           Mass       Energy' )
      print( '      Cost to clone                 {0:6d}'.format(int(self._costToClone())) )
      print( '      Predicted Daughter {0:6d}     {1:6d}'.format(int(self._prospectiveDaugherCellMass()), int(self._prospectiveDaugherCellMass() * Entity.ENERGY_PER_MASS)) )
      print( '      Min store needed to clone     {0:6d}'.format(int(self._minimumStoreToClone())) )

   def mass( self ):
      return self._totalCellMass()

   def _chooseBehavior( self ):
      # Identify applicable rules
      ruleSet = [ ]
      for ruleNum,rule in enumerate(self._rules):
         if (self._test(rule.intCond) and self._test(rule.extCond)):
            ruleSet.append( ruleNum )
      
      # Choose behavior
      try:
         if Entity.CHOOSE_BEHAVIOR_METHOD == 'PRIORITIZED':
            ruleNum = ruleSet[ 0 ]
         elif Entity.CHOOSE_BEHAVIOR_METHOD == 'RANDOM':
            ruleNum = choice( ruleSet )   # The entity may be failed -- having no rules
         else:
            raise Exception( )
      except:
         return
      
      return self._rules[ ruleNum ].behavior
   
   def _test( self, condition ):
      if condition == 'ANY':
         return self._test_any( self._userDict )
      if condition == 'RAND_LOW':
         return self._itest_rand_low( self._userDict )
      elif condition == 'OBJ_FOOD_N_1':
         return self._xtest_food_N_1( self._userDict )
      elif condition == 'OBJ_FOOD_S_1':
         return self._xtest_food_S_1( self._userDict )
      elif condition == 'CAN_CLONE':
         return self._itest_can_clone( self._userDict )
      elif condition == 'EMPTY_NEIGHBOR_POS':
         return self._xtest_empty_neighbor_pos( self._userDict )
      else:
         raise Exception( )
   
   def _realizeBehavior( self, behavior ):
      if behavior == 'MOVE_RAND':
         self._action_moveRandom( self._userDict )
      elif behavior == 'MOVE_LINE':
         self._action_moveLine( self._userDict )
      elif behavior == 'EAT_N':
         self._action_eat_N( self._userDict )
      elif behavior == 'EAT_S':
         self._action_eat_S( self._userDict )
      elif behavior == 'CLONE':
         self._action_clone( self._userDict )
      else:
         raise Exception( )

   def _test_any( self, userDict ):
      return True

   def _itest_rand_low( self, userDict ):
      return random() < Entity.RAND_LOW_THREASHOLD
   
   def _xtest_food_N_1( self, userDict ):
      objN = self._board.getAt( self._xy[0] - 1, self._xy[1] )
      if isinstance( objN, Food ):
         return True
   
   def _xtest_food_NE( self, userDict ):
      pass
   
   def _xtest_food_E( self, userDict ):
      pass
   
   def _xtest_food_SE( self, userDict ):
      pass
   
   def _xtest_food_S_1( self, userDict ):
      objS = self._board.getAt( self._xy[0] + 1, self._xy[1] )
      if isinstance( objS, Food ):
         return True
   
   def _xtest_food_SW( self, userDict ):
      pass
   
   def _xtest_food_W( self, userDict ):
      pass
   
   def _xtest_food_NW( self, userDict ):
      pass
   
   def _itest_can_clone( self, userDict ):
      return self._store > self._minimumStoreToClone()

   def _xtest_empty_neighbor_pos( self, userDict ):
      neighbors = self._board.allNeighborsOf( *self._xy )
      freeCellFound = False
      for direction,cell in neighbors.items():
         x, y, contents = cell
         if contents is None:
            freeCellFound = True
            break
      return freeCellFound
   
   def _action_look( self, userDict ):
      # consume the energy
      # self._consumeEnergy( 1 )  # A basic look is free of energy cost
      
      # perform the action
      world = SIM.providers( "world" )[0]
      return world.mNeighbors( self )
   
   def _action_probe( self, direction, userDict ):
      # consume the energy
      self._consumeEnergy( 1 )
      
      # perform the action
      world = SIM.providers( "world" )[0]
      return world.mLook( self, direction )
   
   def _action_moveRandom( self, userDict ):
      dirs = self._findAvailableMoveDirs_( )
      try:
         direction = choice( dirs )
      except:
         return  # No available moves
      
      self._action_move( direction, userDict )
      
      return
      # Look at the neighbors
      availableMoves = [ ]
      neighbors = self._board.allNeighborsOf( *self._xy )
      for direction,cell in neighbors.items():
         nx, ny, contents = cell
         if contents is None:
            availableMoves.append( direction )

      # perform the action
      try:
         direction = choice( availableMoves )
      except:
         return   # No available moves
      
      self._action_move( direction )

   def _findAvailableMoveDirs_( self ):
      # Look at the neighbors
      availableMoves = [ ]
      neighbors = self._board.allNeighborsOf( *self._xy )
      
      for direction,cell in neighbors.items():
         nx, ny, contents = cell
         if contents is None:
            availableMoves.append( direction )
      
      return availableMoves

   def _action_moveLine( self, userDict ):
      # Decide if we change direction
      changeDir = False
      origDirection = None
      if '_action_moveLine' not in userDict:
         changeDir = True
      else:
         origDirection = userDict[ '_action_moveLine' ]
         nx, ny, neighbor = self._board.getPosNeighbor( self._xy[0], self._xy[1], origDirection )
         if neighbor is not None:
            changeDir = True
         else:
            changeDir = (random() < 0.2)
      
      # Determine the actual direction of the next move
      if changeDir:
         dirs = self._findAvailableMoveDirs_( )
         
         try:
            dirs.remove( origDirection )
         except:
            pass
         
         if len(dirs) == 0:
            return
         
         newDirection = choice(dirs)
      else:
         newDirection = origDirection
      
      # Execute the move
      userDict[ '_action_moveLine' ] = newDirection
      self._action_move( newDirection, userDict )

   def _action_move( self, direction, userDict ):
      # Consume the energy
      energyNeeded = max(int(self._totalCellMass() * Entity.ENERGY_TO_MOVE_1_MASS), 1 )
      self._consumeEnergy( energyNeeded )

      # Perform the move
      oldxy = self._xy
      newxy = self._board.newPos( self._xy[0], self._xy[1], direction, 1 )

      self._board.setAt( self._xy[0], self._xy[1], None )
      self._xy = newxy
      self._board.setAt( self._xy[0], self._xy[1], self )
      
      self.postMessage( 'move', oldxy=oldxy, newxy=newxy, dir=direction )
   
   def _action_eat_N( self, userDict ):
      # consume the energy
      self._consumeEnergy( Entity.ENERGY_TO_EAT_1_MASS )
      
      # perform the action
      nx, ny, food = self._board.getPosNeighbor( self._xy[0], self._xy[1], 'N' )
      food_xy = (nx, ny)
      
      try:
         food.feed( who=self, amount=1 )   # take a bite
      except:
         return
      
      self._store += Entity.ENERGY_PER_MASS
      
      self._mortality += Entity.ADDITIONAL_MORTALITY_UPON_EAT
      
      self.postMessage('eat', xy=self._xy, food_xy=food_xy, dir='N')
   
   def _action_eat_S( self, userDict ):
      # consume the energy
      self._consumeEnergy( Entity.ENERGY_TO_EAT_1_MASS )
      
      # perform the action
      nx, ny, food = self._board.getPosNeighbor( self._xy[0], self._xy[1], 'S' )
      food_xy = ( nx, ny )
      
      try:
         food.feed( who=self, amount=1 )   # take a bite
      except:
         return
      
      self._store += Entity.ENERGY_PER_MASS
      
      self._mortality += Entity.ADDITIONAL_MORTALITY_UPON_EAT
      
      SIM.postMessage( Message('eat', self, self._sim.simTime(),
                               xy=self._xy, food_xy=food_xy,
                               dir='S') )
   
   def _action_clone( self, userDict ):
      # Determine where to place the daughter cell
      neighbors = self._board.allNeighborsOf( *self._xy )
      found = False
      for direction,cell in neighbors.items():
         daughterX, daughterY, contents = cell
         if contents is None:
            found = True
            break
      
      if not found:
         return
      
      # Will the daughter be mutated
      mutateDaughter = False #random() <= Entity.MUTATION_RATE
      if mutateDaughter:
         daughterRules = deepcopy( self._rules )
         
         mutationType = choice( Entity.MUTATIONS )
         
         if mutationType == 'DOUBLE RULE':
            ruleToDouble = choice( daughterRules )
            daughterRules.append( deepcopy(ruleToDouble) )
         elif mutationType == 'OMITT RULE':
            ruleToSkip = randint( 0, len(daughterRules) - 1 )
            del daughterRules[ ruleToSkip ]
         elif mutationType in [ 'CHANGE INT COND', 'CHANGE EXT COND', 'CHANGE BEHAVIOR' ]:
            ruleToMutate = randint( 0, len(daughterRules) - 1 )
            if mutationType == 'CHANGE INT COND':
               daughterRules[ ruleToMutate ].intCond = choice( Entity.INT_CONDS )
            elif mutationType == 'CHANGE EXT COND':
               daughterRules[ ruleToMutate ].extCond = choice( Entity.EXT_CONDS )
            elif mutationType == 'CHANGE BEHAVIOR':
               daughterRules[ ruleToMutate ].behavior = choice( Entity.BEHAVIORS )
         
         daughterSpeciesId = Entity.SPECIES.newSpecies( self._speciesId, daughterRules )
      
      else:
         daughterSpeciesId = self._speciesId
      
      # consume the energy
      #self.report( )
      
      costToClone          = self._costToClone()
      self._consumeEnergy( costToClone )
      
      massOfCellBody       = self._massOfCellBody()
      massOfRules          = self._massOfRules()
      massEnergyOfCellBase = (massOfCellBody + massOfRules) * Entity.ENERGY_PER_MASS
      self._consumeEnergy( massEnergyOfCellBase )
         
      # put her together
      daughter = Entity( self._board, daughterSpeciesId, energy=(self._store/2), xy=(daughterX,daughterY) )
      #daughter.report( )
      
      self._consumeEnergy( self._store/2 )
      #self.report( )
      
      # set her aloft
      SIM.add( daughter )
      
      self._mortality += Entity.ADDITIONAL_MORTALITY_UPON_CLONE
   
      self.postMessage( 'clone', xy=self._xy, dxy=(daughterX, daughterY), mutated=mutateDaughter )

   def _action_drop( self, thing, userDict ):
      self._consumeEnergy( Entity.ENERGY_TO_DROP_1_MASS )
      pass
   
   def _action_die( self, userDict, reason=None ):
      # Remove the entity model from the simulation, and free the obj
      self._board.setAt( self._xy[0], self._xy[1], None )
      self.postMessage( 'die', xy=self._xy, reason=reason )
      self._sim.drop(self)
      
      # Record the death in the SpeciesHistory
      self.SPECIES.species( self._speciesId ).recordDeath( self )
      
      # Create a food object in the entity's place of equal value
      residualMass = self._totalCellMass( ) * Entity.ENERGY_REMAINING_UPON_DEATH
      self._sim.add( Food(world, mass=residualMass, xy=self._xy) )
      
      raise Die( )

   def _consumeEnergy( self, energyUnits ):
      if energyUnits > self._store:
         self._action_die( self._userDict, reason='starvation' )
      
      self._store -= energyUnits

   def _massOfRules( self ):
      return len(self._rules) * Entity.MASS_OF_1_RULE
   
   def _massOfStoredEnergy( self ):
      return self._store / Entity.ENERGY_PER_MASS

   def _massOfCellBody( self ):
      return self._storeCapacity / 10000
   
   def _totalCellMass( self ):
      return self._massOfCellBody() + self._massOfRules() + self._massOfStoredEnergy()

   def _basalTickEnergy( self ):
      return self._totalCellMass() * Entity.ENERGY_TO_SURVIVE_1_MASS

   def _energyNeededToReproduce( self ):
      basicCellMass        = self._massOfCellBody() + self._massOfRules()
      energyToPerformClone = basicCellMass * Entity.ENERGY_TO_CLONE_1_MASS
      energyOfMother       = basicCellMass * Entity.ENERGY_PER_MASS
      return energyToPerformClone + energyOfMother + (2 * Entity.MIN_ENERGY_AFTER_CLONE)
   
   def _costToClone( self ):
      return self._totalCellMass() * Entity.ENERGY_TO_CLONE_1_MASS
   
   def _prospectiveDaugherCellMass( self ):
      baseMass = self._massOfCellBody() + self._massOfRules()
      baseMassAsEnergy = baseMass * Entity.ENERGY_PER_MASS
      mothersEnergyAfterClone = self._store - (baseMassAsEnergy + self._costToClone())
      
      daughtersStoredEnergy = mothersEnergyAfterClone / 2
      
      daughtersTotalEnergy = baseMassAsEnergy + daughtersStoredEnergy
      
      daughtersMass = daughtersTotalEnergy / Entity.ENERGY_PER_MASS
      
      return daughtersMass

   def _minimumStoreToClone( self ):
      baseMass = self._massOfCellBody() + self._massOfRules()
      baseMassAsEnergy = baseMass * Entity.ENERGY_PER_MASS
      return baseMassAsEnergy + self._costToClone() + Entity.MIN_ENERGY_AFTER_CLONE


class HeadedEntity( Entity ):
   def __init__( self, aBoard, speciesId, ident=None, parentID=None, energy=None, xy=None, heading=None ):
      super().__init__( aBoard, speciesId, ident, parentID, energy, xy )
      self._head = heading
      
      if heading is None:
         self._head = choice( World.DIRECTIONS )

   def _test( self, condition ):
      if condition == 'ANY':
         return self._test_any( self._userDict )
      if condition == 'FOOD_FORWARD':
         return self._xtest_food_forward( self._userDict )
      elif condition == 'EMPTY_FORWARD':
         return self._xtest_empty_forward( self._userDict )
      elif condition == 'EMPTY_NEIGHBOR_POS':
         return self._xtest_empty_neighbor_pos( self._userDict )
      elif condition == 'CAN_CLONE':
         return self._itest_can_clone( self._userDict )
      elif condition == 'NON_EMPTY_FORWARD':
         return self._xtest_nonEmptyForward( self._userDict )
      else:
         raise Exception( )
   
   def _realizeBehavior( self, behavior ):
      if behavior == 'EAT_FORWARD':
         self._action_eatForward( self._userDict )
      elif behavior == 'MOVE_FORWARD':
         self._action_moveForward( self._userDict )
      elif behavior == 'TURN_RIGHT':
         self._action_turnRight( self._userDict )
      elif behavior == 'TURN_LEFT':
         self._action_turnLeft( self._userDict )
      elif behavior == 'TURN_RAND':
         self._action_turnRand( self._userDict )
      elif behavior == 'CLONE':
         self._action_clone( self._userDict )
      else:
         raise Exception( )

   def _xtest_food_forward( self, userDict ):
      nx, ny, contents = self._board.getPosNeighbor( self._xy[0], self._xy[1], self._head )
      return isinstance( contents, Food )

   def _xtest_empty_forward( self, userDict ):
      nx, ny, contents = self._board.getPosNeighbor( self._xy[0], self._xy[1], self._head )
      return contents is None
   
   def _xtest_nonEmptyForward( self, userDict ):
      nx, ny, contents = self._board.getPosNeighbor( self._xy[0], self._xy[1], self._head )
      return (not isinstance(contents,Food)) and (contents is not None)
   
   def _action_moveForward( self, userDict ):
      # Consume the energy
      energyNeeded = max(int(self._totalCellMass() * Entity.ENERGY_TO_MOVE_1_MASS), 1 )
      self._consumeEnergy( energyNeeded )

      # Perform the move
      nx, ny, contents = self._board.getPosNeighbor( self._xy[0], self._xy[1], self._head )
      if contents is not None:
         return
      
      oldxy    = self._xy
      self._board.setAt( self._xy[0], self._xy[1], None )
      self._xy = (nx, ny)
      newxy    = self._xy
      self._board.setAt( self._xy[0], self._xy[1], self )
      
      self.postMessage( 'move', oldxy=oldxy, newxy=newxy, dir=self._head )

   def _action_turnRight( self, userDict ):
      # Consume the energy
      energyNeeded = max(int(self._totalCellMass() * Entity.ENERGY_TO_MOVE_1_MASS), 1 )
      self._consumeEnergy( energyNeeded )

      # Perform the move
      self._head = self._board.rightOf( self._head )
      
      self.postMessage( 'turn', direction='right', heading=self._head )
   
   def _action_turnLeft( self, userDict ):
      # Consume the energy
      energyNeeded = max(int(self._totalCellMass() * Entity.ENERGY_TO_MOVE_1_MASS), 1 )
      self._consumeEnergy( energyNeeded )

      # Perform the move
      self._head = self._board.leftOf( self._head )
      
      self.postMessage( 'turn', direction='left', heading=self._head )
   
   def _action_turnRand( self, userDict ):
      # Consume the energy
      energyNeeded = max(int(self._totalCellMass() * Entity.ENERGY_TO_MOVE_1_MASS), 1 )
      self._consumeEnergy( energyNeeded )

      # Perform the move
      turnDir = choice( [ 'right', 'left' ] )
      if turnDir == 'right':
         self._head = self._board.rightOf( self._head )
      else:
         self._head = self._board.leftOf( self._head )
      
      self.postMessage( 'turn', direction=turnDir, heading=self._head )
   
   def _action_clone( self, userDict ):
      # Determine where to place the daughter cell
      neighbors = self._board.allNeighborsOf( *self._xy )
      found = False
      for direction,cell in neighbors.items():
         daughterX, daughterY, contents = cell
         if contents is None:
            found = True
            break
      
      if not found:
         return
      
      # Will the daughter be mutated
      mutateDaughter = False #random() <= Entity.MUTATION_RATE
      if mutateDaughter:
         daughterRules = deepcopy( self._rules )
         
         mutationType = choice( Entity.MUTATIONS )
         
         if mutationType == 'DOUBLE RULE':
            ruleToDouble = choice( daughterRules )
            daughterRules.append( deepcopy(ruleToDouble) )
         elif mutationType == 'OMITT RULE':
            ruleToSkip = randint( 0, len(daughterRules) - 1 )
            del daughterRules[ ruleToSkip ]
         elif mutationType in [ 'CHANGE INT COND', 'CHANGE EXT COND', 'CHANGE BEHAVIOR' ]:
            ruleToMutate = randint( 0, len(daughterRules) - 1 )
            if mutationType == 'CHANGE INT COND':
               daughterRules[ ruleToMutate ].intCond = choice( Entity.INT_CONDS )
            elif mutationType == 'CHANGE EXT COND':
               daughterRules[ ruleToMutate ].extCond = choice( Entity.EXT_CONDS )
            elif mutationType == 'CHANGE BEHAVIOR':
               daughterRules[ ruleToMutate ].behavior = choice( Entity.BEHAVIORS )
         
         daughterSpeciesId = Entity.SPECIES.newSpecies( self._speciesId, daughterRules )
      
      else:
         daughterSpeciesId = self._speciesId
      
      # consume the energy
      #self.report( )
      
      costToClone          = self._costToClone()
      self._consumeEnergy( costToClone )
      
      massOfCellBody       = self._massOfCellBody()
      massOfRules          = self._massOfRules()
      massEnergyOfCellBase = (massOfCellBody + massOfRules) * Entity.ENERGY_PER_MASS
      self._consumeEnergy( massEnergyOfCellBase )
         
      # put her together
      daughter = HeadedEntity( self._board, daughterSpeciesId, energy=(self._store/2), xy=(daughterX,daughterY) )
      #daughter.report( )
      
      self._consumeEnergy( self._store/2 )
      #self.report( )
      
      # set her aloft
      SIM.add( daughter )
      
      self._mortality += Entity.ADDITIONAL_MORTALITY_UPON_CLONE
   
      self.postMessage( 'clone', xy=self._xy, dxy=(daughterX, daughterY), mutated=mutateDaughter )

   def _action_eatForward( self, userDict ):
      # consume the energy
      self._consumeEnergy( Entity.ENERGY_TO_EAT_1_MASS )
      
      # perform the action
      nx, ny, food = self._board.getPosNeighbor( self._xy[0], self._xy[1], self._head )
      food_xy = (nx, ny)
      
      try:
         food.feed( who=self, amount=1 )   # take a bite
      except:
         return
      
      self._store += Entity.ENERGY_PER_MASS
      
      self._mortality += Entity.ADDITIONAL_MORTALITY_UPON_EAT
      
      self.postMessage('eat', xy=self._xy, food_xy=food_xy, dir=self._head)
   

SIM = Simulation( )


world = World( 15, 15 )

logger = Monitor(world)
SIM.add( logger )

god = God( world )
SIM.add( god )

# Create Eve - our first entity
rules = [ ]
rules.append( Rule( 'ANY',       'FOOD_FORWARD',       'EAT_FORWARD'     ) )
rules.append( Rule( 'CAN_CLONE', 'EMPTY_NEIGHBOR_POS', 'CLONE'           ) )
rules.append( Rule( 'ANY',       'EMPTY_FORWARD',      'MOVE_FORWARD'    ) )
rules.append( Rule( 'ANY',       'NON_EMPTY_FORWARD',  'TURN_RIGHT'      ) )
speciesId = Entity.SPECIES.newSpecies( None, rules )

eve = HeadedEntity(world, speciesId, ident='E', energy=10000)
SIM.add( eve, xy=eve.position() )

print( '### Species Report ###' )
Entity.SPECIES.report( )

print( )
print( )
print( '### Entity Report: Eve ###' )
eve.report()

god.hornOfPlenty( 40 )

for tick in range( 3000 ):
   if Entity.SPECIES.entitiesAliveAt() == 0:
      break
   
   SIM.advanceSim( )

SIM.advanceSim( )

print( 'DONE' )