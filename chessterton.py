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

# ---VERSION 1.0:
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
# 16.08.20 recognize stalemate
# 16.08.20 get_move_info; notation displayed in shell by pressing b (glitchy)
# 17.08.20 fixed glitch with check, checkmate, and stalemate recognition
# 17.08.20 added right-side section to window; move_log to include more specific move traits; castling


# ---IMPORTS---
import sys
import pygame as pg
import numpy as np
from pygame.locals import *

# ---CONSTANTS---
WIN_W = 800
WIN_H = 700
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
win = pg.display.set_mode((WIN_W, WIN_H), 0, 32)
pg.display.set_caption("Chessterton Grove v1.0")
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
		# New move coordinates: [from-x, from-y, to-x, to-y]
		self.move_coord = [] 
		self.colour = 'w'
		self.move_log = []




# ---FUNCTIONS: DRAWING TO SCREEN & WINDOW OPTIONS---
def load_images():
	sheet = pg.image.load('chess_set.png').convert_alpha()
	pieces = ['bQ', 'bK', 'bR', 'bN', 'bB', 'bP',
			  'wQ', 'wK', 'wR', 'wN', 'wB', 'wP']
	for i in range(len(pieces)):
		PIECE_IMG[pieces[i]] = sheet.subsurface(i*50,0,50,50)

def draw_chessboard(screen):
	pg.draw.rect(screen, BROWN, (80,180,440,440))
	for i in range(8):
		for j in range(8):
			if (i+j) % 2 == 1:
				pg.draw.rect(screen, B_SQ,\
					(100 + j*SQ_SIZE, 200 + i*SQ_SIZE, SQ_SIZE, SQ_SIZE))
			else:
				pg.draw.rect(screen, W_SQ,\
					(100 + j*SQ_SIZE, 200 + i*SQ_SIZE, SQ_SIZE, SQ_SIZE))
	for i in range(8):
		# Draw digits 1-8 along side
		digits = coord_font.render(('{}'.format(i+1)), False, BLACK)
		screen.blit(digits, (88, 568 - 50*i))
		# Draw letters A-H (ASCII characters 65-72) along bottom
		letters = coord_font.render(('{}'.format(chr(65+i))), False, BLACK)
		screen.blit(letters, (122 + 50*i, 604))

def draw_pieces(screen, board):
	for i in range(8):
		for j in range(8):
			if board[i][j] != '  ':
				pc = board[i][j]
				screen.blit(PIECE_IMG[pc],(100 + j*SQ_SIZE, 200 + i*SQ_SIZE))

def highlight_sq(screen, sq, colour):
	# Draw red square 3 pixels thick by connecting the four points
	if colour == 'w':
		turn_col = WHITE
	else:
		turn_col = BLACK
	pg.draw.lines(screen, turn_col, True, [(100+sq[0]*50, 200+sq[1]*50),\
								      	   (150+sq[0]*50, 200+sq[1]*50),\
								           (150+sq[0]*50, 250+sq[1]*50),\
								           (100+sq[0]*50, 250+sq[1]*50)], 3)

def terminate():
	pg.quit()
	sys.exit()

def game_over():
	print('Game Over.')




# ---FUNCTIONS: CONVERSIONS---
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

def swap_col(colour):
	if colour == 'w':
		return 'b'
	else:
		return 'w'




