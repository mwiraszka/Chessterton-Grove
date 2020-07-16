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
# 14.07.20 white pawn captures; change .turn instance attribute to str
# 15.07.20 black pawn moves & captures; queening
# 15.07.20 .move_log instance attribute - conception; knight moves
# 16.07.20 bishop moves
# 16.07.20 rook moves; some absolute value calculations simplified


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
			['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
			])
		
		self.turn = 'w'		
		self.move = [] #list of ints [from-x, from-y, to-x, to-y]
		
		#move_log = {
		#'ply_num': 14,
		#'piece': 'wP',
		#'from_x': 3,
		#'from_y': 1,
		#'to_x': 3,
		#'to_y': 2,
		#'capture': '  ',
		#'check': False}


def check_move_valid(board, move):
	from_x = move[0]
	from_y = move[1]
	to_x = move[2]
	to_y = move[3]
	x_diff = to_x - from_x
	y_diff = to_y - from_y
	x_direction = -1 if x_diff < 0 else 1
	y_direction = -1 if y_diff < 0 else 1
	piece = board[from_y, from_x]
	
	if (board[to_y, to_x])[0] != piece[0]:
		if piece == 'wP' and (
				(
					# one square forward
					from_x == to_x and
					from_y - to_y == 1 and
					board[to_y, to_x] == '  ') or 
				(
					# two squares forward
					from_x == to_x and
					from_y - to_y == 2 and
					from_y == 6 and
					board[to_y, to_x] == '  ' and
					board[to_y + 1, to_x] == '  ') or
				(
					# capture
					abs(x_diff) == 1 and
					from_y - to_y == 1 and
					board[to_y, to_x].startswith('b')) or
				(	
					# capture en passant
					False)
				):
			return True
		elif piece == 'bP' and (
				(
					# one square forward
					from_x == to_x and
					to_y - from_y == 1 and
					board[to_y, to_x] == '  ') or 
				(
					# two squares forward
					from_x == to_x and
					to_y - from_y == 2 and
					from_y == 1 and
					board[to_y, to_x] == '  ' and
					board[to_y - 1, to_x] == '  ') or
				(
					# capture
					abs(x_diff) == 1 and
					to_y - from_y == 1 and
					board[to_y, to_x].startswith('w')) or
				(	
					# capture en passant
					False)
				):
			return True
		elif piece.endswith('N') and (
				(abs(x_diff) == 2 and abs(y_diff) == 1) or
				(abs(x_diff) == 1 and abs(y_diff) == 2)):
			return True
		elif piece.endswith('B') and abs(x_diff) == abs(y_diff):
			# check for any pieces along the way
			# if x_diff or y_diff is neg, step direction = -1, and start index
			# also set to -1 (i.e. don't check origin square at index 0)
			for i in range(x_direction, x_diff, x_direction):
				for j in range(y_direction, y_diff, y_direction):
					if abs(i)==abs(j) and board[from_y+j, from_x+i] != '  ':
						return False
			return True
		elif piece.endswith('R') and (x_diff == 0 or y_diff == 0):
			if x_diff != 0:
				for i in range(x_direction, x_diff, x_direction):
					if board[from_y, from_x+i] != '  ':
						return False
			else:
				for i in range(y_direction, y_diff, y_direction):
					if board[from_y+i, from_x] != '  ':
						return False
			return True
		return False


def move_piece(board, move):
	from_x = move[0]
	from_y = move[1]
	to_x = move[2]
	to_y = move[3]
	piece = board[from_y, from_x]
	
	if piece == 'wP' and to_y == 0:
		board[to_y, to_x] = 'wQ'
	elif piece == 'bP' and to_y == 7:
		board[to_y, to_x] = 'bQ'
	else:
		board[to_y, to_x] = board[from_y, from_x]
	board[from_y, from_x] = '  '
	
	print (piece[1] + ' at ' + cr_fr([from_x, from_y]) +\
		   ' moved to ' + cr_fr([to_x, to_y]) + '.\n')


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
				move_valid = check_move_valid(gs.board, gs.move)
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