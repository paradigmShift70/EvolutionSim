import tkinter as tk


class WorldOptionsFrame( tk.LabelFrame ):
   def __init__( self, parent, *args, **opts ):
      super().__init__( parent, *args, text='World Parameters', **opts )
      
      self._rows             = tk.StringVar( )
      self._columns          = tk.StringVar( )
      
      self._buildGUI( )

   def _buildGUI( self ):
      tk.Label( self, text='Rows'    ).grid( row=1, column=1, sticky=tk.W )
      tk.Entry( self, textvariable=self._rows ).grid( row=1, column=2, sticky=tk.E, padx=2 )
      
      tk.Label( self, text='Columns' ).grid( row=2, column=1, sticky=tk.W )
      tk.Entry( self, textvariable=self._columns ).grid( row=2, column=2, sticky=tk.E, padx=2 )

   def updateInfo( self, rows, columns ):
      self._rows.set( rows )
      self._columns.set( columns )


class PlantOptionsFrame( tk.LabelFrame ):
   def __init__( self, parent, *args, **opts ):
      super().__init__( parent, *args, text='Plant Parameters', **opts )
      
      self._plant              = tk.StringVar( )  # Which plant growth algorithm
      self._maxPlantCells      = tk.StringVar( )
      self._energyPerPlantCell = tk.StringVar( )
      
      self._buildGUI( )
   
   def _buildGUI( self ):
      plantOptions = [ 'Clover', 'Sinuous' ]
      
      tk.Label( self, text='Plant'            ).grid( row=1, column=1, sticky=tk.W )
      tk.OptionMenu( self, self._plant, *plantOptions ).grid( row=1, column=2, sticky=tk.E+tk.W, padx=2 )
      
      tk.Label( self, text='Population Limit' ).grid( row=2, column=1, sticky=tk.W )
      tk.Entry( self, textvariable=self._maxPlantCells ).grid( row=2, column=2, sticky=tk.E, padx=2 )
      
      tk.Label( self, text='Energy Per Cell'  ).grid( row=3, column=1, sticky=tk.W )
      tk.Entry( self, textvariable=self._energyPerPlantCell ).grid( row=3, column=2, sticky=tk.E, padx=2 )

   def updateInfo( self, plant, popLimit, energyPerCell ):
      self._plant.set( plant )
      self._maxPlantCells.set( popLimit )
      self._energyPerPlantCell.set( energyPerCell )


class CellOptionsFrame( tk.LabelFrame ):
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

   def updateInfo( self, popLimit, costPerMove, numToStart, firstGenes, maturityAge, minEnergyToClone ):
      self._maxCells.set( popLimit )
      self._costPerMove.set( costPerMove )
      self._numStartingCells.set( numToStart )
      self._startingGenes.set( firstGenes )
      self._maturityAge.set( maturityAge )
      self._minEnergyToClone.set( minEnergyToClone )

class OptionsFrame( tk.Frame ):
   def __init__( self, parent, *args, **opts ):
      super().__init__( parent, *args, **opts )
      
      self._worldOpts = None
      self._plantOpts = None
      self._cellOpts  = None
      
      self._buildGUI( )
   
   def _buildGUI( self ):
      self._worldOpts = WorldOptionsFrame( self )
      self._worldOpts.grid( row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=4, ipadx=5, ipady=5 )
      
      self._cellOpts = CellOptionsFrame( self )
      self._cellOpts.grid( row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=4, ipadx=5, ipady=5 )
      
      self._plantOpts = PlantOptionsFrame( self )
      self._plantOpts.grid( row=3, column=1, sticky=tk.W+tk.E, padx=5, pady=4, ipadx=5, ipady=5 )

   def worldOptions( self ):
      return self._worldOpts
   
   def plantOptions( self ):
      return self._plantOpts
   
   def cellOptions( self ):
      return self._cellOpts


if __name__=='__main__':
   top = tk.Tk( )
   
   opt = OptionsFrame( top )
   opt.grid( )
   top.grid( )
   
   top.mainloop( )
