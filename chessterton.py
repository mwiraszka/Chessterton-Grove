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
# 03.07.20 all variables rewritten as 'game state' class attributes
# 05.07.20 redefine sq_sel variable w.r.t. mouse click position variable
# 05.07.20 add all square-select/move piece variables to GameState class



# Author: Michal Wiraszka June-July 2020
# Contributions, Influences, References:
#	- Eddie Sharick's "Chess Engine in Python" Tutorial
#	  for 'Game State' Class

# ---IMPORTS---
import sys
import pygame as pg
import numpy as np
from pygame.locals import *

# ---CONSTANTS---
WIN_SIZE = 600
SQ_SIZE = 50

FPS = 60
BLACK = (10,10,10)
WHITE = (245,245,245)
B_SQ = (80,70,60)
W_SQ = (200,200,200)
RED = (220,20,20)
BROWN = (139,69,19)
YELLOW = (200,200,0)
GREEN = (14,80,14)
PC_IMG = {}

# ---PYGAME SETUP---
pg.init()
win = pg.display.set_mode((WIN_SIZE, WIN_SIZE), 0, 32)
pg.display.set_caption("Chessterton Grove")
clock = pg.time.Clock()
pg.font.get_fonts()
coord_font = pg.font.SysFont('helvetica', 18, False, False)



# ---MAIN CLASS CONTAINING ALL OF GAME'S CURRENT STATE INFORMATION---
class GameState():
	def __init__(self):
		self.board = [
			['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
			['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
			['ee', 'ee', 'ee', 'ee', 'ee', 'ee', 'ee', 'ee'],
			['ee', 'ee', 'ee', 'ee', 'ee', 'ee', 'ee', 'ee'],
			['ee', 'ee', 'ee', 'ee', 'ee', 'ee', 'ee', 'ee'],
			['ee', 'ee', 'ee', 'ee', 'ee', 'ee', 'ee', 'ee'],
			['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
			['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]
		self.white_to_move = True
		self.move_log = []
		self.sq_from = [9,0] # (9,0) indicates out of bounds/ no selection
		self.sq_to = []
	def highlight_sq(self, sq):
	# Draw square by connecting the four dots
		pg.draw.lines(win, RED, True, [
			(100+sq[0]*50,100+sq[1]*50),\
			(150+sq[0]*50,100+sq[1]*50),\
			(150+sq[0]*50,150+sq[1]*50),\
			(100+sq[0]*50,150+sq[1]*50)], 3)



def load_images():
	sheet = pg.image.load('chess_set.png').convert_alpha()
	i = 0
	pieces = [
		'bQ', 'bK', 'bR', 'bN', 'bB','bP',
		'wQ', 'wK', 'wR', 'wN', 'wB', 'wP'
		]
	for piece in pieces:
		PC_IMG[piece] = sheet.subsurface(i*50,0,50,50)
		i += 1

def draw_game_state(screen, board):
	pg.draw.rect(screen, BROWN, (80,80,440,440))
	# Draw board
	for i in range(8):
		for j in range(8):
			if (i+j) % 2 == 1:
				pg.draw.rect(screen, B_SQ,\
					(100 + j*SQ_SIZE, 100 + i*SQ_SIZE, SQ_SIZE, SQ_SIZE))
			else:
				pg.draw.rect(screen, W_SQ,\
					(100 + j*SQ_SIZE, 100 + i*SQ_SIZE, SQ_SIZE, SQ_SIZE))
	for i in range(8):
		# Draw digits 1-8 along side
		digits = coord_font.render(('{}'.format(i+1)), False, BLACK)
		screen.blit(digits, (88, 468 - 50*i))
		# Draw letters A-H (ASCII characters 65-72) along bottom
		letters = coord_font.render(('{}'.format(chr(65+i))), False, BLACK)
		screen.blit(letters, (122 + 50*i, 504))
	# Draw pieces
	for i in range(8):
 		for j in range(8):
 			piece = board[i][j]
 			if piece != 'ee':
 				screen.blit(PC_IMG[piece], (100 + j*SQ_SIZE, 100 + i*SQ_SIZE))

def terminate():
	pg.quit()
	sys.exit()





def main():
	gs = GameState()
	load_images()
	sq_sel = [9,0]

	while True:
		win.fill(GREEN)
		draw_game_state(win, gs.board)
		if gs.sq_from[0] < 9:
			gs.highlight_sq(gs.sq_from)
		
		event = pg.event.get()
		for e in event:
			if e.type == pg.MOUSEBUTTONUP:
				if pg.mouse.get_pos()[0] >= 500 or pg.mouse.get_pos()[0] < 100 or\
					pg.mouse.get_pos()[1] >= 500 or pg.mouse.get_pos()[1] < 100:
					# use x-coord = 9 as indicator that click is out of bounds
					gs.sq_from[0] = 9
				else:
					gs.sq_from[0] = (pg.mouse.get_pos()[0]-100) // SQ_SIZE
					gs.sq_from[1] = (pg.mouse.get_pos()[1]-100) // SQ_SIZE

			if e.type == QUIT:
				terminate()
			if e.type == KEYDOWN:
				pass
			if e.type == KEYUP:
				if e.key == K_ESCAPE or e.key == K_q:
					terminate()

		pg.display.update()
		clock.tick(FPS)



if __name__ == "__main__":
	main()