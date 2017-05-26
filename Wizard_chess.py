import pickle
import threading
import RPi.GPIO as GPIO
from motor_class import Motor

motor_x = Motor(17,18,27,22)
motor_y = Motor(4,25,24,23)
motor_x.init()
motor_y.init()

GPIO.setup(7, GPIO.OUT)
GPIO.output(7,1)

motor_movement_dictionary_from_a1 = {
"00":[0,0],
"10":[0,0.65],
"20":[0,1.3],
"30":[0,1.95],
"40":[0,2.6],
"50":[0,3.25],
"60":[0,3.9],
"70":[0,4.55],
"01":[0.65,],
"11":[0.65,0.65],
"21":[0.65,1.3],
"31":[0.65,1.95],
"41":[0.65,2.6],
"51":[0.65,3.25],
"61":[0.65,3.9],
"71":[0.65,4.55],
"02":[1.3,0],
"12":[1.3,0.65],
"22":[1.3,1.3],
"32":[1.3,1.95],
"42":[1.3,2.6],
"52":[1.3,3.25],
"62":[1.3,3.9],
"72":[1.3,4.55],
"03":[1.95,0],
"13":[1.95,0.65],
"23":[1.95,1.3],
"33":[1.95,1.95],
"43":[1.95,2.6],
"53":[1.95,3.25],
"63":[1.95,3.9],
"73":[1.95,4.55],
"04":[2.6,0],
"14":[2.6,0.65],
"24":[2.6,1.3],
"34":[2.6,1.95],
"44":[2.6,2.6],
"54":[2.6,3.25],
"64":[2.6,3.9],
"74":[2.6,4.55],
"05":[3.25,0],
"15":[3.25,0.65],
"25":[3.25,1.3],
"35":[3.25,1.95],
"45":[3.25,2.6],
"55":[3.25,3.25],
"65":[3.25,3.9],
"75":[3.25,4.55],
"06":[3.9,0],
"16":[3.9,0.65],
"26":[3.9,1.3],
"36":[3.9,1.95],
"46":[3.9,2.6],
"56":[3.9,3.25],
"66":[3.9,3.9],
"76":[3.9,4.55],
"07":[4.55,0],
"17":[4.55,0.65],
"27":[4.55,1.3],
"37":[4.55,1.95],
"47":[4.55,2.6],
"57":[4.55,3.25],
"67":[4.55,3.9],
"77":[4.55,4.55],
}

class piece():
    pieces = {'white':{},'black':{}}
    pieces_taken = {'white':{},'black':{}}
    def __init__(self,piece_type,colour):
        self.piece_type=piece_type
        self.colour=colour
        self.no_of_moves = 0
        self.position = '00'
        self.moves_list = []

        if not self.piece_type in piece.pieces[self.colour]:
            piece.pieces[self.colour][self.piece_type] = [self]
        else:
            piece.pieces[self.colour][self.piece_type].append(self)


    def legal_move(self,rank_from,rank_to,file_from,file_to):
        valid_move=True
        return valid_move

class pawn(piece):
    def __init__(self, colour):
        piece.__init__(self,'pawn', colour)

    def legal_move(self,rank_from,rank_to,file_from,file_to):
        valid = True
        direction = 1
        if self.colour == 'white':
            direction = -1
        if rank_from == 1 or rank_from == 6:
            maximum_distance = 2
        else:
            maximum_distance = 1

        file_diference = abs(file_from-file_to)
        rank_diference = rank_to - rank_from
        if self.colour == 'black' and (rank_diference > maximum_distance or rank_diference <= 0) :
            valid = False
        elif self.colour == 'white' and (rank_diference < maximum_distance*-1 or rank_diference >=0):
            valid = False
        elif file_diference >1:
            valid = False
        elif file_diference == 1:
            if rank_diference != direction or (board[rank_to][file_to]==0 and not self.en_passant(rank_from,rank_to,file_from,file_to)):
                valid = False
        else:
            for x_rank in range(rank_from+direction,rank_to+direction,direction):
                if board[x_rank][file_from] != 0:
                    valid = False
                    break
        return valid

    def en_passant(self,rank_from,rank_to,file_from,file_to):
        valid = False
        if board[rank_from][file_to] != 0:
            piece_type = board[rank_from][file_to].piece_type
            moves_list = board[rank_from][file_to].moves_list
            if piece_type == 'pawn':
                if self.colour == 'white':
                    if rank_from == 3 and moves_list[-1] == '1'+str(file_to)+'-3'+str(file_to):
                        valid = True
                else:
                    if rank_from == 4 and moves_list[-1] == '6'+str(file_to)+'-4'+str(file_to):
                        valid = True
        return valid


