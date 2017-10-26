import threading
import chess
import chess.uci
from abc import abstractmethod

import RPi.GPIO as GPIO
from motor_class import Motor


class Player:
    @abstractmethod
    def get_next_move(self, board):
        pass


class HumanPlayer(Player):
    def get_next_move(self, board):
        possible_moves = list(map(lambda move: move.uci(), board.generate_legal_moves()))
        print('Possible moves you can make: {}'.format(possible_moves))

        while True:
            move_uci_str = input('{}, please enter where to move. '.format(get_player_for_current_turn(board)))
            try:
                move = chess.Move.from_uci(move_uci_str.rstrip().lstrip())
            except ValueError:
                print('"{}" not formatted correctly'.format(move_uci_str))
                continue

            moved_piece = board.piece_at(move.from_square)

            if move in board.legal_moves:
                break
            elif moved_piece is None:
                print('No piece is there!')
            elif moved_piece.color != board.turn:
                print("That's someone else's piece!")
            elif board.piece_at(move.to_square) is not None and board.piece_at(move.to_square).color == board.turn:
                print('You cannot take your own piece!')
            elif board.is_into_check(move):
                print('You cannot move into check!')
            else:
                print('A {} cannot make that move!'.format(chess.PIECE_NAMES[moved_piece.piece_type]))

        return move


class ComputerPlayer(Player):
    def __init__(self, uci_engine_path, skill_level, think_time_ms=100):
        """
        Initialize the computer
        :param uci_engine_path: the path to the uci engine executable
        :param skill_level: How good of a player it is. For stockfish this can be anything in he range of [0, 20],
        where 20 is the best, and 0 is the worst
        :param think_time_ms: how long the engine should spend thinking each turn in milliseconds. default 100ms
        """
        self.engine = chess.uci.popen_engine(uci_engine_path)
        self.engine.uci()

        # see http://support.stockfishchess.org/kb/advanced-topics/engine-parameters for stockfish parameters.
        # note: if you don't use stockfish these will be different
        opts = {'Skill Level': skill_level}
        self.engine.setoption(opts)

        self.think_time_ms = think_time_ms

    def get_next_move(self, board):
        self.engine.ucinewgame()
        self.engine.position(board)
        best_move, ponder_move = self.engine.go(movetime=self.think_time_ms)
        self.engine.stop()
        return best_move


class Magnet:
    """
    Simple wrapper around GPIO calls, just to make it more clear what's g oin
    """

    @staticmethod
    def initialize():
        """
        Sets up the magnet
        :return: none
        """
        GPIO.setup(7, GPIO.OUT)

    @staticmethod
    def grab():
        """
        Grab a piece with the magnet
        :return: none
        """
        GPIO.output(7, 0)

    @staticmethod
    def release():
        """
        Release the piece from the magnet
        :return: none
        """
        GPIO.output(7, 1)

    @staticmethod
    def cleanup():
        """
        Cleans up the magnet
        :return: none
        """
        GPIO.cleanup()


class MotorMover:
    """
    Handles moving the motor to a specific position on the board
    """

    def __init__(self, motor_x, motor_y, unit_dist=0.65):
        """
        Initialize the motor mover
        :param motor_x: motor for the x axis
        :param motor_y: motor for the y axis
        :param unit_dist: distance that traveling 1 unit takes
        """
        self.x = 0
        self.y = 0
        self.motors = [motor_x, motor_y]
        self.unit_dist = unit_dist

        for motor in self.motors:
            motor.init()

    def _compute_dist_and_rot_dir(self, new_value, old_value):
        """
        Calculates the distance and rotation that the motor has to travel for going to a new location
        :param new_value: the new location
        :param old_value: the old location
        :return: (distance, rotation_direction), where rotation_direction is either Motor.CLOCKWISE or Motor.ANTICLOCKWISE
        """
        distance = self.unit_dist * abs(old_value - new_value)
        rotation_direction = Motor.CLOCKWISE if new_value > old_value else Motor.ANTICLOCKWISE
        return distance, rotation_direction

    def _start_moving_motor(self, motor_ind, distance, rotation_direction):
        """
        :param motor_ind: The index into self.motors that the motor is at
        :param distance: the distance to move
        :param rotation_direction: the direction to turn the motor
        :return: the thread that was started
        """
        motor_thread = threading.Thread(group=None, target=self.motors[motor_ind].turn,
                                        args=(distance * Motor.Revolution, rotation_direction),
                                        name="motor" + str(motor_ind))

        motor_thread.start()
        return motor_thread

    def move_to_x(self, x):
        """
        Move only along the x axis
        :param x: the new x value
        :return: none
        """
        distance, rotation = self._compute_dist_and_rot_dir(x, self.x)
        motor_x_thread = self._start_moving_motor(0, distance, rotation)
        motor_x_thread.join()

        self.x = x

    def move_to_y(self, y):
        """
        Move only along the y axis
        :param y: the new y value
        :return: none
        """
        distance, rotation = self._compute_dist_and_rot_dir(y, self.y)
        motor_y_thread = self._start_moving_motor(1, distance, rotation)
        motor_y_thread.join()

        self.y = y

    def move_to(self, x, y):
        """
        Move to a new location along both axes
        :param x: the new x value
        :param y: the new y value
        :return: none
        """
        x_distance, x_rotation = self._compute_dist_and_rot_dir(x, self.x)
        y_distance, y_rotation = self._compute_dist_and_rot_dir(y, self.y)

        motor_x_thread = self._start_moving_motor(0, x_distance, x_rotation)
        motor_y_thread = self._start_moving_motor(1, y_distance, y_rotation)

        motor_x_thread.join()
        motor_y_thread.join()

        self.x = x
        self.y = y

    def __str__(self):
        return 'MotorMover({}, {})'.format(self.x, self.y)


