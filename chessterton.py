# CHESSTERTON GROVE
# by Michal Wiraszka

# Written fully in Python, making heavy use of its Pygame and Numpy modules.

# What is 'Chessterton Grove'?
# 'Chessterton Grove' is sophistication. 'Chessterton Grove' is poise.
# 'Chessterton Grove', my friend, is all you've ever strived to be, but could
# never quite make it. Now, while 'Chessterton Grove' exudes such grandiosity
# as to necessitate itself to refer to itself in the third person, it is equally
# humble to concede that Rome was not built in a day and may or may not be a
# little rough around the edges.

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
# 14.07.20 white pawn captures; change turn instance attribute to str
# 15.07.20 black pawn moves & captures; queening
# 15.07.20 .move_log instance attribute - conception; knight moves
# 16.07.20 bishop moves
# 16.07.20 rook moves; some absolute value calculations simplified
# 17.07.20 king and queen moves
# 20.07.20 glitch in highlighting square fixed
# 20.07.20 white and black to move in turn
# 20.07.20 scream at user if king is in check - rough trial
# 26.07.20 defined a gs.move_log variable as a list of dicts
# 27.07.20 en passant
# 06.08.20 highlight a square only if there is a piece on it
# 09.08.20 check if king is in check, cont'd
# 16.08.20 change .turn to .colour; invalidate move if walking into check
# 16.08.20 function names simplified; recognize checkmate


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
BLUE = (20,20,220)
BROWN = (139,69,19)
YELLOW = (200,200,0)
GREEN = (14,80,14)
PIECE_IMG = {}

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
		self.colour = 'w'		
		self.move = [] #list of ints [from-x, from-y, to-x, to-y]
		self.in_check = False
		# list of dictionaries; initialize with dummy variable so that check_move_valid
		# function can be called, and so that ply count (list index) starts at 1
		self.move_log = [0]



# ---ALL FUNCTIONS---
def is_valid(board, move, colour, move_log):
	# Rename all variables passed in for ease of use 
	from_x = move[0]
	from_y = move[1]
	to_x = move[2]
	to_y = move[3]
	x_diff = to_x - from_x
	y_diff = to_y - from_y
	x_direction = -1 if x_diff < 0 else 1
	y_direction = -1 if y_diff < 0 else 1
	piece = board[from_y, from_x]

	# --- CHECK #1: check if 'to' and 'from' squares are the same.
	if from_x==to_x and from_y==to_y:
		return False
	
	# --- CHECK #2: check if trying to move wrong coloured piece.
	if colour != piece[0]:
		return False
	
	# --- CHECK #3: check if trying to capture own piece.
	if colour == board[to_y, to_x][0]:
		return False

	# --- CHECK #4: check if this is proper move for that piece to make.
	proper_move = False
	if piece.endswith('P'):
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
					from_y == 3 and
					to_y == 2 and
					abs(x_diff) == 1 and
					move_log[-1].get('piece') == 'bP' and
					move_log[-1].get('from_y') == 1 and
					move_log[-1].get('to_y') == 3 and
					abs(move_log[-1].get('to_x') - from_x) == 1)
				):
			proper_move = True
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
					from_y == 4 and
					to_y == 5 and
					abs(x_diff) == 1 and
					move_log[-1].get('piece') == 'wP' and
					move_log[-1].get('from_y') == 6 and
					move_log[-1].get('to_y') == 4 and
					abs(move_log[-1].get('to_x') - from_x) == 1)
				):
			proper_move = True
		else:
			proper_move = False
	elif piece.endswith('N'):
			if (	(abs(x_diff)==2 and abs(y_diff)==1) or
					(abs(x_diff)==1 and abs(y_diff)==2)):
				proper_move = True
			else:
				proper_move = False
	elif piece.endswith('B'):
		proper_move = True
		if abs(x_diff) != abs(y_diff):
			proper_move = False
		else:
			# Check for any pieces along the way;
			# If x_diff or y_diff is neg, step direction = -1, and start index
			# also set to -1 (i.e. don't check origin square at index 0)
			for i in range(x_direction, x_diff, x_direction):
				for j in range(y_direction, y_diff, y_direction):
					if abs(i)==abs(j) and board[from_y+j, from_x+i] != '  ':
						proper_move = False
	elif piece.endswith('R'):
		proper_move = True
		if y_diff == 0:
			for i in range(x_direction, x_diff, x_direction):
				if board[from_y, from_x+i] != '  ':
					proper_move = False
		elif x_diff == 0:
			for i in range(y_direction, y_diff, y_direction):
				if board[from_y+i, from_x] != '  ':
					proper_move = False
		else:
			proper_move = False
	elif piece.endswith('Q'):
		# Check for any pieces along the way, for the three cases:
		# horizontal move (y_diff is 0), vertical move (x_diff is 0),
		# and diagonal move (absolute values of x_diff & y_diff are equal) 
		proper_move = True
		if y_diff == 0:
			for i in range(x_direction, x_diff, x_direction):
				if board[from_y, from_x+i] != '  ':
					proper_move = False
		elif x_diff == 0:
			for i in range(y_direction, y_diff, y_direction):
				if board[from_y+i, from_x] != '  ':
					proper_move = False
		elif abs(x_diff) == abs(y_diff):
			for i in range(x_direction, x_diff, x_direction):
				for j in range(y_direction, y_diff, y_direction):
					if abs(i)==abs(j) and board[from_y+j, from_x+i] != '  ':
						proper_move = False
		else:
			proper_move = False
	elif piece.endswith('K') and abs(y_diff)<=1 and abs(x_diff)<=1:
		proper_move = True
	
	if proper_move == False:
		return False

	# --- CHECK #5: check if this move would move your king into check.
	hypothetical_board, move_info = move_piece(board, move)
	moving_into_check = is_check(hypothetical_board, colour, move_log)
	if moving_into_check:
		return False
	
	# --- All 5 checks passed, so move is deemed valid.
	return True


