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


import sys
import pygame as pg
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
GREEN = (34,139,34)

pg.font.get_fonts()
coord_font = pg.font.SysFont('helvetica', 18, False, False)

sq_coord = [9,0]

# b[0]-b[5]/w[0]-w[5]: queen, king, rook, knight, bishop, pawn, respectively
sheet = pg.image.load('chess_set.png').convert_alpha()
b = [None] * 6
w = [None] * 6
for i in range(6):
	b[i] = sheet.subsurface((i*50,0,50,50))
	w[i] = sheet.subsurface((i*50,50,50,50))


def terminate():
	pg.quit()
	sys.exit()

def drawBoard():
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

def initPieces():
	win.blit(b[2], (100,100))
	win.blit(b[3], (150,100))
	win.blit(b[4], (200,100))
	win.blit(b[1], (250,100))
	win.blit(b[0], (300,100))
	win.blit(b[4], (350,100))
	win.blit(b[3], (400,100))
	win.blit(b[2], (450,100))
	for i in range(0,8):
		win.blit(b[5], (100+i*50,150))
		win.blit(w[5], (100+i*50,400))
	win.blit(w[2], (100,450))
	win.blit(w[3], (150,450))
	win.blit(w[4], (200,450))
	win.blit(w[1], (250,450))
	win.blit(w[0], (300,450))
	win.blit(w[4], (350,450))
	win.blit(w[3], (400,450))
	win.blit(w[2], (450,450))

def drawSqSelect(sq):
	# Start at 100 and add coordinate values multipled by a factor of 50
	pg.draw.lines(win, RED, True, [(100+sq[0]*50,100+sq[1]*50),\
		(150+sq[0]*50,100+sq[1]*50),(150+sq[0]*50,150+sq[1]*50),\
		(100+sq[0]*50,150+sq[1]*50)], 3)


while True:
	win.fill(GREEN)
	drawBoard()
	initPieces()
	if sq_coord[0] < 9:
		drawSqSelect(sq_coord)
	event = pg.event.get()
	for e in event:
		if e.type == pg.MOUSEBUTTONUP:
			# Store coordinate of the selected square on the 8x8 board, with
			# indeces starting at 0 (e.g. A1 = (0,0), C5 = (2,4), etc.)
			for i in range(8):
				# Store x- and y-coords of clicked square, indeces starting at 0
				if pg.mouse.get_pos()[0] >= (100+i*50) and\
				pg.mouse.get_pos()[0] < (150+i*50):
					sq_coord[0] = i
				if pg.mouse.get_pos()[1] >= (100+i*50) and\
				pg.mouse.get_pos()[1] < (150+i*50):
					sq_coord[1] = i
				# Click is out of bounds (use x = 9 as an indicator)
				if pg.mouse.get_pos()[0] >= 500 or pg.mouse.get_pos()[0] < 100 or\
				pg.mouse.get_pos()[1] >= 500 or pg.mouse.get_pos()[1] < 100:
					sq_coord[0] = 9
		if e.type == QUIT:
			terminate()
		if e.type == KEYDOWN:
			pass
		if e.type == KEYUP:
			if e.key == K_ESCAPE or e.key == K_q:
				terminate()

	pg.display.update()
	clock.tick(FPS)