# ---FUNCTIONS: MAIN LOGIC FUNCTIONS---
def is_valid_move(board, colour, move, move_log):
	# Rename all coordinate-related variable names
	from_x = move[0]
	from_y = move[1]
	to_x = move[2]
	to_y = move[3]
	x_diff = to_x - from_x
	y_diff = to_y - from_y
	x_direction = -1 if x_diff < 0 else 1
	y_direction = -1 if y_diff < 0 else 1

	# Rename all piece-related variable names
	piece = board[from_y, from_x]
	piece_colour = board[from_y, from_x][0]
	piece_kind = board[from_y, from_x][-1]

	# --- CHECK #1: check if 'to' and 'from' squares are the same.
	# --- CHECK #2: check if trying to move wrong coloured piece.
	# --- CHECK #3: check if trying to capture own piece.
	if (
			(from_x==to_x and from_y==to_y) or\
			(colour != piece_colour) or\
			(colour == board[to_y, to_x][0])):
		return False

	# --- CHECK #4: check if this is proper move for the piece to make.
	proper_move = False
	if piece=='wP' and (
			(
				# One square forward
				from_x == to_x and
				from_y - to_y == 1 and
				board[to_y, to_x] == '  ') or 
			(
				# Two squares forward
				from_x == to_x and
				from_y - to_y == 2 and
				from_y == 6 and
				board[to_y, to_x] == '  ' and
				board[to_y + 1, to_x] == '  ') or
			(
				# Capture
				abs(x_diff) == 1 and
				from_y - to_y == 1 and
				board[to_y, to_x].startswith('b'))
			):
		proper_move = True
	elif piece=='wP' and move_log and (	
				# Capture en passant
				# (Only possible after at least one move has been made)
				from_y == 3 and
				to_y == 2 and
				abs(x_diff) == 1 and
				move_log[-1]['piece'] == 'bP' and
				move_log[-1]['from_y'] == 1 and
				move_log[-1]['to_y'] == 3 and
				abs(move_log[-1]['to_x'] - from_x) == 1):
		proper_move = True
	elif piece=='bP' and (
			(
				# One square forward
				from_x == to_x and
				to_y - from_y == 1 and
				board[to_y, to_x] == '  ') or 
			(
				# Two squares forward
				from_x == to_x and
				to_y - from_y == 2 and
				from_y == 1 and
				board[to_y, to_x] == '  ' and
				board[to_y - 1, to_x] == '  ') or
			(
				# Capture
				abs(x_diff) == 1 and
				to_y - from_y == 1 and
				board[to_y, to_x].startswith('w'))
			):
		proper_move = True
	elif piece=='bP' and move_log and (
				# Capture en passant
				# (Only possible after at least one move has been made)
				from_y == 4 and
				to_y == 5 and
				abs(x_diff) == 1 and
				move_log[-1]['piece'] == 'wP' and
				move_log[-1]['from_y'] == 6 and
				move_log[-1]['to_y'] == 4 and
				abs(move_log[-1]['to_x'] - from_x) == 1):
		proper_move = True
	if piece_kind=='N':
			if (	(abs(x_diff)==2 and abs(y_diff)==1) or
					(abs(x_diff)==1 and abs(y_diff)==2)):
				proper_move = True
			else:
				proper_move = False
	elif piece_kind=='B':
		proper_move = (abs(x_diff) == abs(y_diff))
		# Check for any pieces along the way. If x_diff or y_diff is neg, step
		# direction = -1 & start at -1 (i.e. don't check origin square at i=0)
		for i in range(x_direction, x_diff, x_direction):
			for j in range(y_direction, y_diff, y_direction):
				if abs(i)==abs(j) and board[from_y+j, from_x+i] != '  ':
					proper_move = False
	elif piece_kind=='R':
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
	elif piece_kind=='Q' and move_log:
		# Check for any pieces along the way for 3 cases:
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
	elif piece_kind=='K' and move_log:
		proper_move = (
			(abs(y_diff)<=1 and abs(x_diff)<=1) or\
			((not move_log[-1]['lost_castle_ks']) and x_diff==2) or\
			((not move_log[-1]['lost_castle_qs']) and x_diff==-2))

	if proper_move == False:
		return False
	

	# --- CHECK #5: check if this move would move the king into check
	hypothetical_board = move_piece(board, move)
	would_be_check = is_check(hypothetical_board, swap_col(colour), move_log)
	if would_be_check:
		return False

	return True	


def does_valid_move_exist(board, colour, move_log):
	# Given a position, check all possible moves for all of given colour's pieces
	for i in range(8):
		for j in range(8):
			if board[i, j][0] == colour:
				for x in range(8):
					for y in range(8):
						valid_move = is_valid_move(
							board, colour, [j, i, y, x], move_log)
						if valid_move:
							return True
	return False


