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
		self.pieces_left = {'w': {'Q':1, 'R':2, 'N':2, 'B':2, 'P':8},
						   {'b': {'Q':1, 'R':2, 'N':2, 'B':2, 'P':8}}}
		self.pieces_points = {'w': 39, 'b': 39}
		self.click_xy = [] # Click's pixel location coordinates [x, y]
		self.move_xy = []  # Move's coordinates [from-x, from-y, to-x, to-y]
		self.moves = []


		def is_click_valid(self):
			return if not ((self.click_xy[0] < 100 or self.click_xy[0] >= 500) or
	   					   (self.click_xy[1] < 200 or self.click_xy[1] >= 600))

		def is_game_over(self):
			# Checkmate, stalemate, or both sides have insufficient material
			if gs.is_checkmate:
				return 'Checkmate!'
			elif gs.is_stalemate:
				return 'Stalemate!'
			elif (gs.piece_points['w']) < 1 and (gs.piece_points['b']) < 1:
				return 'Both sides have insufficient material!'
			return ''

		def is_move_possible(self):
			for piece in gs.board:
				if piece.startswith(gs.is_turn):
					piece_xy = np.where(self.board == piece)
					# for now, check if that piece can move to any of the 64 squares.
					# later, to be optimized for that piece_kind's possible squares.
					for i in range(8):
						for j in range(8):
							move_xy = [piece_xy[1].item(),
									   piece_xy[0].item(),
									   j, i]
							hypothetical_gs = GameState()
							hypothetical_move = Move(gs, move_xy)
							if hypothetical_move.valid:
								return True
			return False

		def make_move(self, new_move):
			update_board(self, new_move)
			self.board = new_move.board_after
			self.on_move += 1
			self.is_turn = swap(self.is_turn) 
			self.is_check = new_move.check
			self.is_checkmate = new_move.checkmate
			self.is_stalemate = new_move.stalemate
			self.pieces_left = new_move.pieces_left
			self.pieces_points = new_move.pieces_points
			self.moves.append(self.new_move)
			self.click_xy = []
			self.move_xy = []

		def change_sq_sel(self, move_xy):
			# Demote 'to' square to be the new 'from' square
			gs.move_xy[0] = gs.move_xy[2]
			gs.move_xy[1] = gs.move_xy[3]
			del gs.move_xy[2:]



