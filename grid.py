class Slot( object ):
   def __init__( self, row, col, content=None, contentType=0 ):
      self.content     = content
      self.contentType = contentType
      
      self.row         = row   # Location of this slot
      self.col         = col
      
      self.vNeighbors  = { }   # Von Neumann Neighbors - Map: dirString -> Slot
      self.mNeighbors  = { }   # Moore Neighbors -       Map: dirString -> Slot
         # References to the neighboring slots in the Grid.
         # The row, col, vNeighbors and mNeighbors values are set when the
         # Grid is constructed.  They should remain unmodified for the life of
         # The Slot instance.  The content and contentType members may be 
         # modified at will.

   def emptyVNeighbors( self ):
      result = { }
      for dirStr,slot in self.vNeighbors.items():
         if slot.contentType == 0:
            result[ dirStr ] = slot
      return result
   
   def emptyMNeighbors( self, row, col ):
      result = { }
      for dirStr,slot in self.mNeighbors.items():
         if slot.contentType == 0:
            result[ dirStr ] = slot
      return result
   
   def vNeighborsOfType( self, row, col, aType ):
      result = { }
      for dirStr,slot in self.vNeighbors.items():
         if slot.contentType == aType:
            result[ dirStr ] = slot
      return result
   
   def mNeighborsOfType( self, row, col, aType ):
      result = { }
      for dirStr,slot in self.mNeighbors.items():
         if slot.contentType == aType:
            result[ dirStr ] = slot
      return result


class PeriodicGrid( object ):
   DELTAS = {
      'NW': (-1, -1),
      'N':  (-1,  0),
      'NE': (-1,  1),
      'W':  ( 0, -1),
      'E':  ( 0,  1),
      'SW': ( 1, -1),
      'S':  ( 1,  0),
      'SE': ( 1,  1)
      }

   def __init__( self, numRows, numCols ):
      self._numRows = numRows
      self._numCols = numCols
      
      self._slots   = [ [ Slot(r,c) for c in range(numCols) ] for r in range(numRows) ]
      
      for r in range(numRows):
         for c in range(numCols):
            vneighbors = self._slots[r][c].vNeighbors
            mneighbors = self._slots[r][c].mNeighbors
            for dirStr,deltas in Grid.DELTAS.items():
               dRow,dCol = deltas
               nRow,nCol = (r+dRow) % numRows, (c+dCol) % numCols
               mneighbors[ dirStr ] = self._slots[nRow][nCol]
               if dirStr in [ 'N', 'E', 'S', 'W' ]:
                  vneighbors[ dirStr ] = self._slots[nRow][nCol]
   
   def at( self, row, col ):
      return self._slots[row][col]
   
   def setAt( self, row, col, content, contentType=0 ):
      slot = self._slots[row][col]
      slot.content     = content
      slot.contentType = contentType

   def getSlotAt( self, row, col ):
      return self._slots[row][col]
   
   def getObjAt( self, row, col ):
      return self._slots[row][col].content


class FlatGrid( object ):
   DELTAS = {
      'NW': (-1, -1),
      'N':  (-1,  0),
      'NE': (-1,  1),
      'W':  ( 0, -1),
      'E':  ( 0,  1),
      'SW': ( 1, -1),
      'S':  ( 1,  0),
      'SE': ( 1,  1)
      }

   def __init__( self, numRows, numCols, borderCondition=None ):
      self._numRows = numRows
      self._numCols = numCols
      self._edge    = borderCondition
      
      self._slots   = [ [ Slot(r,c) for c in range(numCols) ] for r in range(numRows) ]
      
      for r in range(numRows):
         for c in range(numCols):
            vneighbors = self._slots[r][c].vNeighbors
            mneighbors = self._slots[r][c].mNeighbors
            for dirStr,deltas in FlatGrid.DELTAS.items():
               dRow,dCol = deltas
               nRow,nCol = r+dRow, c+dCol
               try:
                  mneighbors[ dirStr ] = self._slots[nRow][nCol]
                  if dirStr in [ 'N', 'E', 'S', 'W' ]:
                     vneighbors[ dirStr ] = self._slots[nRow][nCol]
               except:
                  if self._edge is not None:
                     mneighbors[ dirStr ] = Slot(-1,-1,self._edge)
                     if dirStr in [ 'N', 'E', 'S', 'W' ]:
                        vneighbors[ dirStr ] = Slot(-1,-1,self._edge)

   
   def at( self, row, col ):
      return self._slots[row][col]
   
   def setAt( self, row, col, content, contentType=0 ):
      slot = self._slots[row][col]
      slot.content     = content
      slot.contentType = contentType

   def getSlotAt( self, row, col ):
      return self._slots[row][col]
   
   def getObjAt( self, row, col ):
      return self._slots[row][col].content