def is_check(board, colour, move_log):
	# Given a position, check if this colour is currently giving check
	opp_king = np.where(board == (str(swap_col(colour))+'K'))
	in_check = False
	for i in range(8):
	   	for j in range(8):
	   		if board[i, j][0] == colour:
	   			# Test if any pieces threatening to capture opponent's king
	   			move = [j, i, opp_king[1].item(), opp_king[0].item()]
	   			can_capture = is_valid_move(board, colour, move, move_log)
	   			if can_capture:
	   				in_check = True
	return in_check


def move_piece(board, move_coord):
	from_x = move_coord[0]
	from_y = move_coord[1]
	to_x = move_coord[2]
	to_y = move_coord[3]
	piece = board[from_y, from_x]
	piece_kind = board[from_y, from_x][-1]
	piece_colour = board[from_y, from_x][0]
	capture = board[to_y, to_x]

	new_board = board.copy()
	
	# En passant scenario: manually remove opponent's pawn
	if piece_kind=='P' and abs(from_x-to_x)==1 and capture=='  ':
		if piece_colour == 'w':
			new_board[to_y+1, to_x] = '  '
		else:
			new_board[to_y-1, to_x] = '  '

	# Pawn queening scenario: change pawn to a queen;
	# otherwise simply move that same piece to the new square
	if piece=='wP' and to_y==0:
		new_board[to_y, to_x] = 'wQ'
	elif piece=='bP' and to_y==7:
		new_board[to_y, to_x] = 'bQ'
	else:
		new_board[to_y, to_x] = new_board[from_y, from_x]
	new_board[from_y, from_x] = '  '
	
	# Castling scenarios: additional move required (jump rook over)
	if piece_kind=='K' and (to_x-from_x)==2:
		new_board[to_y, to_x+1] = '  '
		new_board[to_y, to_x-1] = str(piece_colour)+'R'
	elif piece_kind=='K' and (to_x-from_x)==-2:
		new_board[to_y, to_x-2] = '  '
		new_board[to_y, to_x+1] = str(piece_colour)+'R'

	return new_board