class knight(piece):
    def __init__(self,colour):
        piece.__init__(self,'knight', colour)

    def legal_move(self,rank_from,rank_to,file_from,file_to):
        valid = True
        if abs(rank_from-rank_to) == 2:
            if abs(file_from-file_to) != 1:
                valid = False
        elif abs(file_from-file_to) == 2:
            if abs(rank_from-rank_to) != 1:
                valid = False
        else:
            valid = False
        return valid

class castle(piece):
    def __init__(self, colour):
        piece.__init__(self,'castle', colour)

    def legal_move(self,rank_from,rank_to,file_from,file_to):
        valid = True
        if file_to > file_from or rank_to > rank_from:
            direction = 1
        else:
            direction = -1

        if file_from != file_to and rank_from != rank_to:
            valid = False
        elif rank_from == rank_to:
            for x_file in range(file_from+direction, file_to,direction):
                if board[rank_to][x_file] != 0:
                    valid = False
                    break
        elif file_from == file_to:
            for x_rank in range(rank_from+direction, rank_to, direction):
                if board[x_rank][file_to] != 0:
                    valid = False
                    break
        return valid

class bishop(piece):
    def __init__(self,colour):
        piece.__init__(self,'bishop', colour)

    def legal_move(self,rank_from,rank_to,file_from,file_to):
        valid = True
        if rank_to > rank_from:
            direction = 1
        else:
            direction = -1

        if(rank_from+file_from == rank_to+file_to):
            y_file = file_from
            for x_rank in range(rank_from+direction,rank_to,direction):
                y_file -= direction
                if board[x_rank][y_file] != 0:
                    return False
        elif (rank_to-file_to)==(rank_from-file_from):
            y_file = file_from
            for x_rank in range(rank_from+direction,rank_to,direction):
                y_file += direction
                if board[x_rank][y_file] != 0:
                    return False
        else:
            valid =  False
        return valid

class king(piece):
    def __init__(self,colour):
        piece.__init__(self,'king', colour)

    def legal_move(self,rank_from,rank_to,file_from,file_to):
        valid = False
        if abs(rank_from-rank_to) <= 1 and abs(file_from-file_to) <= 1:
            valid = True
        elif self.can_castle(rank_from,rank_to,file_from,file_to):
            valid = True
        return valid
    def can_castle(self,rank_from,rank_to,file_from,file_to):
        valid = False
        if rank_from == rank_to and abs(file_from-file_to)==2 and self.no_of_moves ==0:
            pieces_havent_moved = False
            if file_to-file_from <0:
                direction = -1
                if board[rank_from][0].piece_type == 'castle' and board[rank_from][0].no_of_moves == 0:
                    pieces_havent_moved = True
            elif file_to-file_from >0:
                direction = 1
                if board[rank_from][7].piece_type == 'castle' and board[rank_from][7].no_of_moves == 0:
                    pieces_havent_moved = True
            if pieces_havent_moved:
                attacking_player = change_current_player(self.colour)
                for x_file in range(file_from,file_to+direction,direction):
                    square = str(rank_from)+str(x_file)
                    if (check_if_square_attacked(square,attacking_player,True)):
                        valid = False
                        break
                    else:
                        valid = True
            return valid


