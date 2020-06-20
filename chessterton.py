# Chessterton Grove will be an on-going practice project, with the sole goal to
# make the most sophisticated chess platform possible, with all progress
# documented for future reference.

# 19 June 2020: project started





# 1) begin coding with pygame right away
# 2) 8x8 board on the screen, label, quit works

import sys
import pygame as pg
from pygame.locals import *
pg.init()

WINW = 600
WINH = 600
win = pg.display.set_mode((WINW, WINH), 0, 32)
pg.display.set_caption("Chessterton Grove")

BLACK = (0, 0, 0)
YELLOW = (200, 200, 0)
GREEN = (150, 255, 60)
WHITE = (255, 255, 255)
FPS = 60

clock = pg.time.Clock()

def terminate():
	pg.quit()
	sys.exit()


while True:
	win.fill(GREEN)
	for i in range(0,7):
		for j in range(0,7):
			if (i+j)%2 == 1:
				pg.draw.rect(win, WHITE, ((100+50*i),(100+50*j),50,50))
			else:
				pg.draw.rect(win, BLACK, ((100+50*i),(100+50*j),50,50))

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