# ---FUNCTIONS: MOVE LOG & NOTATION---
def get_move_info(current_board, colour, move_coord, move_log):
	# move = New 'Move Log' entry
	move = {
		# Based on passed in information...
		'colour': colour,
		'piece': current_board[move_coord[1], move_coord[0]],
		'piece_colour': current_board[move_coord[1], move_coord[0]][0],
		'piece_kind': current_board[move_coord[1], move_coord[0]][-1],
		'from_x': move_coord[0],
		'from_y': move_coord[1],
		'to_x': move_coord[2],
		'to_y': move_coord[3],
		'moving_x': (move_coord[0] - move_coord[2]),
		'moving_y': (move_coord[1] - move_coord[3]),
		'capture': current_board[move_coord[3], move_coord[2]],
		'board_before_move': current_board,
		
		# To be calculated...
		'board_after_move': [],
		'opp_has_moves': None,
		'move_num': None,
		'ply_num': None,
		'is_check': None,
		'is_stalemate': None,
		'is_checkmate': None,
		'lost_castle_qs': False,
		'lost_castle_ks': False,
		'is_castle_qs': False,
		'is_castle_ks': False,
		'is_en_passant': None,
		'b_pieces_left': {'Q':1, 'R':2, 'N':2, 'B':2, 'P':8},
		'w_pieces_left': {'Q':1, 'R':2, 'N':2, 'B':2, 'P':8},
		'b_piece_pts': 39,
		'w_piece_pts': 39,
		'queening': None,
		'insuff_material': None
	}

	# For easier use within function
	if move_log:
		last_move = move_log[-1]
	else:
		last_move = None


	# New Board Game State; Whether Opponent Has Any Valid Moves Next Turn
	move['board_after_move'] = move_piece(current_board, move_coord)
	if not last_move:
		move['opp_has_moves'] = True
	else:
		move['opp_has_moves'] = does_valid_move_exist(move['board_after_move'],
												      swap_col(colour),
												      move_log)

	# Move Number; Ply Number
	if not last_move:
		move['ply_num'] = 1
	else:
		move['ply_num'] = last_move['ply_num'] + 1
	move['move_num'] = int(move['ply_num']/2 + 0.5)


	
	

	# Is Check; Is Checkmate; Is Stalemate
	move['is_check'] = is_check(move['board_after_move'], colour, move_log)
	move['is_checkmate'] = move['is_check'] and\
						   not move['opp_has_moves']
	move['is_stalemate'] = not move['is_check'] and\
						   not move['opp_has_moves']
	

	# Is En Passant; Castling Rights
	if len(move_log) > 2:
		print(move_log[-2]['ply_num'], ' <--> ', move['ply_num'])
		# Carry over state from last move (2 plies) starting on move 3
		move['lost_castle_qs'] = move_log[-2]['lost_castle_qs']
		move['lost_castle_ks'] = move_log[-2]['lost_castle_ks']
		move['is_en_passant'] = ((move['piece_kind'] == ('P')) and\
							     (abs(move['moving_x']) == 1) and\
							     (move['capture'] == '  '))
	if (
			(move['piece_kind']==('R') and move['from_x']==0) or\
			(move['piece_kind']==('K'))):
		move['lost_castle_qs'] = True
	if (
			(move['piece_kind']==('R') and move['from_x']==7) or\
			(move['piece_kind']==('K'))):
		move['lost_castle_ks'] = True


	# Castling
	move['is_castle_qs'] = (
			(move['piece_kind']==('K') and move['moving_x']==2) and\
			(not move['lost_castle_qs']))
	move['is_castle_ks'] = (
			(move['piece_kind']==('K') and move['moving_x']==-2) and\
			(not move['lost_castle_ks']))
	if move['is_castle_qs'] or move['is_castle_ks']:
		move['lost_castle_qs'] = True
		move['lost_castle_ks'] = True
	
	
	# Amount of Each Piece Left; Total Piece (Material) Points; Queening
	if last_move:
		move['b_pieces_left'] = last_move['b_pieces_left']
		move['w_pieces_left'] = last_move['w_pieces_left']
		move['b_piece_pts'] = last_move['b_piece_pts']
		move['w_piece_pts'] = last_move['w_piece_pts']
	
	pc_value = {'Q':9, 'R':5, 'N':3, 'B':3, 'P':1}
	pc_lost_kind = move['capture'][-1]

	if move['capture'].startswith('b'):
		move['b_pieces_left'][pc_lost_kind] -= 1
		move['b_piece_pts'] -= pc_value[pc_lost_kind]
	elif move['capture'].startswith('w'):
		move['w_pieces_left'][pc_lost_kind] -= 1
		move['w_piece_pts'] -= pc_value[pc_lost_kind]
	
	move['queening'] = (
			(move['to_y']==0 or move['to_y']==7) and\
			(move['piece_kind']=='P'))
	if move['queening'] and move['colour']=='b':
		move['b_pieces_left'][pc_lost_kind] += 1
		move['b_piece_pts'] += 9
	elif move['queening'] and move['colour']=='w':
		move['w_pieces_left']['Q'] += 1
		move['w_piece_pts'] += 9


	# Insufficient Material to Checkmate Anymore
	move['insuff_material'] = (
			(move['colour']=='b' and move['b_piece_pts'] < 10) or\
			(move['colour']=='w' and move['w_piece_pts'] < 10))

	return move


def get_move_algebraic(move):
	# If castles, return special notation
	if move['is_castle_ks']:
		return 'O-O'
	elif move['is_castle_qs']:
		return 'O-O-O'
	
	# If pawn is capturing, use letter of sq it came from; otherwise, drop the P
	move_return = ''
	if move['piece_kind']=='P' and move['capture']!='  ':
		move_return += str(cr_fr([move['from_x'], move['from_y']]))[0]
	elif move['piece_kind']!='P':
		move_return += move['piece_kind']

	if move['capture'] != '  ':
		move_return += 'x'

	# Destination square
	move_return += str(cr_fr([move['to_x'], move['to_y']]))

	if move['queening']:
		move_return += '=Q'

	if move['is_checkmate']:
		move_return += '#'
	elif move['is_stalemate']:
		move_return += '$'
	elif move['is_check']:
		move_return += '+'

	return move_return
	