class queen(piece):
    def __init__(self,colour):
        piece.__init__(self,'queen',colour)

    def legal_move(self,rank_from,rank_to,file_from,file_to):
        valid = False
        if bishop.legal_move(self,rank_from,rank_to,file_from,file_to):
            valid = True
        elif castle.legal_move(self,rank_from,rank_to,file_from,file_to):
            valid = True
        return valid

board=[
       [0,0,0,0,0,0,0,0],
       [0,0,0,0,0,0,0,0],
       [0,0,0,0,0,0,0,0],
       [0,0,0,0,0,0,0,0],
       [0,0,0,0,0,0,0,0],
       [0,0,0,0,0,0,0,0],
       [0,0,0,0,0,0,0,0],
       [0,0,0,0,0,0,0,0],
      ]

piece_characters={'white':{"king":'\u2654','queen':'\u2655','castle':'\u2656','bishop':'\u2657','knight':'\u2658','pawn':'\u2659'},
'black':{'king':'\u265A','queen':'\u265B','castle':'\u265C','bishop':'\u265D','knight':'\u265E','pawn':'\u265F'}}
current_player = 'white'
valid_move = False
move_from = "99"
move_to = "99"
checkmate = False
moves_made = []

def clear_board(board):
    for x in range(len(board)):
        for y in range(len(board)):
            board[x][y] = 0

def reset_board(board):
    piece.pieces = {'white':{},'black':{}}
    clear_board(board)
    for rank_number in range(0, 8):
      for file_number in range(0, 8):
        current_piece = 0
        if rank_number == 0 or rank_number == 7:
            if rank_number == 0:
                colour = 'black'
            elif rank_number == 7:
                colour = 'white'
            if file_number == 0 or file_number == 7:
                current_piece =  castle(colour)
            if file_number == 1 or file_number == 6:
                current_piece =  knight(colour)
            if file_number == 2 or file_number == 5:
                current_piece =  bishop(colour)
            if file_number == 3:
                current_piece =  queen(colour)
            if file_number == 4:
                current_piece =  king(colour)
        elif rank_number == 1:
            current_piece =  pawn('black')
        elif rank_number == 6:
            current_piece =  pawn('white')
        if current_piece != 0:
            current_piece.position = str(rank_number)+str(file_number)
        board[rank_number][file_number] = current_piece

def display_board(board):
    for rank in range(0,len(board)):
        print('  _________________________________')
        print(str((rank+1))+' ',end="")
        for file in range(0,len(board)):
            if board[rank][file] == 0:
                print("|   ",end="")
            else:
                #print('| '+piece_characters[board[rank][file].colour][board[rank][file].piece_type],end = "")
                print('|'+board[rank][file].colour[:1]+board[rank][file].piece_type[:2],end="")
        print('|')
    print('  _________________________________')
    print("    a   b   c   d   e   f   g   h")
    print()

def display_moves_made(moves_made):
    print("   White        Black    ")
    print("-"*25)
    for x in range(0,len(moves_made),2):
        move_from = moves_made[x][-5:-3]
        move_to = moves_made[x][-2:]
        piece = moves_made[x][:-5]
        move_symbol = moves_made[x][-3]
        print(piece+convert_coordinates(move_from)+move_symbol+convert_coordinates(move_to)+" "*(12-len(moves_made[x]))+"|"+" "*(12-len((moves_made[x]))),end="")
        try:
            move_from = moves_made[x+1][-5:-3]
            move_to = moves_made[x+1][-2:]
            piece = moves_made[x+1][:-5]
            move_symbol = moves_made[x+1][-3]
            print(piece+convert_coordinates(move_from)+move_symbol+convert_coordinates(move_to))
        except IndexError:
            print("")

def get_move(from_or_to,current_player):
    vald_coords = False
    while not vald_coords:
        move = input(current_player.capitalize()+", please enter where to move "+from_or_to+" (file first)")
        vald_coords = check_valid_coordinates(move)
    rank = int(move[1]) - 1
    file = ord(move[0]) - 97
    move_coordinates = str(rank)+str(file)
    return move_coordinates

