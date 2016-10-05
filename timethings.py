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

import random

def addImg( ):
   x = random.randint(1,200)
   y = random.randint(1,200)
   
   img = tk.BitmapImage( data=SHAPE['8.BLOCK'], foreground='blue', background='black' )
   obj = can.create_image( x, y, image=img )
   
   can.move( obj, +10, +10 )
   
   can.delete( obj )

def addBmp( ):
   x = random.randint(1,200)
   y = random.randint(1,200)
   
   obj = can.create_bitmap( x, y, bitmap=SHAPE['8.BLOCK'], foreground='blue', background='black' )
   
   can.move( obj, +10, +10 )
   
   can.delete( obj )

def addRct( ):
   x = random.randint(1,200)
   y = random.randint(1,200)
   
   obj = can.create_rectangle( x, y, x+8, y+8, fill='blue' )
   
   can.move( obj, +10, +10 )
   
   can.delete( obj )

top = tk.Tk()
can = tk.Canvas( top, height=200, width=200, background='black' )
can.pack()

count = 0
def draw( ):
   global count
   
   addRct( )
   
   if count < 10000:
      count += 1
      top.after( 1, draw )
   else:
      top.quit( )

top.after( 1, draw )

#top.mainloop( )

import timeit
import profile

profile.run( 'top.mainloop()' )
#print( 'Img', timeit.timeit( 'top.mainloop()', 'from __main__ import top', number=1 ) )
#print( 'Bmp', timeit.timeit( 'addBmp()', 'from __main__ import addBmp' ) )
#print( 'Rct', timeit.timeit( 'addRct()', 'from __main__ import addRct' ), number=1 )
