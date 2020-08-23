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
# 19.08.20 major redesign - Move(), GameState(), check_if_check re-defining (in progress)
# 19.08.20 major redesign finished; about to start debugging
# 20.08.20 split validations into separate functions; better organizing functions into classes (in progress)
# 21.08.20 major reorganizing and debugging cont'd
# 22.08.20 misc debugging cont'd



# ---IMPORTS---
import sys
import pygame as pg
import numpy as np
from pygame.locals import *
import copy

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
PIECE_VAL = {'Q':9, 'R':5, 'N':3, 'B':3, 'P':1}


# ---PYGAME SETUP--------------------------------------------------------------
pg.init()
win = pg.display.set_mode((WIN_W, WIN_H), 0, 32)
pg.display.set_caption("Chessterton Grove v1.0")
clock = pg.time.Clock()


# ---FONT CONSTANTS------------------------------------------------------------
pg.font.get_fonts()
FONT_COORD = pg.font.SysFont('helvetica', 18, False, False)


# ---CLASSES-------------------------------------------------------------------
class GameState:
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
		self.ply_num = 1
		self.turn = 'w'
		self.pieces = {'w': {'Q':1, 'R':2, 'N':2, 'B':2, 'P':8},
			           'b': {'Q':1, 'R':2, 'N':2, 'B':2, 'P':8}}
		self.pieces_pts = {'w': 39, 'b': 39}
		self.insuff_mat = self.pieces_pts['w']<1 and self.pieces_pts['b']<1
		self.castling_rights_qs = {'w': True, 'b': True}
		self.castling_rights_ks = {'w': True, 'b': True}
		self.moves = []
		self.check = False
		self.stalemate = False
		self.checkmate = False


	def update_board(self, move):
		new_board = self.board.copy()
		
		# Update destination and origin squares
		if move.queening:
			new_board[move.to_y, move.to_x] = str(move.piece_colour)+'Q'
		else:
			new_board[move.to_y, move.to_x] = move.piece
		new_board[move.from_y, move.from_x] = '  '
		
		# Castling scenarios: additionally jump rook over
		if move.is_castle_qs():
			new_board[move.to_y, move.to_x-2] = '  '
			new_board[move.to_y, move.to_x+1] = str(move.piece_colour)+'R'
		elif move.is_castle_ks():
			new_board[move.to_y, move.to_x+1] = '  '
			new_board[move.to_y, move.to_x-1] = str(move.piece_colour)+'R'
		
		# En passant scenario: additionally manually remove opponent's pawn
		if move.en_passant:
			if move.piece_colour == 'w':
				new_board[move.to_y + 1, move.to_x] = '  '
			else:
				new_board[move.to_y - 1, move.to_x] = '  '
		
		self.board = new_board


	def valid_moves_left(self):
		print('VALID MOVES LEFT for', self.turn, '?')
		print(self.board)
		for from_row, from_col in np.ndindex(self.board.shape):
			on_sq = (self.board[from_row, from_col])
			if on_sq.startswith(self.turn):
				for to_row in range(8):
					for to_col in range(8):
						from_sq = [from_row, from_col]
						to_sq = [to_row, to_col]
						print('checking', on_sq, 'from square', from_sq, 'to square', to_sq)
						if from_sq != to_sq:
							print('making hypothetical move.')
							hyp_move = Move(self, from_sq, to_sq)
							print('checking its validity')
							move_valid = hyp_move.is_valid(self, True)
							if move_valid == True:
								print('found a valid move!', from_sq, 'to', to_sq)
								return True
		return False

	def is_check(self, turn):
		# 'turn' is the side supposedly giving check, therefore opponent's king is swap(turn)
		king_loc = np.where(self.board == swap(turn)+'K')
		king = [king_loc[1].item(), king_loc[0].item()]
		counter = 0
		# pieces verified in order of general likelihood of giving check
		for piece_kind in ['Q', 'R', 'B', 'N', 'P']:
			piece_loc = np.where(self.board == turn+piece_kind)
			for i in range(len(piece_loc[0])):
				piece = [piece_loc[1][i], piece_loc[0][i]]
				counter += 1
				hyp_move = Move(self, piece, king)
				# (..., only_piece_validity = True, cant_capture_king = False)
				valid = hyp_move.is_valid(self, True, False)
				if valid:
					return True
		return False

	def is_stalemate(self):
		print('checking if stalemate...')
		valid_moves = self.valid_moves_left()
		return not valid_moves and not self.check

	def is_checkmate(self):
		print('checking if checkmate...')
		valid_moves = self.valid_moves_left()
		return not valid_moves and self.check

	def is_game_over(self):
		if self.checkmate:
			return 'Checkmate!'
		elif self.stalemate:
			return 'Stalemate!'
		elif self.insuff_mat:
			return 'Both sides have insufficient material!'
		return ''

	def count_pieces(self):
		if len(self.moves < 3):
			return self.pieces
		else:
			pieces = {'w': {'Q':0, 'R':0, 'N':0, 'B':0, 'P':0},
			          'b': {'Q':0, 'R':0, 'N':0, 'B':0, 'P':0}}
			for colour in pieces.keys():
				for kind in pieces[colour].keys():
					for piece in np.where(self.board == colour+kind):
						pieces[colour][kind] += 1
		return pieces
		
	def count_points(self):
		if len(self.moves < 3):
			return self.pieces_pts
		else:
			pieces_pts = {'w': 0, 'b': 0}
			for colour in self.pieces.keys():
				for kind in pieces[colour].keys():
					pieces_pts[colour][kind] *= PIECE_VAL[kind]
		return pieces_pts

	def make_move(self, new_move):
		self.update_board(new_move)
		self.check = self.is_check(self.turn)
		self.stalemate = self.is_stalemate()
		print('result...', self.stalemate)
		self.checkmate = self.is_checkmate()
		print('result...', self.checkmate)
		print('final results... check, stalemate, checkmate:', self.check, self.stalemate, self.checkmate)

		if (
				(new_move.is_castle_qs()) or
				(new_move.piece_kind == 'R' and new_move.from_x == 0)
				):
			self.castling_rights_qs[self.turn] = False
		if (
				(new_move.is_castle_ks()) or
				(new_move.piece_kind == 'R' and new_move.from_x == 7)
				):
			self.castling_rights_ks[self.turn] = False
		if new_move.piece_kind == 'K':
			self.castling_rights_qs[self.turn] = False
			self.castling_rights_ks[self.turn] = False

		self.moves.append(new_move)
		self.ply_num += 1
		self.turn = swap(self.turn)


