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
# 06.07.20 combine sq_from & sq_to to sq_move list; move a piece
# 07.07.20 notation conversion function
# 12.07.20 notation conversion function, cont'd
# 13.07.20 pawn moves off 2nd rank - trial
# 14.07.20 'check_move_validity' & re-incorporate numpy array for board
# 14.07.20 white pawn moves, cont'd; 'b' to print board


# Written by Michal Wiraszka in June-July 2020


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
PIECE_IMg = {}

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
		self.board = np.array([
			['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
			['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
			['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
			['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
			['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
			['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
			['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
			['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']])
		self.move_log = []
		self.white_to_move = True
		self.move = [] # int list [from-x, from-y, to-x, to-y]


def check_move_validity(board, move):
	from_x = move[0]
	from_y = move[1]
	to_x = move[2]
	to_y = move[3]
	piece = board[from_y, from_x]

	valid = False
	
	# Pawn move
	if piece == 'wP':
		if from_x == to_x and board[from_y - 1, from_x] == '  ':
			if to_y == (from_y - 1):
				if from_y > 1:
					valid = True
			elif to_y == (from_y - 2) and from_y == 6 and\
			board[(from_y - 2), from_x] == '  ':
				valid = True
	return valid


def move_piece(board, move):
	piece = board[move[1], move[0]]
	board[move[3], move[2]] = board[move[1], move[0]]
	board[move[1], move[0]] = '  '
	print (piece[1] + ' at ' + cr_fr([move[1], move[0]]) +\
		   ' has been moved to ' + cr_fr([move[3], move[2]]) + '.')


def load_images():
	sheet = pg.image.load('chess_set.png').convert_alpha()
	pieces = ['bQ', 'bK', 'bR', 'bN', 'bB','bP',
			  'wQ', 'wK', 'wR', 'wN', 'wB', 'wP'
			 ]
	for i in range(len(pieces)):
		PIECE_IMg[pieces[i]] = sheet.subsurface(i*50,0,50,50)

def draw_chessboard(screen):
	pg.draw.rect(screen, BROWN, (80,80,440,440))
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

def draw_pieces(screen, board):
	for i in range(8):
		for j in range(8):
			if board[i][j] != '  ':
				pc = board[i][j]
				screen.blit(PIECE_IMg[pc],(100 + j*SQ_SIZE, 100 + i*SQ_SIZE))

def highlight_sq(screen, sq):
	# Draw square by connecting the four points
	pg.draw.lines(screen, RED, True, [(100+sq[0]*50,100+sq[1]*50),\
								      (150+sq[0]*50,100+sq[1]*50),\
								      (150+sq[0]*50,150+sq[1]*50),\
								      (100+sq[0]*50,150+sq[1]*50)], 3)
def cr_fr(cr):
	# Convert column-row notation to file-rank notation
	# Expects int list 'cr' where cr[0] = {0,1,..,7}; cr[1] = {0,1,..,7}
	# Returns str 'fr' where file (f) = {a,b,..,h}; rank (r) = {1,2,..,8}
	fr = chr(97 + cr[0]) + str(8 - cr[1])
	return (fr)

def fr_cr(fr):
	# Convert file-rank notation to column-row notation
	# Expects str 'fr' where file (f) = {a,b,..,h}; rank (r) = {1,2,..,8}
	# Returns int list 'cr' where cr[0] = {0,1,..,7}; cr[1] = {0,1,..,7}
	cr = [ord(fr[0]) - 97, int(fr[1]) - 1]
	return cr


def terminate():
	pg.quit()
	sys.exit()





def main():
	gs = GameState()
	load_images()
	clk = ()
	move_valid = False
	while True:
		win.fill(GREEN)
		draw_chessboard(win)
		draw_pieces(win, gs.board)
		if clk:
			if clk[0] < 100 or clk[0] >= 500 or clk[1] < 100 or clk[1] >= 500:
				gs.move = [] # Click is out of bounds: reset list
			elif len(gs.move) < 4:
				gs.move.append((clk[0]-100) // SQ_SIZE)
				gs.move.append((clk[1]-100) // SQ_SIZE)
				if len(gs.move) > 2 and (gs.move[0] == gs.move[2])\
						and (gs.move[1] == gs.move[3]):
					# 'From' and 'To' squares are the same: truncate list
					del gs.move[2:]
				highlight_sq(win, gs.move)
			else:
				move_valid = check_move_validity(gs.board, gs.move)
				clk = (0,0)
				if move_valid:
					move_piece(gs.board, gs.move)
					gs.move = []
					

		event = pg.event.get()
		for e in event:
			if e.type == MOUSEBUTTONDOWN:
				clk = e.pos
			if e.type == QUIT:
				terminate()
			if e.type == KEYDOWN:
				pass
			if e.type == KEYUP:
				if e.key == K_b:
					print(gs.board)
					print('\n')
				if e.key == K_ESCAPE or e.key == K_q:
					terminate()

		pg.display.update()
		clock.tick(FPS)



if __name__ == "__main__":
	main()