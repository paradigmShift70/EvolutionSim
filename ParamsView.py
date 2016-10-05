import tkinter as tk
import Params


class WorldParamsFrame( tk.LabelFrame ):
   def __init__( self, parent, *args, **opts ):
      super().__init__( parent, *args, text='World Parameters', **opts )
      
      self._rows             = tk.StringVar( )
      self._columns          = tk.StringVar( )
      
      self._buildGUI( )

   def _buildGUI( self ):
      tk.Label( self, text='Rows'    ).grid( row=1, column=1, sticky=tk.W )
      tk.Entry( self, textvariable=self._rows,    state='readonly' ).grid( row=1, column=2, sticky=tk.E, padx=2 )
      
      tk.Label( self, text='Columns' ).grid( row=2, column=1, sticky=tk.W )
      tk.Entry( self, textvariable=self._columns, state='readonly' ).grid( row=2, column=2, sticky=tk.E, padx=2 )

   def updateView( self ):
      self._rows.set( Params.ROWS )
      self._columns.set( Params.COLUMNS )
   
   def commit( self ):
      pass

class PlantParamsFrame( tk.LabelFrame ):
   def __init__( self, parent, *args, **opts ):
      super().__init__( parent, *args, text='Plant Parameters', **opts )
      
      self._plant              = tk.StringVar( )  # Which plant growth algorithm
      self._maxPlantCells      = tk.StringVar( )
      self._energyPerPlantCell = tk.StringVar( )
      self._randGrowthFactor   = tk.StringVar( )
      
      self._buildGUI( )
   
   def _buildGUI( self ):
      plantOptions = [ 'Geometric', 'Sinuous' ]
      
      tk.Label( self, text='Plant'            ).grid( row=1, column=1, sticky=tk.W )
      tk.OptionMenu( self, self._plant, *plantOptions ).grid( row=1, column=2, sticky=tk.E+tk.W, padx=2 )
      
      tk.Label( self, text='Population Limit' ).grid( row=2, column=1, sticky=tk.W )
      tk.Entry( self, textvariable=self._maxPlantCells ).grid( row=2, column=2, sticky=tk.E, padx=2 )
      
      tk.Label( self, text='Energy Per Cell'  ).grid( row=3, column=1, sticky=tk.W )
      tk.Entry( self, textvariable=self._energyPerPlantCell ).grid( row=3, column=2, sticky=tk.E, padx=2 )

      tk.Label( self, text='Growth Randomization Factor' ).grid( row=4, column=1, sticky=tk.W )
      tk.Entry( self, textvariable=self._randGrowthFactor ).grid( row=4, column=2, sticky=tk.E, padx=2 )

   def updateView( self ):
      self._plant.set( Params.PLANT_SPECIES )
      self._maxPlantCells.set( Params.MAX_PLANT_POPULATION )
      self._energyPerPlantCell.set( Params.ENERGY_PER_PLANT_CELL )
      self._randGrowthFactor.set( Params.RAND_GROWTH_FACTOR )

   def commit( self ):
      Params.PLANT_SPECIES         = self._plant.get()
      Params.MAX_PLANT_POPULATION  = int(self._maxPlantCells.get())
      Params.ENERGY_PER_PLANT_CELL = int(self._energyPerPlantCell.get())
      Params.RAND_GROWTH_FACTOR    = float(self._randGrowthFactor.get())


class CellParamsFrame( tk.LabelFrame ):
   def __init__( self, parent, *args, **opts ):
      super().__init__( parent, *args, text='Cell Parameters', **opts )
      
      self._maxCells         = tk.StringVar( )
      self._costPerMove      = tk.StringVar( )
      self._numStartingCells = tk.StringVar( )
      self._startingGenes    = tk.StringVar( )
      self._maturityAge      = tk.StringVar( )
      self._minEnergyToClone = tk.StringVar( )
      
      self._buildGUI( )
   
   def _buildGUI( self ):
      tk.Label( self, text='Population Limit' ).grid( row=1, column=1, sticky=tk.W )
      tk.Entry( self, textvariable=self._maxCells ).grid( row=1, column=2, sticky=tk.E, padx=2 )
      
      tk.Label( self, text='Cost Per Move'   ).grid( row=2, column=1, sticky=tk.W )
      tk.Entry( self, textvariable=self._costPerMove ).grid( row=2, column=2, sticky=tk.E, padx=2 )
      
      tk.Label( self, text='Start'   ).grid( row=3, column=1, sticky=tk.W )
      tk.Entry( self, textvariable=self._numStartingCells ).grid( row=3, column=2, sticky=tk.E, padx=2 )
      
      tk.Label( self, text='Starting Genes'  ).grid( row=4, column=1, sticky=tk.W )
      tk.Entry( self, textvariable=self._startingGenes ).grid( row=4, column=2, sticky=tk.E, padx=2 )
      
      tk.Label( self, text='Maturity Age'  ).grid( row=5, column=1, sticky=tk.W )
      tk.Entry( self, textvariable=self._maturityAge ).grid( row=5, column=2, sticky=tk.E, padx=2 )
      
      tk.Label( self, text='Energy To Clone' ).grid( row=6, column=1, sticky=tk.W )
      tk.Entry( self, textvariable=self._minEnergyToClone ).grid( row=6, column=2, sticky=tk.E, padx=2 )

   def updateView( self ):
      self._maxCells.set( Params.MAX_CELL_POPULATION )
      self._costPerMove.set( Params.ENERGY_PER_MOVE )
      self._numStartingCells.set( Params.STARTING_CELL_COUNT )
      self._startingGenes.set( Params.EVE_GENOME )
      self._maturityAge.set( Params.MATURITY )
      self._minEnergyToClone.set( Params.WELL_FED_LEVEL )

   def commit( self ):
      Params.MAX_CELL_POPULATION = int(self._maxCells.get( ))
      Params.ENERGY_PER_MOVE     = int(self._costPerMove.get( ))
      Params.STARTING_CELL_COUNT = int(self._numStartingCells.get( ))
      Params.EVE_GENOME          = self._startingGenes.get( )
      Params.MATURITY            = int(self._maturityAge.get( ))
      Params.WELL_FED_LEVEL      = int(self._minEnergyToClone.get( ))

class ParamsFrame( tk.Frame ):
   def __init__( self, parent, *args, **opts ):
      super().__init__( parent, *args, **opts )
      
      self._worldOpts = None
      self._plantOpts = None
      self._cellOpts  = None
      
      self._buildGUI( )
   
   def _buildGUI( self ):
      self._worldOpts = WorldParamsFrame( self )
      self._worldOpts.grid( row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=4, ipadx=5, ipady=5 )
      
      self._cellOpts = CellParamsFrame( self )
      self._cellOpts.grid( row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=4, ipadx=5, ipady=5 )
      
      self._plantOpts = PlantParamsFrame( self )
      self._plantOpts.grid( row=3, column=1, sticky=tk.W+tk.E, padx=5, pady=4, ipadx=5, ipady=5 )

   def updateView( self ):
      self._worldOpts.updateView( )
      self._plantOpts.updateView( )
      self._cellOpts.updateView( )

   def commit( self ):
      self._worldOpts.commit( )
      self._plantOpts.commit( )
      self._cellOpts.commit( )


if __name__=='__main__':
   top = tk.Tk( )
   
   opt = ParamsFrame( top )
   opt.grid( )
   top.grid( )
   
   top.mainloop( )