class Move():
	def __init__(self, gs, move_xy):
		# Takes: GameState() object, move coord list [from-x, from-y, to-x, to-y]
		# General Move Information
		self.move_num = gs.on_move
		self.ply_num = int((self.move_num + 1) / 2)
		self.last_move = [gs.moves[-1] if (not self.move_num == 1) else None]
		self.prev_turn = [gs.moves[-2] if (not self.move_num == 1) else None]
		self.turn = gs.is_turn

		# Location on Board Information
		self.from_x = move_xy[0]
		self.from_y = move_xy[1]
		self.to_x = move_xy[2]
		self.to_y = move_xy[3]
		self.x_diff = self.to_x - self.from_x
		self.y_diff = self.to_y - self.from_y
		self.x_direction = -1 if self.x_diff < 0 else 1
		self.y_direction = -1 if self.x_diff < 0 else 1

		# Piece Information
		self.piece = gs.board[self.from_y, self.from_x]
		self.piece_kind = self.piece[1]
		self.piece_colour = self.piece[0]
		self.on_dest_sq = gs.board[to_y, to_x]
		
		# Move Validation & Special Move Attributes
		self.capture = self.on_dest_sq != '  '
		if self.piece_kind == 'P':
			self.valid = (
				((self.piece_colour == 'w' and self.y_dir == -1) or
			     (self.piece_colour == 'b' and self.y_dir == 1)) and
				x_diff == 0 or (x_diff == 1 and y_diff == 1))
			self.queening = (self.y_to == 0 or self.y_to == 7)
			if self.move_num > 3 and (
					(self.last_move.double_pawn_push) and
					(self.last_move.to_y == self.to_y)
					):
				self.capture = True
				self.en_passant = True		
		elif self.piece_kind == 'N':
			self.valid = ((abs(self.x_diff) == 2 and abs(self.y_diff) == 1) or
						  (abs(self.x_diff) == 1 and abs(self.y_diff) == 2))
		
		elif self.piece_kind == 'B':
			self.valid = (abs(self.x_diff) == abs(self.y_diff))
			# Check for obstacles. If x_diff or y_diff < 0, step direction set
			# to -1 and start at -1 (so we don't check origin square at i = 0)
			for row in range(self.x_dir, self.x_diff, self.x_dir):
				for col in range(self.y_dir, self.y_diff, self.y_dir):
					sq_along_way = self.board[self.from_y + r, self.from_x + c]
					if abs(r) == abs(c) and sq_along_way != '  ':
						self.valid = False
		
		elif self.piece_kind == 'R':
			self.valid = (self.y_diff == 0 or self.x_diff == 0)
			if self.y_diff == 0:
				for c in range(self.x_dir, self.x_diff, self.x_dir):
					if self.board[self.from_y, self.from_x + c] != '  ':
						self.valid = False
			elif self.x_diff == 0:
				for r in range(self.y_dir, self.y_diff, self.y_dir):
					if self.board[self.from_y + r, self.from_x] != '  ':
						self.valid = False
			else:
				self.is_valid = True
			self.cant_castle_qs = (self.from_x == 0)
			self.cant_castle_ks = (self.from_x == 7)
		
		elif self.piece_kind == 'Q':
			# Check for obstacles for all 3 cases: horizontal move, vertical move,
			# and diagonal move (where absolutes of x_diff & y_diff are equal)
			if self.y_diff == 0:
				for c in range(self.x_dir, self.x_diff, self.x_dir):
					if self.board[self.from_y, self.from_x + c] != '  ':
						self.valid = False
			elif self.x_diff == 0:
				for r in range(self.y_dir, self.y_diff, self.y_dir):
					if self.board[self.from_y + r, self.from_x] != '  ':
						self.valid = False
			elif abs(self.x_diff) == abs(self.y_diff):
				for c in range(self.x_dir, self.x_diff, self.x_dir):
					for r in range(self.y_dir, self.y_diff, self.y_dir):
						if abs(r) == abs(c):
							if self.board[self.from_y + r, self.from_x + c]!= '  ':
						 		self.valid = False
			else:
				self.valid = True
		
		elif self.piece_kind == 'K':
			self.valid = (abs(self.x_diff) < 2 and abs(self.y_diff) < 2)
			# Castling (only possible after 6th ply)
			if (
					(self.move_num > 6) and
					(abs(self.x_diff) == 2 and self.y_diff == 0)
					):
				if (
						(self.x_dir == -1) and
			   			(not self.prev_turn.cant_castle_qs) and
			   			(self.board[self.to_y, self.to_x - 1] == '  ') and
			   			(self.board[self.to_y, self.to_x - 2] == '  ') and
			   			(self.board[self.to_y, self.to_x - 3] == '  ')
			   			):
					self.castle_qs = True
					self.valid = True
				elif (
						(self.x_dir == 1) and
						(not self.prev_turn.cant_castle_ks) and
			   			(self.board[self.to_y, self.to_x + 1] == '  ') and
			   			(self.board[self.to_y, self.to_x + 2] == '  ')
			   			):
					self.castle_ks = True
					self.valid = True
			else:
				self.castle_qs = False
				self.castle_ks = False

			if self.move_num > 2:
				self.cant_castle_qs = ((self.prev_turn.cant_castle_qs) or
								   	   (self.castle_qs) or
								       (self.castle_ks))
				self.cant_castle_ks = ((self.prev_turn.cant_castle_ks) or
								       (self.castle_qs) or
								       (self.castle_ks))
			else:
				self.cant_castle_qs = False
				self.cant_castle_ks = False

		else:
			self.valid = False
		self.check = check_if_check(self.board, self.turn)
		self.stalemate = not self.valid_move_exists and not self.check
		self.checkmate = not self.valid_moves_exists and self.check

		# Piece Counts and Points
		self.pieces_left = gs.pieces_left
		self.pieces_points = gs.pieces_points
			pc_value = {'Q':9, 'R':5, 'N':3, 'B':3, 'P':1}
			if self.capture:
				if self.en_passant:
					self.pieces_left[swap(turn)]['P']
					self.pieces_points[] -= 1
				else:
					# e.g. if wQ captured, pieces_left['w']['Q'] reduced by 1
					self.pieces_left[self.on_dest_sq[0]][self.on_dest_sq[-1]] -= 1
					self.pieces_points[] -= pc_value[self.on_dest_sq]
		
		self.pieces_left = {'w': {'Q':1, 'R':2, 'N':2, 'B':2, 'P':8},
						   {'b': {'Q':1, 'R':2, 'N':2, 'B':2, 'P':8}}}
		self.pieces_points = {'w': 39, 'b': 39}



	def is_checking(self, board):
		# Check if this move checks the opponent king by ANY piece
		# (Pieces ordered by general likelihood of giving check)
		colour = self.turn
		opp_colour = swap(self.turn)
		opp_king = opp_colour + 'K'
		for piece in ['Q', 'R', 'B', 'N', 'P']:
			move_xy = [
				(np.where(board == colour+piece)[0].item())
				(np.where(board == colour+piece)[1].item())
				(np.where(board == (opp_king)[0].item())),
				(np.where(board == (opp_king)[1].item()))
				]
			hypothetical_move = Move(board, move_xy)
			# Deemed a valid move if could capture the opponent's king
			if hypothetical_move.is_valid:
				return True
		return False

	def is_walking_into_check(self, board):
		# Would an opponent's piece be checking you if this move were made
		hypothetical_move = Move(gs, self)
		return hypothetical_move.is_checking

			




