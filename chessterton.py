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
# 14.07.20 wht pawn moves, cont'd; 'b' to print board
# 14.07.20 wht pawn captures; change turn instance attribute to str
# 15.07.20 blk pawn moves & captures; queening
# 15.07.20 .move_log instance attribute - conception; knight moves
# 16.07.20 bishop moves
# 16.07.20 rook moves; some absolute value calculations simplified
# 17.07.20 king and queen moves
# 20.07.20 glitch in highlighting square fixed
# 20.07.20 wht and blk to move in turn
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
# 23.08.20 flip board option, various graphical enhancements
# 24.08.20 music; sfx; font preferences; graphics, cont'd (glitchy)
# 25.08.20 music & sfx + bottom game options section finalized


# ---IMPORTS-------------------------------------------------------------------
import sys
import copy

import pygame as pg
import pygame.gfxdraw
from pygame.locals import *
from pygame import mixer

import numpy as np


# ---CONSTANTS-----------------------------------------------------------------
WIN_W = 875
WIN_H = 700
SQ_SIZE = 50
FPS = 60

BLK = (10,10,10)
WHT = (245,245,245)
B_SQ = (80,70,60)
W_SQ = (200,200,200)
L_BLUE = (113,124,181)
D_BLUE = (83,94,151)
L_BRN = (40,30,8)
D_BRN = (30,20,0)
L_GRY = (230,230,230)
ML_GRY = (220,220,220)
M_GRY = (210,210,210)
D_GRY = (190,190,190)

PIECE_IMG = {}
PIECE_VAL = {'Q':9, 'R':5, 'N':3, 'B':3, 'P':1}


# ---PYGAME FONTS SETUP--------------------------------------------------------
# Core ideas courtesy of: https://nerdparadise.com/programming/pygame/part5
def make_font(fonts, size):
    available = pg.font.get_fonts()
    # get_fonts() returns a list of lowercase spaceless font names
    choices = map(lambda x: x.lower().replace(' ', ''), fonts)
    for choice in choices:
        if choice in available:
            return pg.font.SysFont(choice, size)
    return pg.font.Font(None, size)
    
_cached_fonts = {}
def get_font(font_pref, size):
    global _cached_fonts
    key = str(font_pref) + '|' + str(size)
    font = _cached_fonts.get(key, None)
    if font == None:
        font = make_font(font_pref, size)
        _cached_fonts[key] = font
    return font

_cached_text = {}
def create_text(text, fonts, size, color):
    global _cached_text
    key = '|'.join(map(str, (fonts, size, color, text)))
    image = _cached_text.get(key, None)
    if image == None:
        font = get_font(fonts, size)
        image = font.render(text, True, color)
        _cached_text[key] = image
    return image

font_pref = ["Times New Roman", "Deja Vu Sans", "Arial", "Helvetica"]


# ---PYGAME INIT---------------------------------------------------------------
pg.mixer.pre_init(44100, -16, 2, 4096)
pg.mixer.init()
pg.init()

pieces_fall = pg.mixer.Sound('sound/pieces_fall.ogg')
pieces_fall.set_volume(0.7)
m_1 = pg.mixer.Sound('sound/move_piece_1.ogg')
m_1.set_volume(0.8)
m_2 = pg.mixer.Sound('sound/move_piece_2.ogg')
m_2.set_volume(0.8)
capture = pg.mixer.Sound('sound/capture.ogg')
capture.set_volume(0.8)
flip_board = pg.mixer.Sound('sound/flip_board.ogg')
flip_board.set_volume(0.8)

pg.display.set_caption("Chessterton Grove v1.0")
win = pg.display.set_mode((WIN_W, WIN_H), 0, 32)