class CA( object ):
   def __init__( self, numRows, numCols, borderCondition=None ):
      self._numRows = numRows
      self._numCols = numCols
      
      self._current   = FlatGrid( numRows, numCols, borderCondition )
      self._next      = FlatGrid( numRows, numCols, borderCondition )
      
      for r in range(numRows):
         for c in range(numCols):
            self._current.setAt( r, c, 0, 1 )
            self._next.setAt( r, c, 0, 1 )

   def at( self, row, col ):
      return self._current.at( row, col )
   
   def setNext( self, row, col, content, contentType=0 ):
      self._next.setAt( row, col, content, contentType )

   def endTurn( self ):
      temp = self._current
      self._current = self._next
      self._next = temp

   def diag( self ):
      for r in range(self._numRows):
         line = ''
         for c in range(self._numCols):
            slot = self._current.at(r,c)
            if slot.content == 1:
               line += '#'
            else:
               line += '.'
         print( line )

   def tick( self ):
      self.diag( )
      
      for r in range(self._numRows):
         for c in range(self._numCols):
            nextVal = self._nextState( self._current.at(r,c) )
            self.setNext( r, c, nextVal )
      
      self.endTurn( )

   def _nextState( self, slot ):
      raise NotImplementedError( )


class LF( CA ):
   def __init__( self, numRows, numCols ):
      CA.__init__( self, numRows, numCols )
   
   def set( self, row, col, val=1 ):
      self.at( row, col ).content = val
   
   def _nextState( self, slot ):
      numNeighbors = 0
      for nSlot in slot.mNeighbors.values():
         numNeighbors += nSlot.content
      
      if numNeighbors <= 1:
         return 0
      elif numNeighbors == 2:
         return slot.content
      elif numNeighbors == 3:
         return 1
      elif numNeighbors >= 4:
         return 0


class WW( CA ):
   ''' +1 head
       -1 tail
       10 wire
       nn anything else
   '''
   def __init__( self, numRows, numCols ):
      CA.__init__( self, numRows, numCols )
   
   def set( self, row, col, val=1 ):
      self.at( row, col ).content = val
   
   def _nextState( self, slot ):
      nbrTypes = { 0:0, 1:0, -1:0, 10:0 }
      for nSlot in slot.mNeighbors.values():
         try:
            nbrTypes[nSlot.content] += 1
         except:
            pass
      
      if (slot.content == 10) and (1 <= nbrTypes[1] <= 2):
         return 1
      elif (slot.content == 1):
         return -1
      elif (slot.content == -1):
         return 10
      else:
         return slot.content

   def diag( self ):
      for r in range(self._numRows):
         line = ''
         for c in range(self._numCols):
            slot = self._current.at(r,c)
            if slot.content == 0:
               line += '.'
            elif slot.content == 1:
               line += '@'
            elif slot.content == -1:
               line += 'o'
            elif slot.content == 10:
               line += '+'
         print( line )