def move_piece(board,move_from, move_to, move_type):
    global motor_movement_dictionary_from_a1

    rank_from = int(move_from[0])
    file_from = int(move_from[1])
    rank_to = int(move_to[0])
    file_to = int(move_to[1])
    piece_to_move = board[rank_from][file_from]
    piece_to_move.no_of_moves += 1
    move_symbol = '-'
    if board[rank_to][file_to] != 0:
        take_piece(board[rank_to][file_to], move_to)
        move_symbol = 'x'
    if move_type == 'castling':
        castling(rank_from,file_from,file_to)
        move_symbol = "+"
    elif move_type == 'convert':
        board[rank_from][file_from] = change_pawn(board,rank_from,file_from)
        piece_to_move = board[rank_from][file_from]
        move_symbol = "="
    elif move_type == 'en-passant':
        take_piece(board[rank_from][file_to], move_to)
        board[rank_from][file_to] = 0

    board[rank_to][file_to] = piece_to_move
    board[rank_to][file_to].position = str(rank_to)+str(file_to)

    physically_move_from = motor_movement_dictionary_from_a1[move_from]
    physically_move_to = motor_movement_dictionary_from_a1[move_to]

    physically_move_x_from = physically_move_from[0]
    physically_move_y_from = physically_move_from[1]
    move_x = threading.Thread(group=None, target=motor_x.turn, args=(physically_move_x_from*Motor.REVOLUTION, Motor.ANTICLOCKWISE), name="motor_x")
    move_y = threading.Thread(group=None, target=motor_y.turn, args=(physically_move_y_from*Motor.REVOLUTION, Motor.CLOCKWISE), name="motor_y")
    move_x.start()
    move_y.start()
	move_x.join()
	move_y.join()

    physically_move_x_to = physically_move_to[0]
    physically_move_y_to = physically_move_to[1]

    physically_move_x = physically_move_x_from - physically_move_x_to
    physically_move_y = physically_move_y_from - physically_move_y_to
	
    GPIO.output(7,0)
    if physically_move_x < 0:
        move_x = threading.Thread(group=None, target=motor_x.turn, args=((abs(physically_move_x))*Motor.REVOLUTION, Motor.CLOCKWISE), name="motor_x")
    else:
        move_x = threading.Thread(group=None, target=motor_x.turn, args=(physically_move_x*Motor.REVOLUTION, Motor.ANTICLOCKWISE), name="motor_x")
    if physically_move_y < 0:
        move_y = threading.Thread(group=None, target=motor_y.turn, args=((abs(physically_move_y))*Motor.REVOLUTION, Motor.ANTICLOCKWISE), name="motor_y")
    else:
        move_y = threading.Thread(group=None, target=motor_y.turn, args=(physically_move_y*Motor.REVOLUTION, Motor.CLOCKWISE), name="motor_y")
    move_x.start()
    move_y.start()
	move_x.join()
	move_y.join()
    GPIO.output(7,1)
	
    reset_motor_x = threading.Thread(group=None, target=motor_x.turn, args=(physically_move_x_to*Motor.REVOLUTION, Motor.CLOCKWISE), name="reset_motor_x")
    reset_motor_y = threading.Thread(group=None, target=motor_y.turn, args=(physically_move_y_to*Motor.REVOLUTION, Motor.ANTICLOCKWISE), name="reset_motor_y")
    reset_motor_x.start()
    reset_motor_y.start()
	reset_motor_x.join()
	reset_motor_y.join()

    board[rank_from][file_from] = 0
    piece_to_move.moves_list.append(move_from+move_symbol+move_to)
    moves_made.append(piece_to_move.piece_type+":"+move_from+move_symbol+move_to)

