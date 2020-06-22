# Chessterton Grove will be an on-going practice project, with the sole goal to
# make the most sophisticated chess platform possible, with all progress
# documented for future reference.

# 19 June 2020: project started
# 20 June 2020: chessboard drawn
# 21 June 2020: (test - github update)
# 21 June 2020: chessboard drawing corrected, coordinates drawn 




import sys
import pygame as pg
from pygame.locals import *
pg.init()

WINW = 600
WINH = 600
win = pg.display.set_mode((WINW, WINH), 0, 32)
pg.display.set_caption("Chessterton Grove")

BLACK = (30, 20, 10)
BROWN = (139, 69, 19)
YELLOW = (200, 200, 0)
GREEN = (34, 139, 34)
WHITE = (220, 220, 220)
FPS = 60

pg.font.get_fonts()
coord_font = pg.font.SysFont('helvetica', 18, False, False)

clock = pg.time.Clock()

def terminate():
	pg.quit()
	sys.exit()

def drawBoard():
	pg.draw.rect(win, BROWN, (80,80,440,440))
	for i in range(0,8):
		for j in range(0,8):
			if (i+j)%2 == 1:
				pg.draw.rect(win, BLACK, ((100+50*i),(100+50*j),50,50))
			else:
				pg.draw.rect(win, WHITE, ((100+50*i),(100+50*j),50,50))
	
	for i in range(0,8):
		# Draw digits 1-8 along side
		text_surface = coord_font.render(('{}'.format(i+1)), False, BLACK)
		win.blit(text_surface, (88,468-50*i))
		# Draw letters A-H (ASCII characters 65-72)
		text_surface = coord_font.render(('{}'.format(chr(65+i))), False, BLACK)
		win.blit(text_surface, (122+50*i,504))


while True:
	win.fill(GREEN)
	drawBoard()

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