def get_player_for_current_turn(board):
    return chess.COLOR_NAMES[board.turn].capitalize()


def execute_move(board, move, mover):
    rank_from = chess.square_rank(move.from_square)
    file_from = chess.square_file(move.from_square)
    rank_to = chess.square_rank(move.to_square)
    file_to = chess.square_file(move.to_square)

    # take any capture piece
    if board.piece_at(move.to_square) is not None:
        take_piece(move.to_square, mover)
    elif board.is_en_passant(move):
        take_piece(chess.square(rank_from, file_to), mover)

    # move the rook if this is a castling move
    if board.is_castling(move):
        if board.is_queenside_castling(move):
            mover.move_to(0, rank_from)
            Magnet.grab()
            mover.move_to(file_to + 1, rank_from)
            Magnet.release()
        elif board.is_kingside_castling(move):
            mover.move_to(7, rank_from)
            Magnet.grab()
            mover.move_to(file_to - 1, rank_from)
            Magnet.release()

    # if this is a promotion move, move the piece off the board and wait for user to replace it
    if move.promotion is not None:
        take_piece(move.from_square, mover)
        input('Please replace the {} at {} with a {}, and hit enter once done.'.format(
            board.piece_at(move.from_square), chess.SQUARE_NAMES[move.from_square], chess.PIECE_NAMES[move.promotion]))

    # move the actual piece
    mover.move_to(file_from, rank_from)
    Magnet.grab()
    mover.move_to(file_to, rank_to)
    Magnet.release()

    board.push(move)


def take_piece(square, mover):
    """
    Moves the captured piece off of the board
    :param square: the square the piece is on
    :param mover: the MotorMover
    :return: none
    """
    rank = chess.square_rank(square)
    file = chess.square_file(square)

    mover.move_to(file, rank)
    Magnet.grab()
    mover.move_to_x(8)
    Magnet.release()


def display_board(board):
    # note: this was modified from chess.BaseBoard.__str__ method. so print(board) works just fine, but doesn't actually
    # print the ranks & files, which this modification does.
    builder = []

    files = [' ', ' ']
    files.extend(chess.FILE_NAMES)
    builder.append(' '.join(files))
    builder.append('')

    for i in reversed(range(8)):
        rank_entries = [chess.RANK_NAMES[i], ' ']
        for j in range(8):
            piece = board.piece_at(chess.square(j, i))
            rank_entries.append('.' if piece is None else piece.symbol())
        rank_entries.append(' ')
        rank_entries.append(chess.RANK_NAMES[i])
        builder.append(' '.join(rank_entries))

    builder.append('')
    builder.append(' '.join(files))

    print('\n'.join(builder))


def display_taken_pieces(pieces_taken):
    print("Pieces Taken")
    print("White | Black")
    print('--------------')
    white_taken = len(pieces_taken[chess.WHITE])
    black_taken = len(pieces_taken[chess.BLACK])
    for i in range(max(white_taken, black_taken)):
        white_str = str(pieces_taken[chess.WHITE][i]) if i < white_taken else '-'
        black_str = str(pieces_taken[chess.BLACK][i]) if i < black_taken else '-'
        print('{:<6} | {:<6}'.format(white_str, black_str))


def display_moves_made(moves_made):
    print("   White        Black    ")
    print("-" * 25)
    for i in range(len(moves_made)):
        move, piece, captured_piece = moves_made[i]
        print('{} {}\t\t'.format(piece, move), end=('\n' if i % 2 == 1 else ''))
    print('')


def setup_players():
    play_computer = input('Play against a computer (y/n)? ')
    if play_computer:
        player_color_str = input('What color do you want to play as (w/b)? ')
        player_color = chess.WHITE if player_color_str == 'w' else chess.BLACK

        # modify the skill level here if you want to make the computer better or worse.
        # 0 is the worst, 20 is the best
        players = {player_color: HumanPlayer(), not player_color: ComputerPlayer('./stockfish_8_x64', skill_level=10)}
    else:
        players = {chess.WHITE: HumanPlayer(), chess.BLACK: HumanPlayer()}
    return players


def main():
    players = setup_players()

    mover = MotorMover(Motor(17, 18, 27, 22), Motor(4, 25, 24, 23))

    # initialize the magnet and make sure its not grabbing anything
    Magnet.initialize()
    Magnet.release()

    # initialize the board
    board = chess.Board()
    moves_made = []
    pieces_taken = {chess.WHITE: [], chess.BLACK: []}

    display_board(board)
    while not board.is_checkmate():
        move = players[board.turn].get_next_move(board)

        moved_piece = board.piece_at(move.from_square)
        captured_piece = board.piece_at(move.to_square)
        moves_made.append((move, moved_piece, captured_piece))

        if board.piece_at(move.to_square) is not None:
            pieces_taken[board.turn].append(captured_piece)

        execute_move(board, move, mover)

        display_board(board)
        # display_taken_pieces(pieces_taken)
        # display_moves_made(moves_made)

        if board.is_check():
            print('Check')

    print('Checkmate')
    print('{} wins!'.format(chess.COLOR_NAMES[board.turn]))
    print("End of Game")

    mover.move_to(0, 0)

    Magnet.cleanup()


if __name__ == '__main__':
    main()