def take_piece(piece_taken,move_to):
    global motor_movement_dictionary_from_a1

    if not piece_taken.piece_type in piece.pieces_taken[piece_taken.colour]:
        piece.pieces_taken[piece_taken.colour][piece_taken.piece_type] = [piece_taken]
    else:
        piece.pieces_taken[piece_taken.colour][piece_taken.piece_type].append(piece_taken)

    piece.pieces[piece_taken.colour][piece_taken.piece_type].remove(piece_taken)

    physically_take_piece = motor_movement_dictionary_from_a1[move_to]
    physically_take_piece_move_motor_x = physically_take_piece[0]
    physically_take_piece_move_motor_y = physically_take_piece[1]
    move_motor_x = threading.Thread(group=None, target=motor_x.turn, args=(physically_take_piece_move_motor_x*Motor.Revolution, Motor.ANTICLOCKWISE), name="take_piece_motor_x")
    move_motor_y = threading.Thread(group=None, target=motor_y.turn, args=(physically_take_piece_move_motor_y*Motor.Revolution, Motor.CLOCKWISE), name="take_piece_motor_x")
    move_motor_x.start()
    move_motor_y.start()
	move_motor_x.join()
	move_motor_y.join()

    GPIO.output(7,0)
    physically_move_piece_out_of_game = 5.2 - physically_take_piece_move_motor_x
    motor_x.turn(physically_move_piece_out_of_game, Motor.CLOCKWISE)
    GPIO.output(7,1)
	
    reset_motor_x = threading.Thread(group=None, target=motor_x.turn, args=(0.65*Motor.REVOLUTION, Motor.ANTICLOCKWISE), name="reset_motor_x")
    reset_motor_y = threading.Thread(group=None, target=motor_y.turn, args=(physically_take_piece_move_motor_y*Motor.REVOLUTION, Motor.ANTICLOCKWISE), name="reset_motor_y")
    reset_motor_x.start()
    reset_motor_y.start()
	reset_motor_x.join()
	reset_motor_y.join()

def castling(rank_from,file_from,file_to):
    if file_to > file_from:
        castle_position = str(rank_from)+'7'
        move_piece(board,castle_position,str(rank_from)+str(file_to-1),get_move_type(board,castle_position,str(rank_from)+str(file_to-1)))
    else:
        castle_position = str(rank_from)+'0'
        move_piece(board,castle_position,str(rank_from)+str(file_to+1))

def check_valid_coordinates(coordinates):
    if len(coordinates) != 2:
        return False
    if coordinates[0] not in ['a','b','c','d','e','f','g','h']:
        print("Please enter coordinates that actually exist!")
        return False
    if coordinates[1] not in['1','2','3','4','5','6','7','8']:
        print("Please enter coordinates that actually exist!")
        return False
    return True

def check_valid_move(board,move_from,move_to,current_player,comments,players_move=True):
    valid_move = True
    rank_from = int(move_from[0])
    file_from = int(move_from[1])

    rank_to = int(move_to[0])
    file_to = int(move_to[1])
    if board[rank_from][file_from] == 0:
        if comments:print("There is no piece there!")
        valid_move = False
    elif board[rank_from][file_from].colour != current_player:
        if comments:print("That's someone else's piece!")
        valid_move = False
    elif board[rank_to][file_to]!=0 and (board[rank_from][file_from].colour == board[rank_to][file_to].colour):
        if comments:print("You cannot take your own piece!")
        valid_move = False
    elif not board[rank_from][file_from].legal_move(rank_from,rank_to,file_from,file_to):
        if comments:print("A "+board[rank_from][file_from].piece_type+" cannot make that move!")
        valid_move = False
    elif players_move:
        if not moving_into_check(move_from,move_to,current_player):
            if comments:print("You cannot move into check!")
            valid_move = False
    return valid_move

