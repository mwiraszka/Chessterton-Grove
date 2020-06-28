# Chessterton Grove is an on-going practice project, with goals to
# 1) make the most sophisticated chess platform possible, while
# 2) documenting all progress for future reference.

# 19.06.20 project started
# 20.06.20 chessboard drawn
# 21.06.20 (test - github update)
# 21.06.20 chessboard drawing corrected, coordinates drawn
# 22.06.20 (temp: dimensions changed)
# 24.06.20 chess pieces drawn
# 25.06.20 select chess square enabled
# 26.06.20 (code cleaned up)
# 28.06.20 numpy arrays for keeping track of what is on each square


import sys
import pygame as pg
import numpy as np
from pygame.locals import *
pg.init()

WINW = 600
WINH = 600
win = pg.display.set_mode((WINW, WINH), 0, 32)
pg.display.set_caption("Chessterton Grove")
FPS = 60
clock = pg.time.Clock()

BLACK = (10,10,10)
WHITE = (245,245,245)
BOARD_BLACK = (80,70,60)
BOARD_WHITE = (200,200,200)
RED = (220,20,20)
BROWN = (139,69,19)
YELLOW = (200,200,0)
GREEN = (14,80,14)

stopdisp = False # temp: for testing identifying what is on a square
pg.font.get_fonts()
coord_font = pg.font.SysFont('helvetica', 18, False, False)

sq_sel_coord = [9,0] # Out of bounds: no square selected yet
sq_occupied = np.full((8,8), False)
on_sq = np.empty([8,8], dtype=object)

# b[0]-b[5]/w[0]-w[5]: queen, king, rook, knight, bishop, pawn, respectively
sheet = pg.image.load('chess_set.png').convert_alpha()
bQ = sheet.subsurface((0,0,50,50))
bK = sheet.subsurface((50,0,50,50))
bR = sheet.subsurface((100,0,50,50))
bN = sheet.subsurface((150,0,50,50))
bB = sheet.subsurface((200,0,50,50))
bP = sheet.subsurface((250,0,50,50))
wQ = sheet.subsurface((0,50,50,50))
wK = sheet.subsurface((50,50,50,50))
wR = sheet.subsurface((100,50,50,50))
wN = sheet.subsurface((150,50,50,50))
wB = sheet.subsurface((200,50,50,50))
wP = sheet.subsurface((250,50,50,50))


def terminate():
	pg.quit()
	sys.exit()

def draw_board():
	pg.draw.rect(win, BROWN, (80,80,440,440))
	for i in range(8):
		for j in range(8):
			if (i+j)%2 == 1:
				pg.draw.rect(win, BOARD_BLACK, ((100+50*i),(100+50*j),50,50))
			else:
				pg.draw.rect(win, BOARD_WHITE, ((100+50*i),(100+50*j),50,50))
	for i in range(8):
		# Draw digits 1-8 along side
		text_surface = coord_font.render(('{}'.format(i+1)), False, BLACK)
		win.blit(text_surface, (88,468-50*i))
		# Draw letters A-H (ASCII characters 65-72)
		text_surface = coord_font.render(('{}'.format(chr(65+i))), False, BLACK)
		win.blit(text_surface, (122+50*i,504))

def init_pieces():
	# sq Numpy Array indexing based on White's chessboard perspective, i.e.
	# sq[x-coord][y-coord] where x-coord 0-7 -> A-H; y-coord 0-7 -> 8-1
	on_sq[0][0] = on_sq[7][0] = 'bR'
	on_sq[1][0] = on_sq[6][0] = 'bN'
	on_sq[2][0] = on_sq[5][0] = 'bB'
	on_sq[3][0] = 'bQ'
	on_sq[4][0] = 'bK'
	on_sq[0][7] = on_sq[7][7] = 'wR'
	on_sq[1][7] = on_sq[6][7] = 'wN'
	on_sq[2][7] = on_sq[5][7] = 'wB'
	on_sq[3][7] = 'wQ'
	on_sq[4][7] = 'wK'
	for i in range(8):
		on_sq[i][1] = 'bP'
		on_sq[i][6] = 'wP'
	sq_occupied[:,0] = sq_occupied[:,1] = sq_occupied[:,6] = sq_occupied[:,7] = True

def draw_pieces():
 	for i in range(8):
 		for j in range(8):
 			if on_sq[i][j] == 'wR':
 				win.blit(wR, (100+i*50, 100+j*50))
 			elif on_sq[i][j] == 'wN':
 				win.blit(wN, (100+i*50, 100+j*50))
 			elif on_sq[i][j] == 'wB':
 				win.blit(wB, (100+i*50, 100+j*50))
 			elif on_sq[i][j] == 'wQ':
 				win.blit(wQ, (100+i*50, 100+j*50))
 			elif on_sq[i][j] == 'wK':
 				win.blit(wK, (100+i*50, 100+j*50))
 			elif on_sq[i][j] == 'wP':
 				win.blit(wP, (100+i*50, 100+j*50))
 			elif on_sq[i][j] == 'bR':
 				win.blit(bR, (100+i*50, 100+j*50))
 			elif on_sq[i][j] == 'bN':
 				win.blit(bN, (100+i*50, 100+j*50))
 			elif on_sq[i][j] == 'bB':
 				win.blit(bB, (100+i*50, 100+j*50))
 			elif on_sq[i][j] == 'bQ':
 				win.blit(bQ, (100+i*50, 100+j*50))
 			elif on_sq[i][j] == 'bK':
 				win.blit(bK, (100+i*50, 100+j*50))
 			elif on_sq[i][j] == 'bP':
 				win.blit(bP, (100+i*50, 100+j*50))
 			else:
 				pass

def draw_sq(sq):
	# Draw square by connecting the four dots
	pg.draw.lines(win, RED, True, [(100+sq[0]*50,100+sq[1]*50),\
		(150+sq[0]*50,100+sq[1]*50),(150+sq[0]*50,150+sq[1]*50),\
		(100+sq[0]*50,150+sq[1]*50)], 3)

init_pieces()
while True:
	win.fill(GREEN)
	draw_board()
	draw_pieces()
	if sq_sel_coord[0] < 9:
		draw_sq(sq_sel_coord)
		if not stopdisp:
			print ('sq has ' + str(on_sq[sq_sel_coord[0]][sq_sel_coord[1]]))
	event = pg.event.get()
	for e in event:
		if e.type == pg.MOUSEBUTTONUP:
			# Store coordinate of the selected square on the 8x8 board, with
			# indeces starting at 0 (e.g. A1 = (0,0), C5 = (2,4), etc.)
			for i in range(8):
				# Store x- and y-coords of clicked square, indeces starting at 0
				if pg.mouse.get_pos()[0] >= (100+i*50) and\
				pg.mouse.get_pos()[0] < (150+i*50):
					sq_sel_coord[0] = i
					stopdisp = False
				if pg.mouse.get_pos()[1] >= (100+i*50) and\
				pg.mouse.get_pos()[1] < (150+i*50):
					sq_sel_coord[1] = i
					stopdisp = False
				# Click is out of bounds (use x = 9 as an indicator)
				if pg.mouse.get_pos()[0] >= 500 or pg.mouse.get_pos()[0] < 100 or\
				pg.mouse.get_pos()[1] >= 500 or pg.mouse.get_pos()[1] < 100:
					sq_sel_coord[0] = 9
					stopdisp = True
		if e.type == QUIT:
			terminate()
		if e.type == KEYDOWN:
			pass
		if e.type == KEYUP:
			if e.key == K_ESCAPE or e.key == K_q:
				terminate()

	pg.display.update()
	clock.tick(FPS)