def is_check(board, colour, move_log):
	king_pos = np.where(board == (str(colour)+'K'))
	in_check = False
	for i in range(8):
	   	for j in range(8):
	   		if board[i, j][0] == swap_col(colour):
	   			# Test if any of opponent's pieces would be able to capture king in a valid way
	   			move = [j, i, king_pos[1].item(), king_pos[0].item()]
	   			could_be_captured = is_valid(board, move, swap_col(colour), move_log)
	   			if could_be_captured:
	   				in_check = True
	return in_check


def is_checkmate(board, colour, move_log):
	in_check = is_check(board, colour, move_log)
	if not in_check:
		return False
	for i in range(8):
		for j in range(8):
			# Check if any of this colour's pieces have any valid moves to make.
			if board[i, j][0] == colour:
				for x in range(8):
					for y in range(8):
						valid_move = is_valid(board, [j, i, y, x], colour, move_log)
						if valid_move:
							return False
	return True





def move_piece(board, move):
	# Returns 1) move_info and 2) new_board (i.e. the board after move is made)
	from_x = move[0]
	from_y = move[1]
	to_x = move[2]
	to_y = move[3]
	piece = board[from_y, from_x]
	move_info = {
		'piece': piece,
		'from_x': from_x,
		'from_y': from_y,
		'to_x': to_x,
		'to_y': to_y,
		'capture': board[to_y, to_x],
		'check': False
		}
	new_board = board.copy()
	# En passant scenario: register move as a special capture and
	# manually remove the opponent's pawn
	if piece.endswith('P') and\
			abs(from_x - to_x) == 1 and board[to_y, to_x] == '  ':
		move_info['capture'] = 'ep'
		if to_y == 2:
			new_board[to_y + 1, to_x] = '  '
		else:
			new_board[to_y - 1, to_x] = '  '
	# Pawn queening scenario: change pawn to a queen;
	# otherwise simply move that same piece to the new square
	if piece == 'wP' and to_y == 0:
		new_board[to_y, to_x] = 'wQ'
	elif piece == 'bP' and to_y == 7:
		new_board[to_y, to_x] = 'bQ'
	else:
		new_board[to_y, to_x] = new_board[from_y, from_x]
	new_board[from_y, from_x] = '  '

	return new_board, move_info


def swap_col(colour):
	if colour == 'w':
		return 'b'
	else:
		return 'w'


def load_images():
	sheet = pg.image.load('chess_set.png').convert_alpha()
	pieces = ['bQ', 'bK', 'bR', 'bN', 'bB','bP',
			  'wQ', 'wK', 'wR', 'wN', 'wB', 'wP'
			 ]
	for i in range(len(pieces)):
		PIECE_IMG[pieces[i]] = sheet.subsurface(i*50,0,50,50)

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
				screen.blit(PIECE_IMG[pc],(100 + j*SQ_SIZE, 100 + i*SQ_SIZE))

def highlight_sq(screen, sq, colour):
	# Draw red square 3 pixels thick by connecting the four points
	if colour == 'w':
		turn_col = WHITE
	else:
		turn_col = BLACK
	pg.draw.lines(screen, turn_col, True, [(100+sq[0]*50, 100+sq[1]*50),\
								      	   (150+sq[0]*50, 100+sq[1]*50),\
								           (150+sq[0]*50, 150+sq[1]*50),\
								           (100+sq[0]*50, 150+sq[1]*50)], 3)
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
	print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
	print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
	print('NEW GAME!')
	print('\n\n\n\n\n')
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
				if len(gs.move) == 4:
					move_valid = is_valid(gs.board, gs.move, gs.colour, gs.move_log)
					if move_valid:
						new_board, move_info = move_piece(gs.board, gs.move)
						gs.board = new_board
						gs.move_log.append(move_info)
						gs.move = []
						gs.colour = swap_col(gs.colour)
						checkmate = is_checkmate(gs.board, gs.colour, gs.move_log)
						if checkmate:
							print('checkmate!')
					else:
						# Use the 2nd selected square as new 'From' square
						gs.move[0] = gs.move[2]
						gs.move[1] = gs.move[3]
						del gs.move[2:]
			clk = ()
		#If a piece is selected (and only if it's that colour's turn to move)
		if len(gs.move) == 2 and gs.board[gs.move[1]][gs.move[0]].startswith(gs.colour):
			highlight_sq(win, gs.move, gs.colour)		

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
					# display current board state in text
					print('\n' + str(gs.board) + '\n')
				if e.key == K_l:
					# display move log list
					print('\n' + str(gs.move_log) + '\n')
				if e.key == K_ESCAPE or e.key == K_q:
					terminate()

		pg.display.update()
		clock.tick(FPS)


if __name__ == "__main__":
	main()