def moving_into_check(move_from, move_to,current_player):
    valid_move = True
    rank_from = int(move_from[0])
    file_from = int(move_from[1])
    rank_to = int(move_to[0])
    file_to = int(move_to[1])

    attacking_player = change_current_player(current_player)

    board[rank_from][file_from].position = move_to
    temp_piece = board[rank_to][file_to]
    board[rank_to][file_to] = board[rank_from][file_from]
    board[rank_from][file_from] = 0
    for x in piece.pieces[attacking_player]:
        for each_piece in piece.pieces[attacking_player][x]:
            if check_in_check(board,attacking_player,each_piece.position):
                board[rank_from][file_from] = board[rank_to][file_to]
                board[rank_from][file_from].position = move_from
                board[rank_to][file_to] = temp_piece
                valid_move = False
                return valid_move
    board[rank_from][file_from] = board[rank_to][file_to]
    board[rank_from][file_from].position = move_from
    board[rank_to][file_to] = temp_piece
    return valid_move

def check_in_check(board,current_player,piece_positon):
    in_check = False
    king_position = piece.pieces[change_current_player(current_player)]['king'][0].position
    in_check = check_valid_move(board,piece_positon,king_position,current_player,False,players_move=False)
    return in_check

def check_king_can_move(king_position):
    can_move = False
    rank_from = int(king_position[0])
    file_from = int(king_position[1])
    current_player = board[rank_from][file_from].colour
    for rank in range(-1,2):
        for file in range(-1,2):
            if rank_from+rank >= 0 and rank_from+rank <=7 and file_from+file >= 0 and file_from+file <= 7:
                current_position = str(rank_from+rank)+str(file_from+file)
                if check_valid_move(board,king_position,current_position,current_player,False):
                    can_move = True
                    return can_move
    return can_move

def check_checkmate(board,attacked_player,piece_position):
    king_position = piece.pieces[attacked_player]['king'][0].position
    piece_rank = int(piece_position[0])
    piece_file = int(piece_position[1])
    king_rank = int(king_position[0])
    king_file = int(king_position[1])
    rank_difference = king_rank - piece_rank
    file_difference = king_file - piece_file
    checkmate = True
    piece_type = board[piece_rank][piece_file].piece_type

    if check_king_can_move(king_position):
        checkmate = False
    elif check_if_square_attacked(piece_position,attacked_player,True):
        checkmate = False
    elif piece_type == 'castle' or (piece_type == 'queen' and (rank_difference == 0 or file_difference == 0)):
        if king_file > piece_file or king_rank > piece_rank:
            direction = 1
        else:
            direction = -1

        if piece_rank == king_rank:
            for x_file in range(piece_file+direction, king_file,direction):
                square = str(piece_rank)+str(x_file)
                if check_if_square_attacked(square, attacked_player,False):
                    checkmate = False
                    break
        elif piece_file == king_file:
            for x_rank in range(piece_rank+direction, king_rank, direction):
                square = str(x_rank)+str(piece_file)
                if check_if_square_attacked(square, attacked_player,False):
                    checkmate = False
                    break
    elif piece_type == 'bishop' or (piece_type == 'queen' and (rank_difference != 0 and file_difference != 0)):
        if king_rank > piece_rank:
            direction = 1
        else:
            direction = -1
        if(piece_rank+piece_file == king_rank+king_file):
            y_file = piece_file
            for x_rank in range(piece_rank+direction,king_rank,direction):
                y_file -= direction
                square = str(x_rank)+str(y_file)
                if check_if_square_attacked(square,attacked_player,False):
                    checkmate = False
                    break
        elif (king_rank-king_file)==(piece_rank-piece_file):
            y_file = piece_file
            for x_rank in range(piece_rank+direction,king_rank,direction):
                y_file += direction
                square = str(x_rank)+str(y_file)
                if check_if_square_attacked(square, attacked_player,False):
                    checkmate = False
    return checkmate

def get_new_piece(old_piece):
    piece_to_make = input("Would you like to convert the pawn into a\nqueen(q), castle(c),bishop(b) or knight(k)?")
    if piece_to_make.lower() in ['q','queen']:
        new_piece = queen(old_piece.colour)
    elif piece_to_make.lower() in ['c','castle']:
        new_piece = castle(old_piece.colour)
    elif piece_to_make.lower() in ['b','bishop']:
        new_piece = bishop(old_piece.colour)
    elif piece_to_make.lower() in ['k','knight']:
        new_piece = castle(old_piece.colour)
    new_piece.no_of_moves = old_piece.no_of_moves
    new_piece.position = old_piece.position
    return new_piece

