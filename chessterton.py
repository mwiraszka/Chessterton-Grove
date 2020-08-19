# CHESSTERTON GROVE
# by Michal Wiraszka

# A chess game made entirely on Python, making heavy use of its Pygame and Numpy modules.


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
# 19.08.20 major redesign - Move() & GameState() classes re-defining (in progress)


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

pg.font.get_fonts()
FONT_COORD = pg.font.SysFont('helvetica', 18, False, False)


# ---PYGAME SETUP--------------------------------------------------------------
pg.init()
win = pg.display.set_mode((WIN_W, WIN_H), 0, 32)
pg.display.set_caption("Chessterton Grove v1.0")
clock = pg.time.Clock()


# ---CLASSES-------------------------------------------------------------------
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
		self.on_move = 1
		self.is_turn = 'w'
		self.is_checkmate = False
		self.is_stalemate = False
		self.is_insuff_material = False
		self.click_coord = [] # Click's coordinates [x, y]
		self.move_coord = []  # Move's coordinates [from-x, from-y, to-x, to-y]
		self.moves = []


class Move():
	def __init__(self, gs, mc):
	# Takes GameState() object and move coord list [from-x, from-y, to-x, to-y]
		# General Move Information
		self.move_num = gs.on_move
		self.ply_num = int((self.move_num + 1) / 2)
		self.last_move = [gs.moves[-1] if (not self.move_num == 1) else None
		self.turn = gs.is_turn

		# Location on Board Information
		self.from_x = mc[0]
		self.from_y = mc[1]
		self.to_x = mc[2]
		self.to_y = mc[3]
		self.x_diff = self.to_x - self.from_x
		self.y_diff = self.to_y - self.from_y
		self.x_direction = -1 if x_diff < 0 else 1
		self.y_direction = -1 if x_diff < 0 else 1

		# Piece Information
		self.piece = self.board[self.from_y, self.from_x]
		self.piece_kind = self.piece[1]
		self.piece_colour = self.piece[0]
		
		# Special Move Attributes
		self.is_capture = self.board[self.to_y, self.to_x]
		
		self.is_double_pawn_push = ((self.piece_kind == 'P') and\
								    (self.x_diff == 2) and\
								    (abs(self.y_diff) == 2) and\
								    (self.from_y == 1 or self.from_y == 6))

		self.is_check = check_if_check()


		self.valid_moves_left = does_valid_move_exist(self.board_after,            ####################
												   swap(self.turn),			# moves need to be sent?
												   game_state.moves)			# maybe only .last_move needed?
		
		self.opp_king = np.where(self.board == (str(swap(self.turn))+'K'))
		for i in range(8):
	   		for j in range(8):
	   			if board[i, j][0] == self.turn:
	   			
	   			move = [j, i, opp_king[1].item(), opp_king[0].item()]
	   			can_capture = is_valid_move(board, colour, move, moves)
	   			self.is_check = True



		self.stalemate = not self.valid_moves_left and not self.check
		self.checkmate = not self.valid_moves_left and self.check

		if (
				(len(game_state.moves) > 3) and\
				(self.piece_kind == 'P') and\
				(abs(self.x_diff) == 1) and\
				(self.capture == '  ') and\
				(self.last_move.double_pawn_push) and\
				(abs(self.last_move.x_to - self.x_to) == 1)\
				(self.last_move.y_to == self.y_to)
				):
			self.is_en_passant = True
		else:
			self.is_en_passant = False


		if len(game_state.moves) > 2:
			self.lost_castle_qs = self.prev_turn.lost_castle_qs
			self.lost_castle_ks = self.prev_turn.lost_castle_ks
		else:
			self.lost_castle_qs = False
			self.lost_castle_ks = False
			if self.piece_kind == 'K':
				self.lost_castle_qs = True
				self.lost_castle_ks = True
			elif self.piece_kind == 'R' and self.from_x == 0:
				self.lost_castle_qs = True
			elif self.piece_kind == 'R' and self.from_x == 7:
				self.lost_castle_ks = True	
		
		self.is_castle_qs = False
		self.is_castle_ks = False
		if (
				(len(game_state.moves) > 6) and\
				(self.piece_kind == 'K') and\
				(self.y_diff == 0) and\
				(self.x_diff == 2)
				):
			if (
					(not self.last_move.lost_castle_qs) and\
					(self.x_direction == -1) and\
					(self.board[self.from_y][(self.from_x - 1)] == ' ') and\
					(self.board[self.from_y][(self.from_x - 2)] == ' ') and\
					(self.board[self.from_y][(self.from_x - 3)] == ' ')):
				self.is_castle_qs = True
			elif (
					(not self.last_move.lost_castle_ks) and\
					(self.x_direction == 1) and\
					(self.board[self.from_y][(self.from_x + 1)] == ' ') and\
					(self.board[self.from_y][(self.from_x + 2)] == ' ')):
				self.is_castle_ks = True

		if self.prev_turn:
			self.pieces_left = self.last_move.pieces_left
			self.pieces_points = self.last_move.pieces_points
		else:
			self.pieces_left = {'Q':(1,1), 'R':(2,2),
								'N':(2,2), 'B':(2,2), 'P':(8,8)}
			self.pieces_points = (39, 39)
		pc_value = {'Q':9, 'R':5, 'N':3, 'B':3, 'P':1}
		if 
		self.queening = None		
	}
	# Amount of Each Piece Left; Total Piece (Material) Points; Queening
	

	
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