class LL( CA ):
   RULE = {
      '00000':0,
      '00001':2,
      '00002':0,
      '00003':0,
      '00005':0,
      '00006':3,
      '00007':1,
      '00011':2,
      '00012':2,
      '00013':2,
      '00021':2,
      '00022':0,
      '00023':0,
      '00026':2,
      '00027':2,
      '00032':0,
      '00052':5,
      '00062':2,
      '00072':2,
      '00102':2,
      '00112':0,
      '00202':0,
      '00203':0,
      '00205':0,
      '00212':5,
      '00222':0,
      '00232':2,
      '00522':2,
      '01232':1,
      '01242':1,
      '01252':5,
      '01262':1,
      '01272':1,
      '01275':1,
      '01422':1,
      '01432':1,
      '01442':1,
      '01472':1,
      '01625':1,
      '01722':1,
      '01725':5,
      '01752':1,
      '01762':1,
      '01772':1,
      '02527':1,
      '10001':1,
      '10006':1,
      '10007':7,
      '10011':1,
      '10012':1,
      '10021':1,
      '10024':4,
      '10027':7,
      '10051':1,
      '10101':1,
      '10111':1,
      '10124':4,
      '10127':7,
      '10202':6,
      '10212':1,
      '10221':1,
      '10224':4,
      '10226':3,
      '10227':7,
      '10232':7,
      '10242':4,
      '10262':6,
      '10264':4,
      '10267':7,
      '10271':0,
      '10272':7,
      '10542':7,
      '11112':1,
      '11122':1,
      '11124':4,
      '11125':1,
      '11126':1,
      '11127':7,
      '11152':2,
      '11212':1,
      '11222':1,
      '11224':4,
      '11225':1,
      '11227':7,
      '11232':1,
      '11242':4,
      '11262':1,
      '11272':7,
      '11322':1,
      '12224':4,
      '12227':7,
      '12243':4,
      '12254':7,
      '12324':4,
      '12327':7,
      '12425':5,
      '12426':7,
      '12527':5,
      '20001':2,
      '20002':2,
      '20004':2,
      '20007':1,
      '20012':2,
      '20015':2,
      '20021':2,
      '20022':2,
      '20023':2,
      '20024':2,
      '20025':0,
      '20026':2,
      '20027':2,
      '20032':6,
      '20042':3,
      '20051':7,
      '20052':2,
      '20057':5,
      '20072':2,
      '20102':2,
      '20112':2,
      '20122':2,
      '20142':2,
      '20172':2,
      '20202':2,
      '20203':2,
      '20205':2,
      '20207':3,
      '20212':2,
      '20215':2,
      '20221':2,
      '20222':2,
      '20227':2,
      '20232':1,
      '20242':2,
      '20245':2,
      '20252':0,
      '20255':2,
      '20262':2,
      '20272':2,
      '20312':2,
      '20321':6,
      '20322':6,
      '20342':2,
      '20422':2,
      '20512':2,
      '20521':2,
      '20522':2,
      '20552':1,
      '20572':5,
      '20622':2,
      '20672':2,
      '20712':2,
      '20722':2,
      '20742':2,
      '20772':2,
      '21122':2,
      '21126':1,
      '21222':2,
      '21224':2,
      '21226':2,
      '21227':2,
      '21422':2,
      '21522':2,
      '21622':2,
      '21722':2,
      '22227':2,
      '22244':2,
      '22246':2,
      '22276':2,
      '22277':2,
      '30001':3,
      '30002':2,
      '30004':1,
      '30007':6,
      '30012':3,
      '30042':1,
      '30062':2,
      '30102':1,
      '30122':0,
      '30251':1,
      '40112':0,
      '40122':0,
      '40125':0,
      '40212':0,
      '40222':1,
      '40232':6,
      '40252':0,
      '40322':1,
      '50002':2,
      '50021':5,
      '50022':5,
      '50023':2,
      '50027':2,
      '50052':0,
      '50202':2,
      '50212':2,
      '50215':2,
      '50222':0,
      '50224':4,
      '50272':2,
      '51212':2,
      '51222':0,
      '51242':2,
      '51272':2,
      '60001':1,
      '60002':1,
      '60212':0,
      '61212':5,
      '61213':1,
      '61222':5,
      '70007':7,
      '70112':0,
      '70122':0,
      '70125':0,
      '70212':0,
      '70222':1,
      '70225':1,
      '70232':1,
      '70252':5,
      '70272':0      
   }
   def __init__( self, numRows, numCols ):
      CA.__init__( self, numRows, numCols, borderCondition=0 )
      
      rotations = { }
      for key,val in LL.RULE.items():
         state,neighbors = key[0],key[1:]
         for ct in range(3):
            neighbors = neighbors[1:] + neighbors[0]
            newKey = state + neighbors
            rotations[ newKey ] = val
      LL.RULE.update( rotations )
   
   def set( self, row, col, val=1 ):
      self.at( row, col ).content = val
   
   def _nextState( self, slot ):
      vn = slot.vNeighbors
      key = ''.join( (str(slot.content), str(vn['N'].content), str(vn['E'].content),
                                         str(vn['S'].content), str(vn['W'].content)) )
      return LL.RULE[ key ]

   def diag( self ):
      for r in range(self._numRows):
         line = ''
         for c in range(self._numCols):
            state = self._current.at(r,c).content
            if state == 0:
               line += '.'
            elif state == 1:
               line += '-'
            elif state == 2:
               line += '#'
            elif state == 3:
               line += '3'
            elif state == 4:
               line += '4'
            elif state == 5:
               line += '5'
            elif state == 6:
               line += '6'
            elif state == 7:
               line += '7'
         
         print( line )