def get_move_type(board,move_from, move_to):
    rank_from = int(move_from[0])
    file_from = int(move_from[1])
    rank_to = int(move_to[0])
    file_to = int(move_to[1])
    piece_to_move = board[rank_from][file_from]
    if piece_to_move.piece_type == 'king' and abs(file_from-file_to) == 2:
        move_type = 'castling'
    elif piece_to_move.piece_type == 'pawn' and ((piece_to_move.colour == 'white' and rank_to == 0) or (piece_to_move.colour == 'black' and rank_to == 7)):
        move_type = 'convert'
    elif piece_to_move.piece_type == 'pawn' and board[rank_to][file_to]==0 and piece_to_move.en_passant(rank_from,rank_to,file_from,file_to):
        move_type = 'en-passant'
    else:
        move_type = 'normal'
    return move_type	

def change_pawn(board,rank,file, piece_type=None):
    if __name__ == '__main__':
        new_piece = get_new_piece(board[rank][file])
    else:
        if piece_type == 'queen':
            new_piece = new_piece = queen(board[rank][file].colour)
        elif piece_type == 'castle':
            new_piece = new_piece = castle(board[rank][file].colour)
        elif piece_type == 'bishop':
            new_piece = new_piece =  bishop(board[rank][file].colour)
        elif piece_type == 'knight':
            new_piece = new_piece = knight(board[rank][file].colour)

    take_piece(board[rank][file])
    return new_piece

def change_current_player(current_player):
    if current_player == 'white':
        current_player = 'black'
    else:
        current_player = 'white'
    return current_player

def check_if_square_attacked(square,attacking_player,include_king):
    attacking = False
    attacking_pieces = []
    for current_piece_type in piece.pieces[attacking_player]:
        if not (current_piece_type == 'king' and include_king == False):
            for current_piece in piece.pieces[attacking_player][current_piece_type]:
                piece_position = current_piece.position
                attacking = check_valid_move(board,piece_position,square,attacking_player,False)
                if attacking:
                    return True
    return attacking

def convert_coordinates(coordinates):
    rank = int(coordinates[0])
    file = int(coordinates[1])
    result = chr(file+97)+str(rank+1)
    return result

def display_taken_pieces():
    black = []
    white = []
    for x in piece.pieces_taken['white']:
        for y in range(len(piece.pieces_taken['white'][x])):
            white.append(x)
    for x in piece.pieces_taken['black']:
        for y in range(len(piece.pieces_taken['black'][x])):
            black.append(x)
    print("Pieces Taken\n")
    print("White | Black")
    print('--------------')
    for x in range(max(len(white),len(black))):
        total = ""
        try:
            total += white[x]+" "*(6-len(white[x]))
        except IndexError:
            total += "      "
        total += "|"
        try:
            total += black[x]+" "*(6-len(black[x]))
        except IndexError:
            total += "      "
        print(total)

if __name__ == '__main__':
    reset_board(board)
    display_board(board)
    while not checkmate:
        valid_move = False
        while not valid_move:
            move_from = (get_move('from',current_player))
            move_to = get_move('to',current_player)
            valid_move = check_valid_move(board,move_from,move_to,current_player,True)
            if not valid_move:
                print('Please Enter a valid move!')

        move_type = get_move_type(board,move_from, move_to)
        move_piece(board,move_from,move_to,move_type)
        display_board(board)
        if check_in_check(board,change_current_player(current_player),move_to):
            if check_checkmate(board,current_player,move_to):
                print("Checkmate")
                print(current_player.capitalize()+' wins!')
                checkmate = True
            else:
                print("Check")
        current_player = change_current_player(current_player)
    print("End of Game")
    GPIO.cleanup()