# ---CONVERSIONS---------------------------------------------------------------
def to_file_rank(column_row):
	# <int list> {0,1,..,7}{0,1,..,7}   -->   <str>  {a,b,..,h}{1,2,..,8}
	file_rank = chr(97 + column_row[0]) + str(8 - column_row[1])
	return file_rank

def to_column_row(file_rank):
	# <str>  {a,b,..,h}{1,2,..,8}   -->   <int list> {0,1,..,7}{0,1,..,7}
	column_row = [ord(file_rank[0]) - 97, int(file_rank[1]) - 1]
	return column_row

def to_move_coord(click_coord):
	return ((click_coord[0]-100)//SQ_SIZE, (click_coord[1]-200)//SQ_SIZE)
	
def swap(turn):
	if colour == 'w':
		return 'b'
	else:
		return 'w'

def to_algebraic(move):
	# <dict>    -->    <str> in alegraic notation, like exd4+ f8=Q#
	# If not Castles; append one character to notation string one at a time
	if move['is_castle_ks']:
		return 'O-O'
	elif move['is_castle_qs']:
		return 'O-O-O'
	
	move_return = ''
	if move['piece_kind']=='P' and move['capture']!='  ':
		# If Pawn Capture, use letter of sq it came from; otherwise, drop the P
		origin_sq = str(to_file_rank([move['from_x'], move['from_y']]))[0]
		move_return += origin_sq
	elif move['piece_kind']!='P':
		move_return += move['piece_kind']
	
	if move['capture'] != '  ':
		move_return += 'x'

	destination_sq = str(to_file_rank([move['to_x'], move['to_y']]))
	move_return += destination_sq
	
	if move['queening']:
		move_return += '=Q'

	if move['is_checkmate']:
		move_return += '#'
	elif move['is_stalemate']:
		move_return += '$'
	elif move['is_check']:
		move_return += '+'

	return move_return





# ---DRAW ON SCREEN---------------------------------------------------------
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
		digits = FONT_COORD.render(('{}'.format(i+1)), False, BLACK)
		screen.blit(digits, (88, 568 - 50*i))
		# Draw letters A-H (ASCII characters 65-72) along bottom
		letters = FONT_COORD.render(('{}'.format(chr(65+i))), False, BLACK)
		screen.blit(letters, (122 + 50*i, 604))

def draw_pieces(screen, board):
	for i in range(8):
		for j in range(8):
			if board[i][j] != '  ':
				pc = board[i][j]
				screen.blit(PIECE_IMG[pc],(100 + j*SQ_SIZE, 200 + i*SQ_SIZE))

def highlight_sq(screen, colour, point):
	# Draw red square 3 pixels thick starting on given point, p
	if colour == 'w':
		turn_col = WHITE
	else:
		turn_col = BLACK
	pg.draw.lines(screen, turn_col, True, [(100 + p[0]*50, 200 + p[1]*50),\
								      	   (150 + p[0]*50, 200 + p[1]*50),\
								           (150 + p[0]*50, 250 + p[1]*50),\
								           (100 + p[0]*50, 250 + p[1]*50)], 3)




# ---PRINT TO SHELL------------------------------------------------------------
def print_new_game():
	print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
	print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
	print('*'*70 + '\n' + ' '*32 + 'NEW GAME' + '\n' + '*'*70)
	print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')

def print_move_list(moves):
	# First, convert moves list to algebraic chess notation, one move at a time
	move_list = []
	for i in range(len(moves)):
		new_move = to_algebraic(moves[i])
		move_list.append(new_move)
	# Print out with offset compensation, so moves show up in straight columns
	print('   ---Move List---')
	for i in range(len(move_list)):
		offset = 5 - len(move_list[i])
		if i % 2 == 0:
			if int((i+3)/2) < 10:
				print(end=' ')  # Extra space before one-digit numbers
			print(str(int((i+3)/2)), '.  ', move_list[i], ' '*offset, end=' ')
		else:
			print(move_list[i])
	print('\n\n')
	
def print_last_move(last_move):
	# Print out each move 'attribute' on own line (extra spaces around np.arrays)
	print('   ---Last Move\'s Info---')
	for key in last_move:
		if isinstance(last_move[key], np.ndarray):
			print(key, ' = \n', last_move[key], '\n')
		else:
			print(key, ' = ', last_move[key])
	print('\n\n')















	
def is_move_valid(board, moves, new_move):
	from_x = move[0]
	from_y = move[1]
	to_x = move[2]
	to_y = move[3]
	x_diff = to_x - from_x
	y_diff = to_y - from_y
	x_direction = -1 if x_diff < 0 else 1
	y_direction = -1 if y_diff < 0 else 1

	piece = board[from_y, from_x]
	piece_colour = board[from_y, from_x][0]
	piece_kind = board[from_y, from_x][-1]

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
	elif piece=='wP' and moves and (	
				# Capture en passant
				# (Only possible after at least one move has been made)
				from_y == 3 and
				to_y == 2 and
				abs(x_diff) == 1 and
				moves[-1]['piece'] == 'bP' and
				moves[-1]['from_y'] == 1 and
				moves[-1]['to_y'] == 3 and
				abs(moves[-1]['to_x'] - from_x) == 1):
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
	elif piece=='bP' and moves and (
				# Capture en passant
				# (Only possible after at least one move has been made)
				from_y == 4 and
				to_y == 5 and
				abs(x_diff) == 1 and
				moves[-1]['piece'] == 'wP' and
				moves[-1]['from_y'] == 6 and
				moves[-1]['to_y'] == 4 and
				abs(moves[-1]['to_x'] - from_x) == 1):
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
	elif piece_kind=='Q' and moves:
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
	elif piece_kind=='K' and moves:
		# All of the following conditions must be met:
		# 1) movement of 1 square in any direction, or 2 to side when castling
		# 2) not walking into opponent king
		proper_move = (
			(abs(y_diff)<=1 and abs(x_diff)<=1) or\
			((not moves[-1]['lost_castle_ks']) and x_diff==2) or\
			((not moves[-1]['lost_castle_qs']) and x_diff==-2))
		if proper_move == False:

	if proper_move == False:
		return False
	

	# --- CHECK #5: check if this move would move the king into check
	hypothetical_board = move_piece(board, move)
	would_be_check = is_check(hypothetical_board, swap(colour), moves)
	if would_be_check:
		return False

	return True	


def any_valid_moves_left(board, colour, moves):
	for i in range(8):
		for j in range(8):
			if board[i, j][0] == colour:
				for x in range(8):
					for y in range(8):
						valid_move = is_valid_move(
							board, colour, [j, i, y, x], moves)
						if valid_move:
							return True
	return False




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



























































# ---FUNCTIONS: CLICK EVENT----------------------------------------------------
def is_click_valid(click_coord):
	if not ((click_coord[0] < 100 or click_coord[0] >= 500) or\
	   		(click_coord[1] < 200 or click_coord[1] >= 600)):
		return True
	else:
		return False


def is_move_ok(board, colour, move_coord):
	# Basic validations done first:  1. 'to' and 'from' not same square
	#								 2. trying to move wrong piece
	# 								 3. trying to move onto own piece
	from_x, from_y, to_x, to_y = move_coord
	if (
			(from_x, to_x) == (to_x, to_y)) or\
			(colour != board[from_y][from_x]) or\
			(colour == board[to_y, to_x][0])
			):
		return False