def print_move_list(move_log):
	# Convert move_log to list of moves in algebraic chess notation
	move_list = []
	for i in range(1, len(move_log)):
		new_move = get_move_algebraic(move_log[i])
		move_list.append(new_move)
		
	print('---Move List---')
	for i in range(0, len(move_list), 2):
		offset = 7 - len(move_list[i])
		if i == (len(move_list) - 1):
			print(move_list[i])
		else:
			print(move_list[i], ' '*offset, move_list[i+1])
			
		




# ---MAIN GAME LOOP---
def main():
	gs = GameState()
	load_images()
	clk = ()
	print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
	print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
	print('*'*70 + '\n' + ' '*32 + 'NEW GAME' + '\n' + '*'*70)
	print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
	while True:
		win.fill(GREEN)
		draw_chessboard(win)
		draw_pieces(win, gs.board)
		if clk:
			# Move 3 onwards (ply = 5+), check for the 3 game over scenarios:
			# Checkmate; stalemate; both sides have insufficient material
			if len(gs.move_log) >= 5 and (
					(gs.move_log[-1]['is_checkmate']) or\
					(gs.move_log[-1]['is_stalemate']) or\
					(
						(gs.move_log[-1]['insuff_material']) and\
						(gs.move_log[-2]['insuff_material']))
					):
				game_over()
			elif clk[0] < 100 or clk[0] >= 500 or clk[1] < 200 or clk[1] >= 600:
				gs.move_coord = [] # Click is out of bounds: reset list of coordinates
			elif len(gs.move_coord) < 4:
				gs.move_coord.append((clk[0]-100) // SQ_SIZE)
				gs.move_coord.append((clk[1]-200) // SQ_SIZE)
				if len(gs.move_coord) == 4:
					valid_move = is_valid_move(
							gs.board, gs.colour, gs.move_coord, gs.move_log)
					if valid_move:
						new_move_info = get_move_info(
							gs.board, gs.colour, gs.move_coord, gs.move_log)
						gs.move_log.append(new_move_info)
						gs.board = move_piece(gs.board, gs.move_coord)
						gs.move_coord = []
						gs.colour = swap_col(gs.colour)
					else:
						# Promote old 'to' square to new 'from' square
						gs.move_coord[0] = gs.move_coord[2]
						gs.move_coord[1] = gs.move_coord[3]
						del gs.move_coord[2:]
			clk = ()
		if (	
				(len(gs.move_coord) == 2) and\
				(gs.board[gs.move_coord[1]][gs.move_coord[0]].startswith(gs.colour))):
			# Piece is selected and it's that colour's turn to move)
			highlight_sq(win, gs.move_coord, gs.colour)		

		event = pg.event.get()
		for e in event:
			if e.type == MOUSEBUTTONDOWN:
				clk = e.pos
			if e.type == QUIT:
				terminate()
			if e.type == KEYDOWN:
				pass
			if e.type == KEYUP:
				# ------KEYS---------------
				#   b = Print [B]oard state
				#   m = [M]ove Information
				#   t = [T]esting
				#   q = [Q]uit
				if e.key == K_b:
					print('\n' + str(gs.board) + '\n')
				if e.key == K_m and gs.move_log:
					print('\n\n')
					for key in gs.move_log[-1]:
						if str(gs.move_log[-1][key]).startswith('board'):
							print(key, ' = \n', gs.move_log[-1][key])
						else:
							print(key, ' = ', gs.move_log[-1][key])
					print('\n')
				if e.key == K_t and gs.move_log:
					print_move_list(gs.move_log)
				if e.key == K_ESCAPE or e.key == K_q:
					terminate()

		pg.display.update()
		clock.tick(FPS)

if __name__ == "__main__":
	main()