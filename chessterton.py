# CHESSTERTON GROVE
# by Michal Wiraszka

# A chess game written entirely in Python, making heavy use of its Pygame module.

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
# 27.08.20 identifying check, forbidding walking into check, and counting valid moves - all functional
# 27.08.20 identifying checkmate and displaying moves
# 28.08.20 sidebar glitches fixes; includes move number if white; counting pieces and piece pts
# 28.08.20 display game state to sidebar by holding G
# 28.08.20 game over message bug fixed; v1.0 final touches //.

# ---VERSION 1.0---------------------------------------------------------------
# - human vs. human gameplay
# - flip board, show current game state info, and start new game functionality
# - controllable jukebox with three (...sophisticated) Classical music tracks
# - independently-designed and integrated move, capture, and board sound effects
# - game's moves relayed in side window, printed in algebraic chess notation

# ---Next Steps----------------------------------------------------------------
# - recognizing stalemate, drawing possible moves for selected piece, basic AI



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
B_SQ = (90,80,70)
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
	def __init__(self, game_num):
		self.game_num = game_num
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
		self.check = None
		self.stalemate = None
		self.checkmate = None

	def update_board(self, move):
		new_board = self.board.copy()
		# Update destination and origin squares
		if move.is_queening:
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
		if move.is_en_passant:
			if move.piece_colour == 'w':
				new_board[move.to_y + 1, move.to_x] = '  '
			else:
				new_board[move.to_y - 1, move.to_x] = '  '
		
		self.board = new_board

	def get_valid_moves(self):
		valid_moves = []
		for from_row, from_col in np.ndindex(self.board.shape):
			on_sq = self.board[from_row, from_col]
			if on_sq.startswith(self.turn):
				for to_row in range(8):
					for to_col in range(8):
						sq_from = [from_col, from_row]
						sq_to = [to_col, to_row]
						dest_sq = self.board[to_row, to_col]
						if sq_from != sq_to and not dest_sq.startswith(self.turn):
							hypothetical_move = Move(self, sq_from, sq_to)
							if hypothetical_move.is_legal:
								walking_into_check = hypothetical_move.check_if_walk_into_check(self)
								if not walking_into_check:
									to_append = str(on_sq) + ' ' + str(sq_from) + ' ' + str(sq_to)
									valid_moves.append(to_append)
		return valid_moves

	def is_game_over(self):
		if self.checkmate and self.turn == 'b':
			return 'Checkmate! White Wins.'
		elif self.checkmate and self.turn == 'w':
			return 'Checkmate! Black Wins.'
		elif self.stalemate:
			return 'Stalemate! Draw.'
		elif self.insuff_mat:
			return 'Insuff. material! Draw.'
		return ''

	def make_move(self, new_move):
		# Update counts if piece has been captured
		if new_move.is_en_passant:
			self.pieces[swap(self.turn)]['P'] -= 1
			self.pieces_pts[swap(self.turn)] -= 1
		elif new_move.is_capture:
			self.pieces[swap(self.turn)][new_move.dest_sq[-1]] -= 1
			self.pieces_pts[swap(self.turn)] -= PIECE_VAL[new_move.dest_sq[-1]]
		self.update_board(new_move)

		# Update castle rights if rook or king moved
		if (
				(new_move.is_castle_qs) or
				(new_move.piece_kind == 'R' and new_move.from_x == 0)
				):
			self.castling_rights_qs[self.turn] = False
		elif (
				(new_move.is_castle_ks) or
				(new_move.piece_kind == 'R' and new_move.from_x == 7)
				):
			self.castling_rights_ks[self.turn] = False
		elif new_move.piece_kind == 'K':
			self.castling_rights_qs[self.turn] = False
			self.castling_rights_ks[self.turn] = False
		
		# Update check, checkmate and stalemate info
		self.check = new_move.is_check
		self.checkmate = new_move.opp_moves_left == 0 and new_move.is_check
		self.stalemate = new_move.opp_moves_left == 0 and not new_move.is_check
		
		# Add move info to game state's move log variable for future reference
		# and switch to opponent's turn
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
		
		self.is_queening = ((self.to_y == 0 and self.piece == 'wP') or
					     (self.to_y == 7 and self.piece == 'bP'))
		self.is_castle_ks = (self.piece_kind == 'K' and self.x_diff == 2)
		self.is_castle_qs = (self.piece_kind == 'K' and self.x_diff == -2)
		if gs.moves:
			# Last move was a two-sq pawn move to the sq adjacent to where this move
			# originates from, and this pawn makes a capture behind the en-pass pawn.
			self.is_en_passant = ((self.piece_kind == 'P') and
	 			    			  (gs.moves[-1].piece_kind == 'P') and
	 			    			  (abs(gs.moves[-1].y_diff) == 2) and
	 			    			  (gs.moves[-1].to_y == self.from_y) and
	 			    			  (abs(gs.moves[-1].from_x - self.from_x) == 1) and
	 			    			  (gs.moves[-1].to_x == self.to_x))
		else:
			self.is_en_passant = False
		self.is_capture = self.is_en_passant or self.dest_sq != '  '
		self.is_legal = self.check_if_legal(gs)
		self.is_walk_into_check = None
		self.is_check = None
		self.opp_moves_left = None

	def check_if_legal(self, gs):
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
			return (valid_dir and (self.is_en_passant or
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
			valid_cas_qs = ((self.y_diff == 0 and self.x_diff == -2) and
							(gs.castling_rights_qs[self.turn]) and
							(gs.board[self.from_y, self.from_x-1] == '  ') and
		   					(gs.board[self.from_y, self.from_x-2] == '  ') and
		   					(gs.board[self.from_y, self.from_x-3] == '  '))
			valid_cas_ks = ((self.y_diff == 0 and self.x_diff == 2) and
							(gs.castling_rights_ks[self.turn]) and
							(gs.board[self.from_y, self.from_x+1] == '  ') and
		   					(gs.board[self.from_y, self.from_x+2] == '  '))
			return valid_1_sq or valid_cas_qs or valid_cas_ks

	def check_if_walk_into_check(self, gs):
		post_move_gs = GameState(0)
		post_move_gs.board = gs.board.copy()
		post_move_gs.update_board(self)
		post_move_gs.turn = swap(gs.turn)
		return self.check_if_check(post_move_gs)

	def check_if_check(self, gs):
		opp_king_loc = np.where(gs.board == swap(gs.turn)+'K')
		opp_king = [opp_king_loc[1].item(), opp_king_loc[0].item()]
		
		# pieces verified in order of general likelihood of giving check
		for piece_type in ['Q', 'R', 'B', 'N', 'P']:
			piece_loc = np.where(gs.board == gs.turn+piece_type)
			for i in range(len(piece_loc[0])):
				piece = [piece_loc[1][i], piece_loc[0][i]]
				hypothetical_king_capture = Move(gs, piece, opp_king)
				if hypothetical_king_capture.is_legal:
					return True
		return False

	def check_how_many_opp_moves_left(self, gs):
		post_move_gs = GameState(99)
		post_move_gs.board = gs.board.copy()
		post_move_gs.update_board(self)
		post_move_gs.turn = swap(gs.turn)
		valid_moves = post_move_gs.get_valid_moves()
		return (len(valid_moves))


# ---CONVERSIONS---------------------------------------------------------------
def to_file_rank(column_row):
	# <int list> {0,1,..,7}{0,1,..,7}   -->   <str>  {a,b,..,h}{1,2,..,8}
	file_rank = chr(97 + column_row[0]) + str(8 - column_row[1])
	return file_rank

def to_column_row(file_rank):
	# <str>  {a,b,..,h}{1,2,..,8}   -->   <int list> {0,1,..,7}{0,1,..,7}
	column_row = [ord(file_rank[0]) - 97, int(file_rank[1]) - 1]
	return column_row

def to_what_clicked(click_xy):
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
	# Start with move number if white move:
	if move.turn == 'w':
		move_num = (str(move.move_num) + '. ')
	else:
		move_num = ''

	# If Castles, nothing more added after zeros
	if move.is_castle_ks:
		return (move_num + 'O-O')
	elif move.is_castle_qs:
		return (move_num + 'O-O-O')

	# If pawn move, use only letter from square it came from
	if move.piece_kind != 'P':
		piece_kind = move.piece_kind
	else:
		piece_kind = str(to_file_rank([move.from_x, move.from_y]))[0]
	
	capture = 'x' if move.is_capture else ''
	
	# If pawn move (non-capture), file already given, so only need to add rank
	if move.piece_kind == 'P' and not move.is_capture:
		destination = str(to_file_rank([move.to_x, move.to_y]))[1]
	else:
		destination = str(to_file_rank([move.to_x, move.to_y]))

	queening = '=Q' if move.is_queening else ''
	checkmate = '#' if move.opp_moves_left == 0 and move.is_check else ''
	stalemate = '$' if move.opp_moves_left == 0 and not move.is_check else ''
	check = '+' if move.is_check and not checkmate else ''
	full_move = (
					move_num
				  + piece_kind
			  	  + capture
			  	  + destination
			  	  + queening
			  	  + checkmate
			  	  + stalemate
			  	  + check)
	return full_move


# ---IMAGES & DRAWING TO SCREEN------------------------------------------------
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

def draw_rounded_rect(surface, rect, col, corner_rad):
    # ---Function courtesy of Glenn Mackintosh on StackOverflow---
	# Anti-aliased circles to make corners smoother
    if rect.width < 2 * corner_rad or rect.height < 2 * corner_rad:
        raise ValueError(f"Both height (rect.height) and width (rect.width) must\
        				   be > 2 * cner radius ({corner_rad})")

    # Anti-aliasing circle drawing routines to smooth corners
    pg.gfxdraw.aacircle(surface,
    	rect.left+corner_rad, rect.top+corner_rad, corner_rad, col)
    pg.gfxdraw.aacircle(surface,
    	rect.right-corner_rad-1, rect.top+corner_rad, corner_rad, col)
    pg.gfxdraw.aacircle(surface,
    	rect.left+corner_rad, rect.bottom-corner_rad-1, corner_rad, col)
    pg.gfxdraw.aacircle(surface,
    	rect.right-corner_rad-1, rect.bottom-corner_rad-1, corner_rad, col)

    pg.gfxdraw.filled_circle(surface,
    	rect.left+corner_rad, rect.top+corner_rad, corner_rad, col)
    pg.gfxdraw.filled_circle(surface,
    	rect.right-corner_rad-1, rect.top+corner_rad, corner_rad, col)
    pg.gfxdraw.filled_circle(surface,
    	rect.left+corner_rad, rect.bottom-corner_rad-1, corner_rad, col)
    pg.gfxdraw.filled_circle(surface,
    	rect.right-corner_rad-1, rect.bottom-corner_rad-1, corner_rad, col)

    rect_tmp = pg.Rect(rect)

    rect_tmp.width -= 2*corner_rad
    rect_tmp.center = rect.center
    pg.draw.rect(surface, col, rect_tmp)

    rect_tmp.width = rect.width
    rect_tmp.height -= 2*corner_rad
    rect_tmp.center = rect.center
    pg.draw.rect(surface, col, rect_tmp)

def draw_bordered_rounded_rect(surface, rect, col, bd_col, corner_rad, bd_th):
	if corner_rad < 0:
		raise ValueError(f"Border radius ({corner_rad}) must be >= 0")
	rect_tmp = pg.Rect(rect)
	center = rect_tmp.center

	if bd_th:
		if corner_rad <= 0:
			pg.draw.rect(surface, bd_col, rect_tmp)
		else:
			draw_rounded_rect(surface, rect_tmp, bd_col, corner_rad)
			rect_tmp.inflate_ip(-2*bd_th, -2*bd_th)
			inner_rad = corner_rad - bd_th + 1
	else:
		inner_rad = corner_rad

	if inner_rad <= 0:
		pg.draw.rect(surface, col, rect_tmp)
	else:
		draw_rounded_rect(surface, rect_tmp, col, inner_rad)

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

def highlight_sq(screen, colour, sq_from, gs, flip):
	# Draw blue square with white or black rounded border, 4 px thick
	col = WHT if colour == 'w' else BLK
	pt_x = sq_from[0] if not flip else (7 - sq_from[0])
	pt_y = sq_from[1] if not flip else (7 - sq_from[1])
	draw_bordered_rounded_rect(screen,
		(98+pt_x*50, 198+pt_y*50, SQ_SIZE+4, SQ_SIZE+4), D_BLUE, col, 4, 2)



# ---DISPLAYING TO SIDE WINDOW-------------------------------------------------
def display_game_state(screen, gs):
	header_text = create_text("Current Game State", font_pref, 24, BLK)
	screen.blit(header_text, (591,190))
	pg.draw.rect(screen, ML_GRY, (590,209,155,2))
	labels = ['Move Number', 'Ply Number', 'Turn', ' ', 'Check?', 'Stalemate?',
	          'Checkmate?', ' ', ' ', 'Pieces Left', 'Pts of Material',
	          'KS Castling Rights', 'QS Castling Rights', ' ', ' ', 
	          'Pieces Left', 'Pts of Material',
	          'KS Castling Rights', 'QS Castling Rights']

	colour = 'White' if gs.turn == 'w' else 'Black'
	values = [(gs.ply_num + 1)//2, gs.ply_num, colour, '', gs.check,
			  gs.stalemate, gs.checkmate, '', '', gs.pieces['w']['P'],
			  gs.pieces_pts['w'], gs.castling_rights_ks['w'],
			  gs.castling_rights_qs['w'], '', '', gs.pieces['b']['P'],
			  gs.pieces_pts['b'], gs.castling_rights_ks['b'],
			  gs.castling_rights_qs['b']]
	
	pg.draw.rect(screen, ML_GRY, (695,235,2,345))
	white_header = create_text('White', font_pref, 20, BLK)
	screen.blit(white_header, (590,378))
	pg.draw.rect(screen, BLK, (560,395,100,2))
	black_header = create_text('Black', font_pref, 20, BLK)
	screen.blit(black_header, (590,488))
	pg.draw.rect(screen, BLK, (560,505,100,2))
	for i in range(len(labels)):
		label = create_text(labels[i], font_pref, 18, BLK)
		screen.blit(label, (560,240+18*i))
		value = create_text(str(values[i]), font_pref, 18, BLK)
		screen.blit(value, (736,240+18*i))
	
def display_moves(screen, gs, move_list):
	draw_bordered_rounded_rect(screen, (540,180,255,440), L_GRY, D_GRY, 5, 3)
	header_text = create_text(("Game " + str(gs.game_num)), font_pref, 24, BLK)
	screen.blit(header_text, (632,190))
	pg.draw.rect(screen, ML_GRY, (590,209,155,2))

	if move_list:
		# Truncate to show a maximum of 15 moves (30 plies) while preserving
		# move number and keeping white moves in left column
		if len(move_list) > 30:
			if len(move_list) % 2 == 0:
				move_list = move_list[-30:]
			else:
				move_list = move_list[-29:]

		for i in range(len(move_list)):
			if i % 2 == 0:
				move_text = create_text(move_list[i], font_pref, 22, BLK)
				# Offset move numbers to the left as more digits are added
				if move_list[i][2] == '.':
					screen.blit(move_text, (592,220+i*10))
				elif move_list[i][3] == '.':
					screen.blit(move_text, (584,220+i*10))
				else:
					screen.blit(move_text, (600,220+i*10))
			else:
				move_text = create_text(move_list[i], font_pref, 22, BLK)
				screen.blit(move_text, (695,220+(i-1)*10))

def draw_game_over_message(screen, info):
	if info == 'Stalemate! Draw.':
		offset = 20
	elif info == 'Insuff. material! Draw.':
		offset = -20
	else:
		offset = 0
	draw_bordered_rounded_rect(screen, (567,550,200,50), M_GRY, D_GRY, 4, 2)
	game_over_message = create_text(info, font_pref, 20, BLK)
	screen.blit(game_over_message, (593+offset,568))

def update_move_list(moves):
	move_list = []
	for move in range(len(moves)):
		new_move = to_algebraic(moves[move])
		move_list.append(new_move)
	return move_list


# ---PRINT TO SHELL------------------------------------------------------------
def print_welcome_msg():
	print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
	print('*'*68)
	print(' '*26 + 'Chessterton Grove')
	print(' '*31 + 'NEW GAME')
	print('*'*68)

def print_board(board):
	print('\n\n' + ' '*11 + '--- BOARD STATE ---')
	print(' '*10 + '(as stored internally)\n\n' + str(board) + '\n')


# ---MUSIC AND SOUND CHANGES---------------------------------------------------
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
	new_game = sound_on = music_on = True
	toggle_flip = vol_up = vol_down = show_gs = False
	flip_delay = jukebox_delay = vol_button_hold = game_counter = 0
	current_track = None

	click_xy = sq_from = sq_to = []  # User-sourced input variables

	bg = pg.image.load('img/bg.png').convert_alpha()
	load_images()

	print_welcome_msg()

	while True:
		# ---New game & various delays to keep buttons lit up for some time
		if new_game:
			game_counter += 1
			gs = GameState(game_counter)	
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

		# ---Draw main elements to screen
		win.blit((bg), (0,0))
		draw_chessboard(win, toggle_flip)
		if sq_from and not sq_to:
			highlight_sq(win, gs.turn, sq_from, gs, toggle_flip)
		draw_pieces(win, gs.board, toggle_flip, new_game)

		if new_game:
			move_list = []
			if not current_track:
				current_track = jukebox('3')	
		new_game = False

		draw_bottom_options(win, int(current_track), music_on,
						    vol_up, vol_down, toggle_flip, ng_button, show_gs)

		# ---Display either move list or game state on sidebar
		draw_bordered_rounded_rect(win, (540,180,255,440), L_GRY, D_GRY, 5, 3)
		if show_gs:
			display_game_state(win, gs)
		else:
			display_moves(win, gs, move_list)
			# ---From third move (5th ply) onwards, check if game is over
			if len(gs.moves) >= 5:
				game_over_info = gs.is_game_over()
				if game_over_info != '':
					draw_game_over_message(win, game_over_info)
	

		# ---MOUSE IS CLICKED
		if click_xy:
			clicked = to_what_clicked(click_xy)
			if clicked == 'board':
				new_sq_xy = to_sq_xy(click_xy, toggle_flip)
				on_sq = gs.board[new_sq_xy[1], new_sq_xy[0]]
				if on_sq.startswith(gs.turn):
					sq_from = new_sq_xy
					sq_to = []
				elif sq_from and (sq_from != sq_to):
					sq_to = new_sq_xy
					new_move = Move(gs, sq_from, sq_to)
					# First, see if the piece can legally move there
					if new_move.is_legal:
						# Next, see if this move puts your king in check
						new_move.is_walk_into_check = new_move.check_if_walk_into_check(gs)
						if not new_move.is_walk_into_check:
							# If both legal and not walking into check, can make move.
							gs.update_board(new_move)
							new_move.is_check = new_move.check_if_check(gs)
							new_move.opp_moves_left = new_move.check_how_many_opp_moves_left(gs)
							gs.make_move(new_move)
							move_list = update_move_list(gs.moves)
							if sound_on:
								m_1.play() if new_move.turn == 'w' else m_2.play()
								if new_move.is_capture:
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
		
		# ---KEYBOARD & MOUSE EVENTS
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
					if e.key == K_p or e.key == K_m:
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
				if e.key == K_b:
					print_board(gs.board)

		pg.display.update()
		clock.tick(FPS)

if __name__ == "__main__":
	main()