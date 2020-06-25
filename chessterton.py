# Chessterton Grove will be an on-going practice project, with the sole goal to
# make the most sophisticated chess platform possible, with all progress
# documented for future reference.

# 19.06.20 project started
# 20.06.20 chessboard drawn
# 21.06.20 (test - github update)
# 21.06.20 chessboard drawing corrected, coordinates drawn
# 22.06.20 (temp: dimensions changed)
# 24.06.20 chess pieces drawn



import sys
import pygame as pg
from pygame.locals import *
pg.init()

WINW = 600
WINH = 600
win = pg.display.set_mode((WINW, WINH), 0, 32)
pg.display.set_caption("Chessterton Grove")

BLACK = (10,10,10)
WHITE = (245,245,245)
BOARD_BLACK = (80,70,60)
BOARD_WHITE = (200,200,200)
BROWN = (139,69,19)
YELLOW = (200,200,0)
GREEN = (34,139,34)

FPS = 60

pg.font.get_fonts()
coord_font = pg.font.SysFont('helvetica', 18, False, False)

clock = pg.time.Clock()

# wP = pg.image.load('pieces/white_pawn.png')
# wR = pg.image.load('pieces/white_rook.png')
# wN = pg.image.load('pieces/white_knight.png')
# wB = pg.image.load('pieces/white_bishop.png')
# wQ = pg.image.load('pieces/white_queen.png')
# wK = pg.image.load('pieces/white_king.png')

# bP = pg.image.load('pieces/black_pawn.png')
# bR = pg.image.load('pieces/black_rook.png')
# bN = pg.image.load('pieces/black_knight.png')
# bB = pg.image.load('pieces/black_bishop.png')
# bQ = pg.image.load('pieces/black_queen.png')
# bK = pg.image.load('pieces/black_king.png')

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

def drawBoard():
	pg.draw.rect(win, BROWN, (80,80,440,440))
	for i in range(0,8):
		for j in range(0,8):
			if (i+j)%2 == 1:
				pg.draw.rect(win, BOARD_BLACK, ((100+50*i),(100+50*j),50,50))
			else:
				pg.draw.rect(win, BOARD_WHITE, ((100+50*i),(100+50*j),50,50))
	for i in range(0,8):
		# Draw digits 1-8 along side
		text_surface = coord_font.render(('{}'.format(i+1)), False, BLACK)
		win.blit(text_surface, (88,468-50*i))
		# Draw letters A-H (ASCII characters 65-72)
		text_surface = coord_font.render(('{}'.format(chr(65+i))), False, BLACK)
		win.blit(text_surface, (122+50*i,504))

def drawPieces():
	win.blit(bR, (100,100))
	win.blit(bN, (150,100))
	win.blit(bB, (200,100))
	win.blit(bQ, (250,100))
	win.blit(bK, (300,100))
	win.blit(bB, (350,100))
	win.blit(bN, (400,100))
	win.blit(bR, (450,100))
	for i in range(0,8):
		win.blit(bP, (100+i*50,150))
		win.blit(wP, (100+i*50,400))
	win.blit(wR, (100,450))
	win.blit(wN, (150,450))
	win.blit(wB, (200,450))
	win.blit(wQ, (250,450))
	win.blit(wK, (300,450))
	win.blit(wB, (350,450))
	win.blit(wN, (400,450))
	win.blit(wR, (450,450))
	


while True:
	win.fill(GREEN)
	drawBoard()
	drawPieces()
	for event in pg.event.get():
		if event.type == QUIT:
			terminate()
		if event.type == KEYDOWN:
			pass
		if event.type == KEYUP:
			if event.key == K_ESCAPE or event.key == K_q:
				terminate()

	pg.display.update()
	clock.tick(FPS)




