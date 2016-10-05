import tkinter as tk

x11_BMP_TEMPLATE = '''
#define im_width {0}
#define im_height {1}
static char im_bits[] = {{
{2} 
}};
'''

def _bmp( size, pixels ):
   return x11_BMP_TEMPLATE.format( size, size, pixels )

SHAPE = {
'4.SQUARE'  : _bmp(4, '0x0F,0x09,0x09,0x0F'),
'4.BLOCK'   : _bmp(4, '0x0F,0x0F,0x0F,0x0F'),
'4.CIRCLE'  : _bmp(4, '0x06,0x09,0x09,0x06'),
'4.BALL'    : _bmp(4, '0x06,0x0F,0x0F,0x06'),
'4.EX'      : _bmp(4, '0x06,0x0F,0x0F,0x06'),
'4.DOT'     : _bmp(4, '0x00,0x06,0x06,0x00'),
'4.CHECKER' : _bmp(4, '0x05,0x0A,0x05,0x0A'),
'8.SQUARE'  : _bmp(8, '0xFF,0x81,0x81,0x81,0x81,0x81,0x81,0xFF'),
'8.SQUARE_T': _bmp(8, '0xFF,0xFF,0xFF,0xE7,0xE7,0xFF,0xFF,0xFF'), # thick
'8.BLOCK'   : _bmp(8, '0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF'),
'8.BLOCK_S' : _bmp(8, '0x00,0x7E,0x7E,0x7E,0x7E,0x7E,0x7E,0x00'), # small
'8.CIRCLE'  : _bmp(8, '0x18,0x42,0x42,0x81,0x81,0x42,0x42,0x18'),
'8.CIRCLE_T': _bmp(8, '0x18,0x7E,0x7E,0xE7,0xE7,0x7E,0x7E,0x18'), # thick
'8.BALL'    : _bmp(8, '0x18,0x7E,0x7E,0xFF,0xFF,0x7E,0x7E,0x18'),
'8.CHECKER' : _bmp(8, '0x55,0xAA,0x55,0xAA,0x55,0xAA,0x55,0xAA')
}


class WorldView( tk.Frame ):
   CELL_SIZE = 9
   BACKGROUND = 'black'
   
   def __init__( self, parent, numRows=10, numCols=10, shape=SHAPE['8.BLOCK'], **opts ):
      super().__init__( parent, **opts )
      height = numRows*WorldView.CELL_SIZE + 5
      width  = numCols*WorldView.CELL_SIZE + 5
      
      self._numRows = numRows
      self._numCols = numCols
      self._canvas = tk.Canvas( self, height=height, width=width, background=WorldView.BACKGROUND )
      self._cells = [ ]
      for rowNum in range(numRows):
         newRow = [ ]
         for colNum in range(numCols):
            xPos = (rowNum + 1) * WorldView.CELL_SIZE
            yPos = (colNum + 1) * WorldView.CELL_SIZE
            imgObj = tk.BitmapImage( data=shape, foreground=WorldView.BACKGROUND, background=WorldView.BACKGROUND )
            canvasId = self._canvas.create_image( yPos, xPos, image=imgObj )
            newRow.append( imgObj )
         self._cells.append( newRow )

   def pack( self, **opts ):
      self._canvas.pack( )
      super().pack( **opts )

   def grid( self, **opts ):
      self._canvas.grid( )
      super().grid( **opts )

   def getCellColor( self, row, col ):
      return self._cells[row][col].cget( 'foreground' )
   
   def setCellColor( self, row, col, color ):
      self._cells[row][col].config( foreground=color )
   
   def clearCellColor( self, row, col ):
      return self.setCellColor(row,col,WorldView.BACKGROUND) == WorldView.BACKGROUND
   
   def setAll( self, color=None ):
      if color is None:
         color = WorldView.BACKGROUND
      
      for row in self._cells:
         for imgObj in row:
            imgObj.config( foreground=color )

   def setMulti( self, changes ):
      '''Apply all changes specified by the arguments.
      changes is an iterable returning pairs: (x,y), color.'''
      for coords, color in changes:
         row,col = coords
         self._cells[row][col].config( foreground=color )