class Move:
	def __init__(self, gs, sq_from, sq_to):
		self.ply_num = gs.ply_num
		self.move_num = (self.ply_num + 1) // 2
		self.turn = gs.turn

		self.from_x = sq_from[0]
		self.from_y = sq_from[1]
		self.to_x = sq_to[0]
		self.to_y = sq_to[1]
		self.x_diff = self.to_x - self.from_x
		self.y_diff = self.to_y - self.from_y
		self.x_dir = -1 if self.x_diff < 0 else 1
		self.y_dir = -1 if self.y_diff < 0 else 1

		self.piece = gs.board[self.from_y, self.from_x]
		self.piece_colour = self.piece[0]
		self.piece_kind = self.piece[1]
		self.dest_sq = gs.board[self.to_y, self.to_x]
		
		self.queening = ((self.to_y == 0 and self.piece == 'wP') or
					     (self.to_y == 7 and self.piece == 'bP'))
		self.en_passant = self.is_en_passant(gs.moves[-1]) if gs.moves else False

	def is_valid(self, gs, only_piece_validity=False, cant_capture_king=True):
		if not only_piece_validity:
			walk_into = self.is_walk_into_check(gs)
			if walk_into:
				print('walking into check... invalid.')
				return False
		
		if cant_capture_king:
			if self.dest_sq.endswith('K'):
				print('capturing king... invalid.')
				return False

		if self.piece_kind == 'P':
			valid_dir = ((self.piece_colour == 'w' and self.y_dir == -1) or
					     (self.piece_colour == 'b' and self.y_dir == 1))
			valid_capture = ((abs(self.x_diff) == 1 and abs(self.y_diff) == 1) and
							 (gs.board[self.to_y, self.to_x] != '  '))
			valid_1_sq = ((self.x_diff == 0 and abs(self.y_diff) == 1) and
					      (gs.board[self.to_y, self.to_x] == '  '))
			mid_point = int((self.to_y+self.from_y)/2)
			valid_2_sq = ((self.x_diff == 0 and abs(self.y_diff) == 2) and
					      (gs.board[self.to_y, self.to_x] == '  ') and
					      (gs.board[mid_point, self.to_x] == '  ') and
					      (self.from_y == 1 or self.from_y == 6))
			return (valid_dir and (self.en_passant or
								   valid_capture or
								   valid_1_sq or
								   valid_2_sq))
						  
		elif self.piece_kind == 'N':
			return ((abs(self.x_diff) == 2 and abs(self.y_diff) == 1) or
				    (abs(self.x_diff) == 1 and abs(self.y_diff) == 2))

		# For B, R, and Q: check for obstacles on all sq along the piece's,
		# path, except the sq it's on and the destination sq (verified earlier)
		elif self.piece_kind == 'B':
			if abs(self.x_diff) == abs(self.y_diff):
				for i in range(1, abs(self.y_diff)):
					sq_y = self.from_y + (i*self.y_dir)
					sq_x = self.from_x + (i*self.x_dir)
					if gs.board[sq_y, sq_x] != '  ':
						return False
				return True
			return False

		elif self.piece_kind == 'R':
			if self.y_diff == 0:
				for i in range(1, abs(self.x_diff)):
					if gs.board[self.from_y, self.from_x+(i*self.x_dir)] != '  ':
						return False
				return True
			elif self.x_diff == 0:
				for i in range(1, abs(self.y_diff)):
					if gs.board[self.from_y+(i*self.y_dir), self.from_x] != '  ':
						return False
				return True
			else:
				return False

		elif self.piece_kind == 'Q':
			if self.y_diff == 0:
				for i in range(1, abs(self.x_diff)):
					if gs.board[self.from_y, self.from_x+(i*self.x_dir)] != '  ':
						return False
				return True
			elif self.x_diff == 0:
				for i in range(1, abs(self.y_diff)):
					if gs.board[self.from_y+(i*self.y_dir), self.from_x] != '  ':
						return False
				return True
			elif abs(self.x_diff) == abs(self.y_diff):
				for i in range(1, abs(self.y_diff)):
					sq_y = self.from_y + (i*self.y_dir)
					sq_x = self.from_x + (i*self.x_dir)
					if gs.board[sq_y, sq_x] != '  ':
						return False
				return True
			else:
				return False 

		elif self.piece_kind == 'K':
			valid_1_sq = abs(self.x_diff) < 2 and abs(self.y_diff) < 2
			valid_castle_qs = ((self.y_diff == 0 and self.x_diff == -2) and
							   (gs.castling_rights_qs[self.turn]) and
							   (gs.board[self.from_y, self.from_x - 1] == '  ') and
		   					   (gs.board[self.from_y, self.from_x - 2] == '  ') and
		   					   (gs.board[self.from_y, self.from_x - 3] == '  '))
			valid_castle_ks = ((self.y_diff == 0 and self.x_diff == 2) and
							   (gs.castling_rights_ks[self.turn]) and
							   (gs.board[self.from_y, self.from_x + 1] == '  ') and
		   					   (gs.board[self.from_y, self.from_x + 2] == '  '))
			return valid_1_sq or valid_castle_qs or valid_castle_ks

	def is_en_passant(self, last_move):
		if last_move:
			# Last move was a two-sq pawn move to the sq adjacent to where this move
			# originates from, and this pawn makes a capture behind the en-pass pawn.
			return ((self.piece_kind == 'P') and
	 			    (last_move.piece_kind == 'P') and
	 			    (abs(last_move.y_diff) == 2) and
	 			    (last_move.to_y == self.from_y) and
	 			    (abs(last_move.from_x - self.from_x) == 1) and
	 			    (last_move.to_x == self.to_x))


	def is_capture(self):
		return (self.en_passant or move.dest_sq != '  ')

	def is_castle_qs(self):
		return (self.piece_kind == 'K' and self.x_diff == -2)

	def is_castle_ks(self):
		return (self.piece_kind == 'K' and self.x_diff == 2)

	def is_walk_into_check(self, gs):
		# Were this move made, would an opponent's piece be checking you
		hyp_gs = copy.copy(gs)
		hyp_gs.update_board(self)
		is_check = hyp_gs.is_check(swap(self.turn))
		return is_check