# ---UPDATE BOARD--------------------------------------------------------------
def update_board(board, move):
	new_board = board.copy()

	# Queening scenario: change pawn to queen...
	if move.piece_kind == 'P' and (move.to_y == 0 or move.to_y == 7):
		new_board[move.to_y, move.to_x] = str(move.piece_colour)+'Q'
	elif move.piece == 'bP' and move.to_y == 7:
		new_board[move.to_y, move.to_x] = 'bQ'
	# ...otherwise, simply move that same piece to the new square
	else:
		new_board[move.to_y, move.to_x] = new_board[move.from_y, move.from_x]
	new_board[move.from_y, move.from_x] = '  '
	
	# Castling scenarios: additional move required (jump rook over)
	if move.piece == 'K' and (move.to_x - move.from_x) == 2:
		board[move.to_y, move.to_x + 1] = '  '
		board[move.to_y, move.to_x - 1] = str(move.piece_colour)+'R'
	elif move.piece == 'K' and (move.to_x - move.from_x)==-2:
		board[move.to_y, move.to_x - 2] = '  '
		board[move.to_y, move.to_x + 1] = str(move.piece_colour)+'R'

	# En passant scenario: manually remove opponent's pawn
	if move.en_passant:
		if move.piece_colour == 'w':
			new_board[move.to_y + 1, move.to_x] = '  '
		else:
			new_board[move.to_y - 1, move.to_x] = '  '

	return new_board





# ---CONVERSIONS---------------------------------------------------------------
def to_file_rank(column_row):
	# <int list> {0,1,..,7}{0,1,..,7}   -->   <str>  {a,b,..,h}{1,2,..,8}
	file_rank = chr(97 + column_row[0]) + str(8 - column_row[1])
	return file_rank

def to_column_row(file_rank):
	# <str>  {a,b,..,h}{1,2,..,8}   -->   <int list> {0,1,..,7}{0,1,..,7}
	column_row = [ord(file_rank[0]) - 97, int(file_rank[1]) - 1]
	return column_row

def to_move_xy(click_xy):
	return ((click_xy[0]-100) // SQ_SIZE, (click_xy[1]-200) // SQ_SIZE)

def swap(turn):
	return 'b' if colour == 'w' else 'w'

def to_algebraic(move):
	# Move() object    -->    <str> in alegraic notation, like exd4+ f8=Q#
	# If not Castles; append characters to string one at a time
	if move.castle_ks:
		return 'O-O'
	elif move.castle_qs:
		return 'O-O-O'
	
	if move.piece_kind != 'P':
		move_return += move.piece_kind
	else:
		# If pawn move, use only letter from square it came from
		origin_sq = str(to_file_rank([move.from_x, move.from_y]))[0]
		move_return += origin_sq
		
	if move.capture:
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




# ---DRAW ON APP---------------------------------------------------------------
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

def game_over(message):
	print(message, ' Game Over.')




# ---MAIN GAME LOOP------------------------------------------------------------
def terminate():
	pg.quit()
	sys.exit()

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
			game_over_notice = gs.is_game_over()
			if not game_over_notice.empty():
				game_over(game_over_notice)

		# ---MOUSE IS CLICKED---
		if clicked:
			click valid = gs.is_click_valid()
			if click_valid:
				gs.move_xy = to_move_xy(gs.click_xy)
				if len(gs.move_xy) < 4:
					# A piece is selected and it's that colour to move)
					if ((len(gs.move_xy) == 2) and\
					    (gs.board[gs.move_xy[1]][gs.move_xy[0]]\
								.startswith(gs.turn))):
						highlight_sq(win, gs.turn, gs.move_xy)
				elif len(gs.move_xy) == 4:
					gs.new_move = Move(gs, move_xy)
					if new_move.valid:
						gs.make_move(new_move)
					else:
						gs.change_sq_sel(move_xy)
						clicked = ()  # Reset click information
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