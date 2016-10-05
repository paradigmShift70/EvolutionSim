from SimpleCellSim import *
import Params

from SimWorldView import WorldView, WorldView2
from StripChart import StripChart
from ParamsView import ParamsFrame

import tkinter as tk
import tkinter.font as tkFont

class SimulationInfoFrame( tk.LabelFrame ):
   def __init__( self, parent, *args, **opts ):
      super().__init__( parent, *args, text='Simulation State', **opts )
      
      self._popStripView = None
      self._egyStripView = None
      
      self._cellPop   = tk.StringVar( )
      self._plantPop  = tk.StringVar( )
      self._cellEgy   = tk.StringVar( )
      self._plantEgy  = tk.StringVar( )
      self._freeEgy   = tk.StringVar( )
      self._totEgy    = tk.StringVar( )
      
      self._cellPop.set( '0' )
      self._plantPop.set( '0' )
      self._cellEgy.set( '0' )
      self._plantEgy.set( '0' )
      self._freeEgy.set( '0' )
      self._totEgy.set( '0' )
      
      self._buildGUI( )

   def _buildGUI( self ):
      tk.Label( self, text='Population'   ).grid( row=1, column=2 )
      tk.Label( self, text='Energy'       ).grid( row=1, column=3 )
      tk.Label( self, text='Plant Cells'  ).grid( row=2, column=1, sticky=tk.W )
      tk.Label( self, text='Animal Cells' ).grid( row=3, column=1, sticky=tk.W )
      tk.Label( self, text='Free',        ).grid( row=4, column=1, sticky=tk.W )
      tk.Label( self, text='   Total',    ).grid( row=5, column=1, sticky=tk.W )  
      
      tk.Entry( self, justify=tk.RIGHT, textvariable=self._plantPop, width=6 ).grid( row=2, column=2, padx=2, pady=2 )
      tk.Entry( self, justify=tk.RIGHT, textvariable=self._plantEgy, width=8 ).grid( row=2, column=3, padx=2, pady=2 )
      tk.Entry( self, justify=tk.RIGHT, textvariable=self._cellPop,  width=6 ).grid( row=3, column=2, padx=2, pady=2 )
      tk.Entry( self, justify=tk.RIGHT, textvariable=self._cellEgy,  width=8 ).grid( row=3, column=3, padx=2, pady=2 )
      tk.Entry( self, justify=tk.RIGHT, textvariable=self._freeEgy,  width=8 ).grid( row=4, column=3, padx=2, pady=2 )
      tk.Entry( self, justify=tk.RIGHT, textvariable=self._totEgy,   width=8 ).grid( row=5, column=3, padx=2, pady=2 )

      self._popStripView = StripChart( self, 100, 200, { 'plant':'green', 'cell':'blue' }, borderwidth=3, relief=tk.SUNKEN )
      tk.Label( self, text='Population' ).grid( row=6, column=1 )
      self._popStripView.grid( row=7, column=1, columnspan=3 )

      tk.Label( self, text='Energy' ).grid( row=8, column=1 )
      self._egyStripView = StripChart( self, 100, 200, { 'plant':'green', 'cell':'blue', 'free':'yellow' }, borderwidth=3, relief=tk.SUNKEN )
      self._egyStripView.grid( row=9, column=1, columnspan=3 )

   def updateInfo( self, tickNum, plantPop, cellPop, cellEgy, availEgy ):
      plantEgy = plantPop * Params.ENERGY_PER_PLANT_CELL
      totEgy = plantEgy + cellEgy + availEgy
      
      self._cellPop.set( cellPop )
      self._plantPop.set( plantPop )
      self._cellEgy.set( cellEgy )
      self._plantEgy.set( plantEgy )
      self._freeEgy.set( availEgy )
      self._totEgy.set( totEgy )
      
      # Update the Strip Chart
      if tickNum % 50 == 0:
         self._popStripView.drawTick( text=str(tickNum), dash=(1,4) )
         self._egyStripView.drawTick( text=str(tickNum), dash=(1,4) )
      
      self._popStripView.plotValues( plant=plantPop // 10,  cell=cellPop // 10 )
      self._egyStripView.plotValues( plant=plantEgy // 100, cell=cellEgy // 100 )# , free=availEgy // 100 )

from chromosome import *

class SimulationControlFrame( tk.LabelFrame ):
   def __init__( self, parent, *args, resetcommand=None, pauseplaycommand=None, stepcommand=None, **opts ):
      super().__init__( parent, *args, text='Simulation Control', **opts )
      
      self._simStatus = tk.StringVar( )
      self._tick      = tk.StringVar( )
      
      self._buildGUI( resetcommand, pauseplaycommand, stepcommand )
   
   def _buildGUI( self, resetcommand, pauseplaycommand, stepcommand ):
      self._resetImg     = tk.PhotoImage( file='reset80.gif' )
      self._stepImg      = tk.PhotoImage( file='step80.gif' )
      self._pausePlayImg = tk.PhotoImage( file='togglePlayPause80.gif' )
      
      tk.Button( self, text='Reset',      compound=tk.LEFT, image=self._resetImg,     width=100, command=resetcommand ).grid( row=1, column=1 )
      tk.Button( self, text='Pause/Play', compound=tk.LEFT, image=self._pausePlayImg, width=100, command=pauseplaycommand ).grid( row=1, column=2 )
      tk.Button( self, text='Tick Once',  compound=tk.LEFT, image=self._stepImg,      width=100, command=stepcommand ).grid( row=1, column=3 )
      
      tk.Label( self, text='Status' ).grid( row=2, column=1 )
      tk.Entry( self, textvariable=self._simStatus ).grid( row=2, column=2 )
      
      tk.Label( self, text='Tick interval').grid( row=3, column=1 )
      tk.Spinbox( self, command=self._spin ).grid( row=3, column=2 )
      
      tk.Label( self, textvariable=self._tick, font=tkFont.Font(family='Helvetica', size='12', weight='bold') ).grid( row=2, column=3, rowspan=2 )

   def _spin( self ):
      pass
   
   def updateInfo( self, tickNumber ):
      self._tick.set( tickNumber )


class WorldViewDriver( World ):
   '''
     0: '#ff0000',
     1: '#ff9c00',
     2: '#ffca00',
     3: '#ffff68',
     4: '#ffffeb',
     5: '#c4ffff',
     6: '#9c34ff',
     7: '#00caff',
     8: '#009cff',
     9: '#0000ff'
     }
'''
   CELL_COLOR = {
        0: 'dark red',
        1: 'brown',
        2: 'firebrick',
        3: 'red2',
        4: 'red',
        5: 'orange red',
        6: 'dark orange',
        7: 'orange',
        8: 'gold2',
        9: 'gold',
       10: 'yellow',
       11: 'white',
       12: 'light blue',
       13: 'blue',
       14: 'blue',
       15: 'blue',
       16: 'blue',
       17: 'blue',
       18: 'blue',
       19: 'blue',
       20: 'blue',
       21: 'blue',
       22: 'blue',
       23: 'blue',
       24: 'blue',
       25: 'blue'
      }

   def __init__( self, view, rows, cols ):
      World.__init__( self, rows, cols )
      
      self._view = view

   def setAt( self, row, col, val ):
      self._locations[row][col] = val
      #World.setAt( self, row, col, val )
      
      if isinstance( val, PlantCell ):
         self._view.add( 'plant', row, col )
      elif val is not None:
         self._view.add( 'cell', row, col )

   def remove( self, row, col, val ):
      if isinstance( val, PlantCell ):
         self._view.remove( 'plant', row, col )
      elif val is not None:
         self._view.remove( 'cell', row, col )
      
      self.setAt( row, col, None )

   def moveTo( self, oldRow, oldCol, newRow, newCol ):
      self._locations[newRow][newCol] = self._locations[oldRow][oldCol]
      self._locations[oldRow][oldCol] = None
      self._view.moveTo( oldRow, oldCol, newRow, newCol )
   

class EvolutionSimGUI( tk.Frame ):
   def __init__( self, parent, *frameArgs, **frameOpts ):
      tk.Frame.__init__( self, parent, *frameArgs, **frameOpts )
      
      # Simulation Elements
      self._sim         = None
      self._world       = None
      self._plant       = None  # The Plant obj

      # GUI Components
      self._top         = parent
      self._worldView   = None
      self._simControl  = None
      self._paramsView  = None
      self._simInfoView = None
      
      self._running     = False
      
      self._buildGUI( )
      self._paramsView.updateView( )
      
      self.reset( )
   
   def _buildGUI( self ):
      self._paramsView = ParamsFrame( self )
      self._paramsView.grid( row=1, column=1, rowspan=3, sticky=tk.N+tk.S+tk.E+tk.W )

      self._worldView = WorldView2( self, Params.ROWS, Params.COLUMNS, {'cell':('8.BLOCK','blue',270), 'plant':('8.BLOCK','green',Params.MAX_PLANT_POPULATION)}, borderwidth=3, relief=tk.SUNKEN )
      self._worldView.grid( row=1, column=2, rowspan=3 )
      
      self._simControl = SimulationControlFrame( self, resetcommand=self.reset, pauseplaycommand=self.togglePausePlay, stepcommand=self.tickSimuationOnce )
      self._simControl.grid( row=1, column=3 )

      self._simInfoView = SimulationInfoFrame( self )
      self._simInfoView.grid( row=2, column=3, rowspan=2 )
   
   def reset( self ):
      self._paramsView.commit( )
      
      # Construct the objects
      self._sim = Simulation( )
      
      self._world = WorldViewDriver( self._worldView, Params.ROWS, Params.COLUMNS )
      self._worldView.reset( )
      
      # Create Eve
      Cell.POPULATION = 0
      eveRow = Params.ROWS // 2
      eveCol = Params.COLUMNS // 2
      eve = SimpleCell( self._world, [ c for c in Params.EVE_GENOME] , energy=Params.ENERGY_PER_PLANT_CELL, row=eveRow, col=eveCol )
      #subChrom = [ EatRandom_BehaviorChromosome( PlantCell ), Clone_BehaviorChromosome( ), Move_BehaviorChromosome( [ c for c in Params.EVE_GENOME] ) ]
      #masterChrom = CoordinatingChromosome( *subChrom )
      #eve = CrCell( masterChrom, self._world, energy=Params.ENERGY_PER_PLANT_CELL, row=eveRow, col=eveCol )
      self._sim.add( eve )
      
      # Create food
      Plant.AVAILABLE_ENERGY = (Params.MAX_PLANT_POPULATION * Params.ENERGY_PER_PLANT_CELL) - (2 * Params.ENERGY_PER_PLANT_CELL)
      if Params.PLANT_SPECIES == 'Geometric':
         self._plant = Plant_A( self._world, Params.MAX_PLANT_POPULATION, Params.ENERGY_PER_PLANT_CELL, Params.RAND_GROWTH_FACTOR )
      elif Params.PLANT_SPECIES == 'Sinuous':
         self._plant = Plant_D( self._world, Params.MAX_PLANT_POPULATION, Params.ENERGY_PER_PLANT_CELL, Params.RAND_GROWTH_FACTOR )
      self._plant.startPlant( eveRow + 1, eveRow )
      self._sim.add( self._plant )
      
      self._running = False
   
   def pause( self ):
      self._running = False
   
   def play( self ):
      self._running = True
      self._top.after( Params.TICK_LENGTH, self._tickSimulation )
   
   def togglePausePlay( self ):
      self._running = (not self._running)
      if self._running:
         self._top.after( Params.TICK_LENGTH, self._tickSimulation )

   def tickSimuationOnce( self ):
      self._running = False
      self._top.after( Params.TICK_LENGTH, self._tickSimulation )

   def updateAllInfoViews( self ):
      simTime = self._sim.simTime( )
      
      # Sim Info
      plantPop = self._plant.size()
      #cellEgy  = 0

      #for model in self._sim:
         #try:
            #cellEgy += model.storedEnergy()
         #except:
            #pass   # <-- model is not a Cell
      
      cellEgy = ((Params.MAX_PLANT_POPULATION - plantPop) * Params.ENERGY_PER_PLANT_CELL) - Plant.AVAILABLE_ENERGY
      self._simInfoView.updateInfo( simTime, plantPop, Cell.POPULATION, cellEgy, Plant.AVAILABLE_ENERGY )#availEgy )
      
      # Simulation Control
      self._simControl.updateInfo( simTime )
      
      self._running = (Cell.POPULATION > 0) and (self._running)

   def _tickSimulation( self ):
      self._sim.tickAllModelsOnce_NoMessaging( )
      
      #simTime = self._sim.simTime()
      #print( simTime )
      #if (self._sim.size() == 1) or (simTime == 100000):
         #print( 'R', Cell.R_tracker )
         #print( 'N', Cell.N_tracker )
         #quit( )
      self.updateAllInfoViews()
      
      if self._running:
         self._top.after( Params.TICK_LENGTH, self._tickSimulation )


def runSim( ):
   top = tk.Tk( )
   top.title( 'SELF - Simulated Evolving Life Form' )
   gui = EvolutionSimGUI( top )
   gui.grid( )
   top.mainloop( )

runSim( )




import random

class SimpleCellWorldViewProfiler( World ):
   def __init__( self, parent, rows, cols ):
      World.__init__( self, rows, cols )
      
      self._view = WorldView2( parent, rows, cols, {'cell':('8.BLOCK','blue',200), 'plant':('8.BLOCK','green',400)} )
      self._view.grid( )
   
   def setAt( self, row, col, val ):
      self._locations[row][col] = val
      
      if isinstance( val, PlantCell ):
         self._view.add( 'plant', row, col )
      elif isinstance( val, Cell ):
         self._view.add( 'cell', row, col )

   def remove( self, row, col, val ):
      if isinstance( val, PlantCell ):
         self._view.remove( 'plant', row, col )
      elif isinstance( val, Cell ):
         self._view.remove( 'cell', row, col )
      
      self.setAt( row, col, None )

   def moveTo( self, oldRow, oldCol, newRow, newCol ):
      self._locations[newRow][newCol] = self._locations[oldRow][oldCol]
      self._locations[oldRow][oldCol] = None
      self._view.moveTo( oldRow, oldCol, newRow, newCol )

def profileSim( showView=True ):
   global top, sim, world, tickCount
   
   Params.ROWS = 40
   Params.COLUMNS = 40
   Params.MAX_PLANT_POPULATION = 400
   
   random.seed( 1 )
   
   top = tk.Tk( )
   
   sim = Simulation( )
   
   # Create the View
   if showView:
      world = SimpleCellWorldViewProfiler( top, Params.ROWS, Params.COLUMNS )
   else:
      world = World( Params.ROWS, Params.COLUMNS )
   
   # Create Eve
   eveRow = Params.ROWS // 2
   eveCol = Params.COLUMNS // 2
   #eve = SimpleCell( world, [ c for c in Params.EVE_GENOME], energy=Params.ENERGY_PER_PLANT_CELL, row=eveRow, col=eveCol )
   subChrom = [ EatRandom_BehaviorChromosome( PlantCell ), Clone_BehaviorChromosome( ), Move_BehaviorChromosome( [ c for c in Params.EVE_GENOME] ) ]
   masterChrom = CoordinatingChromosome( *subChrom )
   eve = CrCell( masterChrom, world, energy=Params.ENERGY_PER_PLANT_CELL, row=eveRow, col=eveCol )
   sim.add( eve )
   
   # Create food
   Plant.AVAILABLE_ENERGY = (Params.MAX_PLANT_POPULATION * Params.ENERGY_PER_PLANT_CELL) - (2 * Params.ENERGY_PER_PLANT_CELL)
   thePlant = Plant_C( world, Params.MAX_PLANT_POPULATION, Params.ENERGY_PER_PLANT_CELL, Params.RAND_GROWTH_FACTOR )
   thePlant.startPlant( eveRow, eveCol + 1 )
   sim.add( thePlant )

   count = 1
   def tickSim( ):
      global sim, top
      nonlocal count
      
      sim.tickAllModelsOnce_NoMessaging()
      
      if count >= 1000:
         top.quit()
      
      count += 1
      top.after( Params.TICK_LENGTH, tickSim )

   top.after( Params.TICK_LENGTH, tickSim )
   
   top.mainloop( )


import timeit
import profile   
profile.Profile.bias = 1.21e-6
#profileSim( showView=True )
#print( timeit.timeit( 'profileSim( showView=True )', 'from __main__ import profileSim', number=1 ) )
#profile.run( 'profileSim( showView=True )' )
#print( timeit.timeit( 'profileSim( showView=False )', 'from __main__ import profileSim', number=1 ) )
#profile.run( 'profileSim( showView=False )' )