class WorldView2( tk.Frame ):
   CELL_SIZE = 9
   BACKGROUND = 'black'
   
   def __init__( self, parent, numRows=10, numCols=10, objDefs=None, **opts ):
      '''objs should be a dict Mapping:   'name' -> (shape, color, maxNumber)'''
      super().__init__( parent, **opts )
      height = numRows*WorldView2.CELL_SIZE + 5
      width  = numCols*WorldView2.CELL_SIZE + 5
      
      self._numRows = numRows
      self._numCols = numCols
      self._objDefs = objDefs
      
      self._canvas     = tk.Canvas( self, height=height, width=width, background=WorldView2.BACKGROUND )
      self._imgs       = None  # list of tk resource object refs - held to prevent garbage collection
      self._cells      = None  # 2D grid (numRows x numCols) of: imageId or None
      self._unusedObjs = None  # Map: 'name' -> [ imgId ]
      
      self._init( )

   def pack( self, **opts ):
      self._canvas.pack( )
      super().pack( **opts )

   def grid( self, **opts ):
      self._canvas.grid( )
      super().grid( **opts )

   def add( self, name, row, col ):
      if self._cells[row][col] is not None:
         raise Exception( )
      
      imgId = self._unusedObjs[ name ].pop( )
      self._cells[row][col] = imgId
      self._canvas.move( imgId, (col+1) * WorldView2.CELL_SIZE, (row+1) * WorldView2.CELL_SIZE )

   def remove( self, name, row, col ):
      imgId = self._cells[row][col]
      self._cells[row][col] = None
      self._unusedObjs[ name ].append( imgId )
      self._canvas.move(imgId, -((col+1) * WorldView2.CELL_SIZE), -((row+1) * WorldView2.CELL_SIZE) )

   def moveTo( self, oldRow, oldCol, newRow, newCol ):
      if self._cells[newRow][newCol] is not None:
         raise Exception( )
      
      imgId = self._cells[oldRow][oldCol]
      self._cells[oldRow][oldCol] = None
      self._cells[newRow][newCol] = imgId
      self._canvas.move(imgId, (newCol-oldCol) * WorldView2.CELL_SIZE, (newRow-oldRow) * WorldView2.CELL_SIZE )
   
   def reset( self ):
      objs = [ ]
      for row in self._cells:
         for col in row:
            if col is not None:
               objs.append( col )
      
      self._canvas.delete( objs )
      
      for vals in self._unusedObjs.values():
         self._canvas.delete( *vals )
      
      self._init( )
   
   def _init( self ):
      self._imgs       = [ ]
      self._cells      = [ [ None for col in range(self._numCols) ] for row in range(self._numRows) ]
      self._unusedObjs = { }
      
      for name,spec in self._objDefs.items():
         shape, color, maxNumber = spec
         store = [ ]
         for ct in range(maxNumber):
            imgObj = tk.BitmapImage( data=SHAPE[shape], foreground=color, background=WorldView2.BACKGROUND )
            self._imgs.append( imgObj )
            imgId = self._canvas.create_image( 0, 0, image=imgObj )
            store.append( imgId )
         self._unusedObjs[ name ] = store

if __name__ == '__main__':
   top = tk.Tk()
   m   = WorldView2( top, 20, 20, {'cell':('8.BLOCK','blue',15)} )
   m.grid( )
   print( len(m._unusedObjs['cell']) )
   
   m.add( 'cell', 0, 0 )
   m.add( 'cell', 0, 1 )
   m.add( 'cell', 9, 9 )
   m.add( 'cell', 5, 5 )
   m.add( 'cell', 4, 4 )
   m.add( 'cell', 4, 5 )
   m.add( 'cell', 4, 6 )
   m.add( 'cell', 5, 4 )
   m.add( 'cell', 5, 6 )
   m.add( 'cell', 6, 4 )
   m.add( 'cell', 6, 5 )
   m.add( 'cell', 6, 6 )
   
   iteration = 1
   
   def moveCell( ):
      global iteration
      
      if iteration == 1:
         m.moveTo( 9, 9, 10, 9 )
      elif iteration == 2:
         m.moveTo( 6, 6, 7, 6 )
      elif iteration == 3:
         m.moveTo( 6, 5, 7, 5 )
      elif iteration == 4:
         m.moveTo( 6, 4, 7, 4 )
      elif iteration == 5:
         m.moveTo( 5, 6, 6, 6 )
      elif iteration == 6:
         m.moveTo( 5, 5, 6, 5 )
      elif iteration == 7:
         m.moveTo( 5, 4, 6, 4 )
      elif iteration == 8:
         m.moveTo( 4, 6, 5, 6 )
      elif iteration == 9:
         m.moveTo( 4, 5, 5, 5 )
      elif iteration == 10:
         m.moveTo( 4, 4, 5, 4 )
      elif iteration == 11:
         m.moveTo( 0, 1, 1, 1 )
      elif iteration == 12:
         m.moveTo( 0, 0, 1, 0 )
      
      elif iteration == 13:
         m.remove( 'cell', 10, 9 )
      elif iteration == 14:
         m.remove( 'cell', 7, 6 )
      elif iteration == 15:
         m.remove( 'cell', 7, 5 )
      elif iteration == 16:
         m.remove( 'cell', 7, 4 )
      elif iteration == 17:
         m.remove( 'cell', 6, 6 )
      elif iteration == 18:
         m.remove( 'cell', 6, 5 )
      elif iteration == 19:
         m.remove( 'cell', 6, 4 )
      elif iteration == 20:
         m.remove( 'cell', 5, 6 )
      elif iteration == 21:
         m.remove( 'cell', 5, 5 )
      elif iteration == 22:
         m.remove( 'cell', 5, 4 )
      elif iteration == 23:
         m.remove( 'cell', 1, 1 )
      elif iteration == 24:
         m.remove( 'cell', 1, 0 )
      elif iteration == 25:
         top.quit( )
      
      print( len(m._unusedObjs['cell']) )
      
      iteration += 1
      top.after( 100, moveCell )
   
   print( len(m._unusedObjs['cell']) )
   top.after( 100, moveCell )
   top.mainloop()