from timeit import timeit

if __name__ == '__main__':
   
   #ca = LF( 10, 10 )
   #ca.set( 3, 3, 1 )
   #ca.set( 3, 4, 1 )
   #ca.set( 3, 5, 1 )

   #ca = WW( 10, 10 )
   #ca.set( 1, 2, -1 )
   #ca.set( 1, 3,  1 )
   #ca.set( 1, 4, 10 )
   #ca.set( 2, 1, 10 )
   #ca.set( 2, 5, 10 )
   #ca.set( 2, 6, 10 )
   #ca.set( 2, 7, 10 )
   #ca.set( 2, 8, 10 )
   #ca.set( 2, 9, 10 )
   #ca.set( 3, 2, 10 )
   #ca.set( 3, 3, 10 )
   #ca.set( 3, 4, 10 )

   ca = LL( 200, 200 )
   ca.set( 100, 101, 2 )
   ca.set( 100, 102, 2 )
   ca.set( 100, 103, 2 )
   ca.set( 100, 104, 2 )
   ca.set( 100, 105, 2 )
   ca.set( 100, 106, 2 )
   ca.set( 100, 107, 2 )
   ca.set( 100, 108, 2 )
   
   ca.set( 101, 100, 2 )
   ca.set( 101, 101, 1 )
   ca.set( 101, 102, 7 )
   ca.set( 101, 103, 0 )
   ca.set( 101, 104, 1 )
   ca.set( 101, 105, 4 )
   ca.set( 101, 106, 0 )
   ca.set( 101, 107, 1 )
   ca.set( 101, 108, 4 )
   ca.set( 101, 109, 2 )
   
   ca.set( 102, 100, 2 )
   ca.set( 102, 101, 0 )
   ca.set( 102, 102, 2 )
   ca.set( 102, 103, 2 )
   ca.set( 102, 104, 2 )
   ca.set( 102, 105, 2 )
   ca.set( 102, 106, 2 )
   ca.set( 102, 107, 2 )
   ca.set( 102, 108, 0 )
   ca.set( 102, 109, 2 )
   
   ca.set( 103, 100, 2 )
   ca.set( 103, 101, 7 )
   ca.set( 103, 102, 2 )
   ca.set( 103, 103, 0 )
   ca.set( 103, 104, 0 )
   ca.set( 103, 105, 0 )
   ca.set( 103, 106, 0 )
   ca.set( 103, 107, 2 )
   ca.set( 103, 108, 1 )
   ca.set( 103, 109, 2 )

   ca.set( 104, 100, 2 )
   ca.set( 104, 101, 1 )
   ca.set( 104, 102, 2 )
   ca.set( 104, 103, 0 )
   ca.set( 104, 104, 0 )
   ca.set( 104, 105, 0 )
   ca.set( 104, 106, 0 )
   ca.set( 104, 107, 2 )
   ca.set( 104, 108, 1 )
   ca.set( 104, 109, 2 )

   ca.set( 105, 100, 2 )
   ca.set( 105, 101, 0 )
   ca.set( 105, 102, 2 )
   ca.set( 105, 103, 0 )
   ca.set( 105, 104, 0 )
   ca.set( 105, 105, 0 )
   ca.set( 105, 106, 0 )
   ca.set( 105, 107, 2 )
   ca.set( 105, 108, 1 )
   ca.set( 105, 109, 2 )

   ca.set( 106, 100, 2 )
   ca.set( 106, 101, 7 )
   ca.set( 106, 102, 2 )
   ca.set( 106, 103, 0 )
   ca.set( 106, 104, 0 )
   ca.set( 106, 105, 0 )
   ca.set( 106, 106, 0 )
   ca.set( 106, 107, 2 )
   ca.set( 106, 108, 1 )
   ca.set( 106, 109, 2 )

   ca.set( 107, 100, 2 )
   ca.set( 107, 101, 1 )
   ca.set( 107, 102, 2 )
   ca.set( 107, 103, 2 )
   ca.set( 107, 104, 2 )
   ca.set( 107, 105, 2 )
   ca.set( 107, 106, 2 )
   ca.set( 107, 107, 2 )
   ca.set( 107, 108, 1 )
   ca.set( 107, 109, 2 )
   ca.set( 107, 110, 2 )
   ca.set( 107, 111, 2 )
   ca.set( 107, 112, 2 )
   ca.set( 107, 113, 2 )

   ca.set( 108, 100, 2 )
   ca.set( 108, 101, 0 )
   ca.set( 108, 102, 7 )
   ca.set( 108, 103, 1 )
   ca.set( 108, 104, 0 )
   ca.set( 108, 105, 7 )
   ca.set( 108, 106, 1 )
   ca.set( 108, 107, 0 )
   ca.set( 108, 108, 7 )
   ca.set( 108, 109, 1 )
   ca.set( 108, 110, 1 )
   ca.set( 108, 111, 1 )
   ca.set( 108, 112, 1 )
   ca.set( 108, 113, 1 )
   ca.set( 108, 114, 2 )

   ca.set( 109, 101, 2 )
   ca.set( 109, 102, 2 )
   ca.set( 109, 103, 2 )
   ca.set( 109, 104, 2 )
   ca.set( 109, 105, 2 )
   ca.set( 109, 106, 2 )
   ca.set( 109, 107, 2 )
   ca.set( 109, 108, 2 )
   ca.set( 109, 109, 2 )
   ca.set( 109, 110, 2 )
   ca.set( 109, 111, 2 )
   ca.set( 109, 112, 2 )
   ca.set( 109, 113, 2 )

   for ct in range(3000):
      print( )
      print( ct )
      ca.tick( )
   
   quit()
   
   g = Grid( 10, 10 )
   g.setAt( 4, 5, 'n-hello', 1 )
   g.setAt( 5, 4, 'w-hello', 1 )
   g.setAt( 5, 6, 'e-hello', 1 )
   g.setAt( 6, 5, 's-hello', 1 )
   
   slot = g.getSlotAt( 5, 5 )
   vn   = slot.vNeighbors

   for dirStr, slot in vn.items():
      print( dirStr, slot.row, slot.col, slot.content, slot.contentType )

   westSlot = vn['W']
   print( timeit('westSlot.contentType == 1',         'from __main__ import westSlot', number=1000) )
   print( timeit('isinstance(westSlot.content, str)', 'from __main__ import westSlot', number=1000) )