clock = pg.time.Clock()


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
		if move.is_castle_qs:
			new_board[move.to_y, move.to_x-2] = '  '
			new_board[move.to_y, move.to_x+1] = str(move.piece_colour)+'R'
		elif move.is_castle_ks:
			new_board[move.to_y, move.to_x+1] = '  '
			new_board[move.to_y, move.to_x-1] = str(move.piece_colour)+'R'
		
		# En passant scenario: additionally manually remove opponent's pawn
		if move.en_passant:
			if move.piece_colour == 'w':
				new_board[move.to_y + 1, move.to_x] = '  '
			else:
				new_board[move.to_y - 1, move.to_x] = '  '
		
		self.board = new_board


	def valid_moves(self, find_all=False):
		print('VALID MOVES LEFT for', self.turn, '?')
		print(self.board)
		valid_moves_left = []
		for from_row, from_col in np.ndindex(self.board.shape):
			on_sq = (self.board[from_row, from_col])
			if on_sq.startswith(self.turn):
				for to_row in range(8):
					for to_col in range(8):
						from_sq = [from_row, from_col]
						to_sq = [to_row, to_col]
						if from_sq != to_sq:
							hyp_move = Move(self, from_sq, to_sq)
							move_valid = hyp_move.is_valid(self, True)
							if move_valid and not find_all:
								return True
							elif move_valid and find_all:
								to_app = str(on_sq) + ' ' + str(from_sq) + ' ' + str(to_sq)
								valid_moves_left.append(to_app)
		if find_all:
			return valid_moves_left
		else:
			return False

	def is_check(self):
		# 'turn' is the side supposedly giving check, therefore opponent's king is swap(turn)
		king_loc = np.where(self.board == swap(self.turn)+'K')
		king = [king_loc[1].item(), king_loc[0].item()]
		counter = 0
		# pieces verified in order of general likelihood of giving check
		for piece_type in ['Q', 'R', 'B', 'N', 'P']:
			piece_loc = np.where(self.board == self.turn+piece_type)
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
		valid_move_list = self.valid_moves(True)
		if valid_move_list:
			print(valid_move_list)
			moves_left = True
		return not moves_left and not self.check

	def is_checkmate(self):
		print('checking if checkmate...')
		valid_move_list = self.valid_moves(True)
		if valid_move_list:
			print(valid_move_list)
			moves_left = True
		return not moves_left and self.check

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
		self.check = self.is_check()
		self.stalemate = self.is_stalemate()
		self.checkmate = self.is_checkmate()
		print('Check, Stalemate, Checkmate:', self.check, self.stalemate, self.checkmate)

		if (
				(new_move.is_castle_qs) or
				(new_move.piece_kind == 'R' and new_move.from_x == 0)
				):
			self.castling_rights_qs[self.turn] = False
		if (
				(new_move.is_castle_ks) or
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
		self.check = False
		self.stalemate = False
		self.checkmate = False
		self.is_castle_ks = (self.piece_kind == 'K' and self.x_diff == 2)
		self.is_castle_qs = (self.piece_kind == 'K' and self.x_diff == -2)

	def is_valid(self, gs, only_piece_validity=False, cant_capture_king=True):
		if not only_piece_validity:
			walk_into = self.is_walk_into_check(gs)
			if walk_into:
				return False
		
		if cant_capture_king:
			if self.dest_sq.endswith('K'):
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
		return (self.en_passant or self.dest_sq != '  ')

	def is_walk_into_check(self, gs):
		# Were this move made, would an opponent's piece be checking you
		hyp_gs = copy.copy(gs)
		hyp_gs.update_board(self)
		opp_turn = swap(self.turn)
		is_check = hyp_gs.is_check()
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

def to_sq_xy(click_xy, flip):
	x = (click_xy[0]-100) // SQ_SIZE
	y = (click_xy[1]-200) // SQ_SIZE
	if flip:
		x = 7 - x
		y = 7 - y
	return (x,y)

def swap(turn):
	return 'b' if turn == 'w' else 'w'

def to_algebraic(move):
	# Move() object    -->    <str> in alegraic notation, like exd4+ f8=Q#
	# If not Castles; append characters to string one at a time
	move_return = ''
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

	if move.checkmate:
		move_return += '#'
	elif move.stalemate:
		move_return += '$'
	elif move.check:
		move_return += '+'

	return move_return




# ---CLICKING EVENTS & DRAWING TO SCREEN---------------------------------------
def load_images():
	sheet = pg.image.load('img/chess_set.png').convert_alpha()
	pieces = ['bQ', 'bK', 'bR', 'bN', 'bB', 'bP',
			  'wQ', 'wK', 'wR', 'wN', 'wB', 'wP']
	for i in range(len(pieces)):
		PIECE_IMG[pieces[i]] = sheet.subsurface(i*50, 0, 50, 50)

def draw_chessboard(screen, flip=False):
	draw_bordered_rounded_rect(screen, (80,180,440,440), L_BRN, D_BRN, 4, 4)
	draw_bordered_rounded_rect(screen, (99,199,402,402), W_SQ, W_SQ, 1, 3)
	for i in range(8):
		for j in range(8):
			sq_col = B_SQ if (i+j) % 2 == 1 else W_SQ
			pg.draw.rect(screen, sq_col,
				(100+j*SQ_SIZE, 200+i*SQ_SIZE, SQ_SIZE, SQ_SIZE))
	for i in range(8):
		# Draw digits 1-8 along either left (flip=False) or right side
		# Draw letters A-H (ASCII chars 65-72) along bottom (flip=False) or top
		flip_offset = (421*int(flip))
		digits_order = 570-50*i if not flip else 220+50*i
		letters_order = 122+50*i if not flip else 472-50*i

		digits = create_text(('{}'.format(i+1)), font_pref, 16, WHT)
		letters = create_text(('{}'.format(chr(65+i))), font_pref, 16, WHT)
		screen.blit(digits, (87+flip_offset, digits_order))
		screen.blit(letters, (letters_order, 605-flip_offset))

def draw_sidebar(screen):
	draw_bordered_rounded_rect(screen, (540,180,255,440), L_GRY, D_GRY, 5, 3)
	

def draw_bottom_options(screen, track, music_on, v_up, v_down, flip, ng, gs):
	draw_bordered_rounded_rect(screen, (80,635,WIN_W-160,50), L_GRY, D_GRY, 5, 3)
	if track == 1:
		piece_name = 'Beethoven - German Dance and Rondo'
	elif track == 2:
		piece_name = 'Mozart - Horn Concerto No. 4'
	elif track == 3:
		piece_name = 'Vivaldi - Concerto in G Dur'
	text_1 = create_text(("Playing:    " + piece_name), font_pref, 22, BLK)
	screen.blit(text_1, (97, 642))

	col_on = L_BLUE if music_on else M_GRY
	col_off = M_GRY if music_on else L_BLUE
	col_1 = L_BLUE if track == 1 else M_GRY
	col_2 = L_BLUE if track == 2 else M_GRY
	col_3 = L_BLUE if track == 3 else M_GRY
	col_up = L_BLUE if v_up else M_GRY
	col_down = L_BLUE if v_down else M_GRY
	col_flip = L_BLUE if flip else M_GRY
	col_ng = L_BLUE if ng else M_GRY
	col_gs = L_BLUE if gs else M_GRY

	draw_bordered_rounded_rect(screen, (95,661,30,20), col_on, D_GRY, 4, 2)
	draw_bordered_rounded_rect(screen, (128,661,36,20), col_off, D_GRY, 4, 2)
	text_2 = create_text("ON   OFF", font_pref, 20, BLK)
	screen.blit(text_2, (100,665))
	draw_bordered_rounded_rect(screen, (221,661,20,20), col_down, D_GRY, 4, 2)
	draw_bordered_rounded_rect(screen, (243,661,20,20), col_up, D_GRY, 4, 2)
	text_3 = create_text("VOL.   -", font_pref, 20, BLK)
	text_3_add = create_text("+", font_pref, 20, BLK)
	screen.blit(text_3, (185,665))
	screen.blit(text_3_add, (249,663))
	draw_bordered_rounded_rect(screen, (285,661,20,20), col_1, D_GRY, 4, 2)
	draw_bordered_rounded_rect(screen, (308,661,20,20), col_2, D_GRY, 4, 2)
	draw_bordered_rounded_rect(screen, (331,661,20,20), col_3, D_GRY, 4, 2)
	text_4 = create_text("1    2    3", font_pref, 20, BLK)
	screen.blit(text_4, (292,665))

	pg.draw.rect(screen, ML_GRY, (465,645,2,32))

	draw_bordered_rounded_rect(screen, (493,639,136,20), col_ng, D_GRY, 4, 2)
	draw_bordered_rounded_rect(screen, (493,661,136,20), col_flip, D_GRY, 4, 2)
	draw_bordered_rounded_rect(screen, (633,639,136,20), col_gs, D_GRY, 4, 2)
	draw_bordered_rounded_rect(screen, (633,661,136,20), M_GRY, D_GRY, 4, 2)
	text_5 = create_text("New Game (N)", font_pref, 22, BLK)
	text_6 = create_text("Flip Board (F)", font_pref, 22, BLK)
	text_7 = create_text("Game State (G)", font_pref, 22, BLK)
	text_8 = create_text("Quit (Q)", font_pref, 22, BLK)
	screen.blit(text_5, (511,642))
	screen.blit(text_6, (515,664))
	screen.blit(text_7, (646,642))
	screen.blit(text_8, (673,664))


def draw_pieces(screen, board, flip=False, new_game=False):
	for i in range(8):
		for j in range(8):
			if board[i][j] != '  ':
				pc = board[i][j]
				if not flip:
					screen.blit(PIECE_IMG[pc],(100+j*SQ_SIZE, 200+i*SQ_SIZE))
				else:
					screen.blit(PIECE_IMG[pc],(450-j*SQ_SIZE, 550-i*SQ_SIZE))
	if new_game:
		pieces_fall.play()


def draw_rounded_rect(surface, rect, col, cor_r):
    # ---Function courtesy of Glenn Mackintosh on StackOverflow---
	# Anti-aliased circles to make corners smoother
    if rect.width < 2 * cor_r or rect.height < 2 * cor_r:
        raise ValueError(f"Both height (rect.height) and width (rect.width) must\
        				   be > 2 * cner radius ({cor_r})")

    # Anti-aliasing circle drawing routines to smooth corners
    pg.gfxdraw.aacircle(surface, rect.left+cor_r, rect.top+cor_r, cor_r, col)
    pg.gfxdraw.aacircle(surface, rect.right-cor_r-1, rect.top+cor_r, cor_r, col)
    pg.gfxdraw.aacircle(surface, rect.left+cor_r, rect.bottom-cor_r-1, cor_r, col)
    pg.gfxdraw.aacircle(surface, rect.right-cor_r-1, rect.bottom-cor_r-1, cor_r, col)

    pg.gfxdraw.filled_circle(surface, rect.left+cor_r, rect.top+cor_r, cor_r, col)
    pg.gfxdraw.filled_circle(surface, rect.right-cor_r-1, rect.top+cor_r, cor_r, col)
    pg.gfxdraw.filled_circle(surface, rect.left+cor_r, rect.bottom-cor_r-1, cor_r, col)
    pg.gfxdraw.filled_circle(surface, rect.right-cor_r-1, rect.bottom-cor_r-1, cor_r, col)

    rect_tmp = pg.Rect(rect)

    rect_tmp.width -= 2*cor_r
    rect_tmp.center = rect.center
    pg.draw.rect(surface, col, rect_tmp)

    rect_tmp.width = rect.width
    rect_tmp.height -= 2*cor_r
    rect_tmp.center = rect.center
    pg.draw.rect(surface, col, rect_tmp)


def draw_bordered_rounded_rect(surface, rect, col, bord_col, corn_rad, bord_th):
	if corn_rad < 0:
		raise ValueError(f"Border radius ({corner_rad}) must be >= 0")
	rect_tmp = pg.Rect(rect)
	center = rect_tmp.center

	if bord_th:
		if corn_rad <= 0:
			pg.draw.rect(surface, bord_col, rect_tmp)
		else:
			draw_rounded_rect(surface, rect_tmp, bord_col, corn_rad)
			rect_tmp.inflate_ip(-2*bord_th, -2*bord_th)
			inner_rad = corn_rad - bord_th + 1
	else:
		inner_rad = corn_rad

	if inner_rad <= 0:
		pg.draw.rect(surface, col, rect_tmp)
	else:
		draw_rounded_rect(surface, rect_tmp, col, inner_rad)


def highlight_sq(screen, colour, sq_from, gs, flip):
	# Draw blue square with white or black rounded border, 4 px thick
	col = WHT if colour == 'w' else BLK
	pt_x = sq_from[0] if not flip else (7 - sq_from[0])
	pt_y = sq_from[1] if not flip else (7 - sq_from[1])
	draw_bordered_rounded_rect(screen,
		(98+pt_x*50, 198+pt_y*50, SQ_SIZE+4, SQ_SIZE+4), D_BLUE, col, 4, 2)


def what_clicked(click_xy):
	x = click_xy[0]
	y = click_xy[1]
	if (x >= 100 and x <= 500) and (y >= 200 and y <= 600):
		return 'board'
	elif (x >= 95 and x <= 123) and (y >= 661 and y <= 679):
		return 'music_on'
	elif (x >= 128 and x <= 162) and (y >= 661 and y <= 679):
		return 'music_off'
	elif (x >= 221 and x <= 239) and (y >= 661 and y <= 679):
		return 'vol_down'
	elif (x >= 243 and x <= 261) and (y >= 661 and y <= 679):
		return 'vol_up'
	elif (x >= 285 and x <= 303) and (y >= 661 and y <= 679):
		return '1'
	elif (x >= 308 and x <= 326) and (y >= 661 and y <= 679):
		return '2'
	elif (x >= 331 and x <= 349) and (y >= 661 and y <= 679):
		return '3'
	elif (x >= 493 and x <= 627) and (y >= 639 and y <= 658):
		return 'new_game'
	elif (x >= 493 and x <= 627) and (y >= 661 and y <= 679):
		return 'flip_board'
	elif (x >= 633 and x <= 767) and (y >= 639 and y <= 658):
		return 'game_state'
	elif (x >= 633 and x <= 767) and (y >= 661 and y <= 679):
		return 'quit'



# ---PRINT TO SHELL------------------------------------------------------------
def print_welcome_msg():
	print_spaces()
	print('*'*68+'\n'+' '*26+'Chessterton Grove\n'+' '*31+'NEW GAME\n'+'*'*68)

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
			 'Pieces Left (wht):',
			 'Pieces Left (blk):',
		     'Points of Material:', 
			 'QS Castling Rights (wht):',
			 'KS Castling Rights (wht):',
			 'QS Castling Rights (blk):',
			 'KS Castling Rights (blk):',
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



def jukebox(request, current_on=None):
	if request == '1' or request == '2' or request == '3': 
		pg.mixer.music.stop()
		pg.mixer.music.load('sound/track_' + request + '.ogg')
		pg.mixer.music.play()
		return int(request)
	if request == 'p':
		pg.mixer.music.pause() if current_on else pg.mixer.music.unpause()
		return not current_on
	if request == 's':
		return not current_on
	if request == 'up':
		current_volume = pg.mixer.music.get_volume()
		if current_volume > 0.9:
			pg.mixer.music.set_volume(1)
		else:
			pg.mixer.music.set_volume(current_volume + 0.1)
	if request == 'down':
		current_volume = pg.mixer.music.get_volume()
		if current_volume < 0.1:
			pg.mixer.music.set_volume(0)
		else:
			pg.mixer.music.set_volume(current_volume - 0.1)
	jukebox_delay = 8


# ---MAIN GAME LOOP------------------------------------------------------------
def terminate():
	pg.quit()
	sys.exit()

def main():
	# ---MISC INITS
	new_game = True
	click_xy = sq_from = sq_to = []  # User-derived inputs
	toggle_flip = vol_up = vol_down = show_gs = False
	flip_delay = jukebox_delay = vol_button_hold = 0
	current_track = jukebox('1')
	sound_on = music_on = True
	bg = pg.image.load('img/bg.png').convert_alpha()
	load_images()
	print_welcome_msg()

	while True:
		# ---Various delays to keep buttons lit up for some time
		if new_game:
			gs = GameState()
			ng_button_hold = 3
		if ng_button_hold > 0:
			ng_button = True
			ng_button_hold -= 1
		else:
			ng_button = False
		if flip_delay > 0:
			flip_delay -= 1
		if jukebox_delay > 0:
			jukebox_delay -= 1
		if vol_button_hold > 0:
			vol_button_hold -= 1
		else:
			vol_up = vol_down = False

		# ---Draw all elements to screen
		win.blit((bg), (0,0))
		draw_chessboard(win, toggle_flip)
		if sq_from and not sq_to:
			highlight_sq(win, gs.turn, sq_from, gs, toggle_flip)
		draw_pieces(win, gs.board, toggle_flip, new_game)
		draw_bottom_options(win, int(current_track), music_on,
						    vol_up, vol_down, toggle_flip, ng_button, show_gs)
		draw_sidebar(win)
		new_game = False

		# From third move (5th ply) onwards, check if game is over
		if len(gs.moves) > 5:
			game_over_notice = gs.is_game_over()
			if game_over_notice != '':
				print_game_over(game_over_notice)

		# ---MOUSE IS CLICKED--------------------------------------------------
		if click_xy:
			clicked = what_clicked(click_xy)
			if clicked == 'board':
				new_sq_xy = to_sq_xy(click_xy, toggle_flip)
				on_sq = gs.board[new_sq_xy[1], new_sq_xy[0]]
				if on_sq.startswith(gs.turn):
					sq_from = new_sq_xy
					sq_to = []
				elif sq_from and (sq_from != sq_to):
					sq_to = new_sq_xy
					new_move = Move(gs, sq_from, sq_to)
					if new_move.is_valid(gs):
						gs.make_move(new_move)
						if sound_on:
							print('sound on')
							m_1.play() if new_move.turn == 'w' else m_2.play()
							if new_move.is_capture():
								capture.play()
					sq_from = sq_to = []
			elif clicked == 'music_on' or clicked == 'music_off':
				music_on = jukebox('p', music_on)
			elif clicked == 'vol_up':
				jukebox('up')
				vol_button_hold = 3
				vol_up = True
			elif clicked == 'vol_down':
				jukebox('down')
				vol_button_hold = 3
				vol_down = True
			elif clicked in ['1','2','3']:
				current_track = jukebox(clicked)
			elif clicked == 'flip_board':
				toggle_flip = not toggle_flip
			elif clicked == 'new_game':
				new_game = True
			elif clicked == 'game_state':
				show_gs = True
			elif clicked == 'quit':
				terminate()
			click_xy = []
		
		# ---EVENTS------------------------------------------------------------
		event = pg.event.get()
		for e in event:
			if e.type == MOUSEBUTTONUP and show_gs:
				show_gs = False
			if e.type == MOUSEBUTTONDOWN:
				click_xy = e.pos
			if e.type == QUIT:
				terminate()
			if e.type == KEYDOWN:
				if e.key == K_f and flip_delay == 0:
					toggle_flip = not toggle_flip
					if sound_on:
						flip_board.play()
						flip_delay = 8
				if e.key == K_ESCAPE or e.key == K_q:
					terminate()
				if e.key == K_g:
					show_gs = True
				if jukebox_delay == 0:
					if e.key == K_p:
						music_on = jukebox('p', music_on)
					if e.key == K_1 or e.key == K_2 or e.key == K_3:
						if e.key == K_1:
							current_track = jukebox('1')
						if e.key == K_2:
							current_track = jukebox('2')
						if e.key == K_3:
							current_track = jukebox('3')
						if not music_on:
							music_on = True
					if e.key == K_UP or e.key == K_EQUALS:
						jukebox('up')
						vol_button_hold = 3
						vol_up = True
					if e.key == K_DOWN or e.key == K_MINUS:
						jukebox('down')
						vol_button_hold = 3
						vol_down = True
					if e.key == K_s:
						sound_on = jukebox('s', sound_on)
			if e.type == KEYUP:
				if e.key == K_n:
					new_game = True
				if e.key == K_g:
					show_gs = False
					print_current_gamestate(gs, click_xy, sq_from, sq_to)
				if e.key == K_b:
					print('\n' + str(gs.board) + '\n')
				if e.key == K_l and gs.moves: 
					print_last_move(gs.moves[-1])
				if e.key == K_t:
					pass

		pg.display.update()
		clock.tick(FPS)

if __name__ == "__main__":
	main()