# ---CONVERSIONS---------------------------------------------------------------
def to_file_rank(column_row):
	# <int list> {0,1,..,7}{0,1,..,7}   -->   <str>  {a,b,..,h}{1,2,..,8}
	file_rank = chr(97 + column_row[0]) + str(8 - column_row[1])
	return file_rank

def to_column_row(file_rank):
	# <str>  {a,b,..,h}{1,2,..,8}   -->   <int list> {0,1,..,7}{0,1,..,7}
	column_row = [ord(file_rank[0]) - 97, int(file_rank[1]) - 1]
	return column_row

def to_sq_xy(click_xy):
	return ((click_xy[0]-100) // SQ_SIZE, (click_xy[1]-200) // SQ_SIZE)

def swap(turn):
	return 'b' if turn == 'w' else 'w'

def to_algebraic(move):
	# Move() object    -->    <str> in alegraic notation, like exd4+ f8=Q#
	# If not Castles; append characters to string one at a time
	if move.is_castle_ks():
		return 'O-O'
	elif move.is_castle_qs():
		return 'O-O-O'
	
	if move.piece_kind != 'P':
		move_return += move.piece_kind
	else:
		# If pawn move, use only letter from square it came from
		origin_sq = str(to_file_rank([move.from_x, move.from_y]))[0]
		move_return += origin_sq
		
	if move.is_capture():
		move_return += 'x'

	destination_sq = str(to_file_rank([move.to_x, move.to_y]))[0]
	move_return += destination_sq
	
	if move.queening:
		move_return += '=Q'

	if move.is_checkmate():
		move_return += '#'
	elif move.is_stalemate():
		move_return += '$'
	elif move.is_check():
		move_return += '+'

	return move_return




# ---CLICKING EVENTS & DRAWING TO SCREEN---------------------------------------
def load_images():
	sheet = pg.image.load('chess_set.png').convert_alpha()
	pieces = ['bQ', 'bK', 'bR', 'bN', 'bB', 'bP',
			  'wQ', 'wK', 'wR', 'wN', 'wB', 'wP']
	for i in range(len(pieces)):
		PIECE_IMG[pieces[i]] = sheet.subsurface(i*50, 0, 50, 50)

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

def highlight_sq(screen, colour, p):
	# Draw red square 3 pixels thick starting on given point, p
	if colour == 'w':
		turn_col = WHITE
	else:
		turn_col = BLACK
	pg.draw.lines(screen, turn_col, True, [(100 + p[0]*50, 200 + p[1]*50),
								      	   (150 + p[0]*50, 200 + p[1]*50),
								           (150 + p[0]*50, 250 + p[1]*50),
								           (100 + p[0]*50, 250 + p[1]*50)], 3)

def is_click_valid(click_xy):
	within_bounds = ((click_xy[0] >= 100 and click_xy[0] <= 500) and
				         (click_xy[1] >= 200 and click_xy[1] <= 600))
	return within_bounds




# ---PRINT TO SHELL------------------------------------------------------------
def print_new_game():
	print_spaces()
	print('*'*68 + '\n' + ' '*32 + 'NEW GAME' + '\n' + '*'*68)

def print_spaces():
	print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
	print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')

def print_current_gamestate(gs, click_xy='N/A', sq_from='N/A', sq_to='N/A'):
	# Print out each gamestate 'attribute' on separate lines under neat columns
	print('-'*24, 'Current Game State', '-'*24)
	names = ['Board:',
			 'Ply Number:',
			 'Turn:',
			 'Check?',
			 'Stalemate?',
			 'Checkmate?',  
			 'Insuff. Mat.?',
			 'Pieces Left (white):',
			 'Pieces Left (black):',
		     'Points of Material:', 
			 'QS Castling Rights (white):',
			 'KS Castling Rights (white):',
			 'QS Castling Rights (black):',
			 'KS Castling Rights (black):',
			 'Moves Stored:',
			 ' ',
			 '--- User input ---',
			 'Click (X,Y):',
			 'From Square Selected:',
			 'To Square Selected:']
	values = [gs.board, gs.ply_num, gs.turn, gs.check, gs.stalemate,
			  gs.checkmate, gs.insuff_mat, gs.pieces['w'], gs.pieces['b'],
			  gs.pieces_pts, gs.castling_rights_qs['w'], gs.castling_rights_ks['w'],
			  gs.castling_rights_qs['b'], gs.castling_rights_ks['b'],
			  len(gs.moves), ' ', ' ', click_xy, sq_from, sq_to]
	for name in range(len(names)):
		offset = 25 - len(str(names[name]))
		if isinstance(values[name], np.ndarray):
			# Extra spaces added to first column to even out np.arrays
			print(names[name], ' '*offset, values[name][0])
			for i in range(1, len(values[name][1])):
				print(' '*(offset+len(str(names[name]))+1), values[name][i])
		else:
			print(names[name], ' '*offset, values[name])	
	print('\n\n')
	
def print_last_move(lm):
	# Print out each move 'attribute' on separate lines under neat columns
	print('-'*24, 'Last Move\'s Info', '-'*24)
	names = ['Ply Number:',
			 'Move Number:',
			 'Turn:',
			 'From X:',
			 'From Y:',
			 'To X:',
			 'To Y:',
			 '   X Difference:',
			 '   Y Difference:',
			 '   X Direction:',  
			 '   Y Direction:',
			 'Piece:',
			 '   Piece Kind:',
		     '   Piece Colour:', 
			 'Destination Sq:',
			 'Queening?']
	values = [lm.ply_num, lm.move_num, lm.turn, lm.from_x, lm.from_y, lm.to_x,
			  lm.to_y, lm.x_diff, lm.y_diff, lm.x_dir, lm.y_dir, lm.piece,
			  lm.piece_kind, lm.piece_colour, lm.dest_sq, lm.queening]
	for name in range(len(names)):
		offset = 25 - len(str(names[name]))
		if values[name] == '  ':
			values[name] = '(empty)'
		print(names[name], ' '*offset, values[name])
	print('\n\n')

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

def print_game_over(message):
	print(message, ' Game Over.')




# ---MAIN GAME LOOP------------------------------------------------------------
def terminate():
	pg.quit()
	sys.exit()

def main():
	gs = GameState()
	load_images()
	print_new_game()
	click_xy = sq_from = sq_to = []
	while True:
		win.fill(GREEN)
		draw_chessboard(win)
		draw_pieces(win, gs.board)
		if sq_from and not sq_to:
			highlight_sq(win, gs.turn, sq_from)
					
		# From third move (5th ply) onwards, check if game is over
		if len(gs.moves) > 5:
			game_over_notice = gs.is_game_over()
			if game_over_notice != '':
				print_game_over(game_over_notice)

		# ---MOUSE IS CLICKED---
		if click_xy:
			valid_click = is_click_valid(click_xy)
			if valid_click:
				new_sq_xy = to_sq_xy(click_xy)
				on_sq = gs.board[new_sq_xy[1], new_sq_xy[0]]
				if on_sq.startswith(gs.turn):
					sq_from = new_sq_xy
					sq_to = []
				elif sq_from and (sq_from != sq_to):
					sq_to = new_sq_xy
					new_move = Move(gs, sq_from, sq_to)
					if new_move.is_valid(gs):
						gs.make_move(new_move)
					sq_from = sq_to = click_xy = []
				else:
					click_xy = []
		
		# ---EVENTS---
		event = pg.event.get()
		for e in event:
			if e.type == MOUSEBUTTONDOWN:
				click_xy = e.pos
			if e.type == QUIT:
				terminate()
			if e.type == KEYDOWN:
				pass
			if e.type == KEYUP:
				# ------KEYS---------------
				#   g = [G]ame State
				#   b = [B]oard
				#   m = [M]ove Information
				#   l = [L]ist of Moves
				#   q = [Q]uit
				#   t = [T]esting
				if e.key == K_g:
					print_current_gamestate(gs, click_xy, sq_from, sq_to)
				if e.key == K_b:
					print('\n' + str(gs.board) + '\n')
				if e.key == K_m and gs.moves:
					print_last_move(gs.moves[-1])
				if e.key == K_l and gs.moves:
					print_move_list(gs.moves)
				if e.key == K_ESCAPE or e.key == K_q:
					terminate()
				if e.key == K_t:
					pass

		pg.display.update()
		clock.tick(FPS)

if __name__ == "__main__":
	main()