# ---GAME OVER-----------------------------------------------------------------
def is_game_over(moves):
	# Checkmate, stalemate, or both sides have insufficient material
	if moves[-1]['is_checkmate']:
		return 'Checkmate!'
	elif moves[-1]['is_stalemate']:
		return 'Stalemate!'
	elif moves[-1]['insuff_mat'] and moves[-2]['insuff_mat']:
		return 'Both sides have insufficient material!'
	return ''

def game_over(message):
	print(message, ' Game Over.')

def terminate():
	pg.quit()
	sys.exit()

# ---MAIN GAME LOOP------------------------------------------------------------
def main():
	gs = GameState()
	load_images()
	print_new_game()
	while:
		win.fill(GREEN)
		draw_chessboard(win)
		draw_pieces(win, gs.board)
		# From third move (ply = 5) onwards, check if game is over
		if gs.moves > 5:
			game_over_notice = is_game_over(gs.moves)
			if not game_over_notice.empty():
				game_over(game_over_notice)

		# For every registered click:
		# Check if click valid --> Check if move valid --> Make move
		if clicked:
			click valid = is_click_valid(gs.click_coord)
			if click_valid:
				gs.move_coord = to_move_coord(gs.click_coord)
				if len(gs.move_coord) < 4:
					# If a piece is selected and it's that colour to move)
					if ((len(gs.move_coord) == 2) and\
					    (gs.board[gs.move_coord[1]][gs.move_coord[0]]\
								.startswith(gs.turn))):
						highlight_sq(win, gs.turn, gs.move_coord)
				elif len(gs.move_coord) == 4:
					move_ok = is_move_ok(gs.board, gs.turn, gs.move_coord)
					gs.new_move = get_move_info(gs.board,
												gs.turn,
												gs.moves,
												gs.move_coord)
					move_valid = is_move_valid(gs.board, gs.moves, gs.new_move)
				if move_valid:
					gs.board = move_piece(gs.board, gs.move_coord)
					gs.moves.append(gs.new_move)
					gs.move_coord = []
					gs.turn = swap(gs.turn)
				else:
					# Promote old 'to' square to become new 'from' square
					gs.move_coord[0] = gs.move_coord[2]
					gs.move_coord[1] = gs.move_coord[3]
					del gs.move_coord[2:]
		else:
			# Reset click variables once nothing left to do with them
			gs.click_coord = []
			clicked = ()


		# ---EVENTS---
		event = pg.event.get()
		for e in event:
			if e.type == MOUSEBUTTONDOWN:
				clicked = e.pos
			if e.type == QUIT:
				terminate()
			if e.type == KEYDOWN:
				pass
			if e.type == KEYUP:
				# ------KEYS---------------
				#   b = Print [B]oard state
				#   m = [M]ove Information
				#   l = [L]ist of Moves
				#   t = [T]esting
				#   q = [Q]uit
				if e.key == K_b:
					print('\n' + str(gs.board) + '\n')
				if e.key == K_m and gs.moves:
					print_last_move(gs.moves[-1])
				if e.key == K_l and gs.moves:
					print_move_list(gs.moves)
				if e.key == K_t:
					pass
				if e.key == K_ESCAPE or e.key == K_q:
					terminate()

		pg.display.update()
		clock.tick(FPS)

if __name__ == "__main__":
	main()