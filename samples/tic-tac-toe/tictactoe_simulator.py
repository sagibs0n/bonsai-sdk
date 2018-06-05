import numpy
import random
import sys

from bonsai_ai import Luminance
from bonsai_ai import Config, Brain, Simulator
from bonsai_ai.logger import Logger

log = Logger()

letters = {"X": [[1, 0, 1], [0, 1, 0], [1, 0, 1]],
           "O": [[0, 1, 0], [1, 0, 1], [0, 1, 0]],
           " ": [[0, 0, 0], [0, 0, 0], [0, 0, 0]]}

POSMAP = {"X": 1, " ": 0, "O": -1}


class TicTacToeGame(object):
    def __init__(self, seed=42):
        random.seed(seed)
        self.board = [" "] * 10
        self.playerLetter, self.computerLetter = ('X', 'O')
        self.terminal = False
        self.reward = 0
        self.framecount = 0
        self.image = numpy.zeros((9, 9), dtype=numpy.uint8)

    def render(self):
        for i in range(3):
            for j in range(3):
                self.image[i*3:i*3+3, j*3:j*3+3] = letters[self.board[i*3+j]]
        image = Luminance(9, 9, self.image.ravel().tolist())
        return image

    def reset(self):
        self.board = [" "] * 10
        if random.randint(0, 1) == 0:
            self._computer_turn()
        self.terminal = False
        self.reward = 0
        return self.render()

    def _computer_turn(self):
        move = self.get_computer_move()
        self.make_move(self.computerLetter, move)

        if self.is_winner(self.computerLetter):
            self.reward = -1
            self.terminal = True
            log.game("\n\n Computer Won\n")
            self.print_board()
        elif self.is_board_full():
            self.reward = 0.5
            self.terminal = True
            log.game("\n\n Draw\n")
            self.print_board()

    def get_reward(self):
        return self.reward

    def make_move(self, letter, move):
        self.board[move] = letter

    def clear_space(self, move):
        self.board[move] = " "

    def is_winner(self, le):
        bo = self.board
        # Given a board and a player's letter, this function returns True
        # if that player has won.
        # We use bo instead of board and le instead of letter
        # so we don't have to type as much.
        return (
            (bo[7] == le and bo[8] == le and bo[9] == le) or  # across the top
            (bo[4] == le and bo[5] == le and bo[6] == le) or  # across the midd
            (bo[1] == le and bo[2] == le and bo[3] == le) or  # across the bott
            (bo[7] == le and bo[4] == le and bo[1] == le) or  # down the left
            (bo[8] == le and bo[5] == le and bo[2] == le) or  # down the middle
            (bo[9] == le and bo[6] == le and bo[3] == le) or  # down the right
            (bo[7] == le and bo[5] == le and bo[3] == le) or  # diagonal
            (bo[9] == le and bo[5] == le and bo[1] == le))  # diagonal

    def choose_random_move_from_list(self, moves_list):
        # Returns a valid move from the passed list on the passed board.
        # Returns None if there is no valid move.
        possible_moves = [i for i in moves_list if self.is_space_free(i)]

        if len(possible_moves) != 0:
            return random.choice(possible_moves)
        else:
            return None

    def get_computer_move(self):
        # Given a board and the computer's letter, determine where to move
        # and return that move.

        # Here is our algorithm for our Tic Tac Toe AI:
        # First, check if we can win in the next move
        for i in range(1, 10):
            if self.is_space_free(i):
                self.make_move(self.computerLetter, i)
                if self.is_winner(self.computerLetter):
                    self.clear_space(i)
                    return i
                else:
                    self.clear_space(i)

        # Check if the player could win on his next move, and block them.
        for i in range(1, 10):
            if self.is_space_free(i):
                self.make_move(self.playerLetter, i)
                if self.is_winner(self.playerLetter):
                    self.clear_space(i)
                    return i
                else:
                    self.clear_space(i)

        # Try to take one of the corners, if they are free.
        move = self.choose_random_move_from_list([1, 3, 7, 9])
        if move is not None:
            return move

        # Try to take the center, if it is free.
        if self.is_space_free(5):
            return 5

        # Move on one of the sides.
        return self.choose_random_move_from_list([2, 4, 6, 8])

    def is_board_full(self):
        # Return True if every space on the board has been taken.
        # Otherwise return False.
        return all([self.board[i] != " " for i in range(1, 10)])

    def is_space_free(self, move):
        # Return true if the passed move is free.
        return self.board[move] == " "

    def print_board(self):
        # This function prints out the board.
        board = self.board

        # "board" is a list of 10 strings representing the board
        # (ignore index 0)
        log.game('   |   |')
        log.game(' ' + board[7] + ' | ' + board[8] + ' | ' + board[9])
        log.game('   |   |')
        log.game('-----------')
        log.game('   |   |')
        log.game(' ' + board[4] + ' | ' + board[5] + ' | ' + board[6])
        log.game('   |   |')
        log.game('-----------')
        log.game('   |   |')
        log.game(' ' + board[1] + ' | ' + board[2] + ' | ' + board[3])
        log.game('   |   |')

    def advance(self, actions):

        # Player's turn.
        if self.is_space_free(actions['move']):
            self.make_move(self.playerLetter, actions['move'])
            if self.is_winner(self.playerLetter):
                log.game("\n\n Player Won\n")
                self.print_board()
                self.reward = 1
                self.terminal = True
                return self.render(), self.reward, self.terminal
            elif self.is_board_full():
                log.game("\n\n Draw\n")
                self.print_board()
                self.reward = 0.5
                self.terminal = True
                return self.render(), self.reward, self.terminal
            else:
                log.game(actions['move'])
                self.reward = 0.01
        else:
            log.game("space taken")
            self.reward = -0.1

        # If the game hasn't ended, have the game take a turn
        self._computer_turn()

        return self.render(), self.reward, self.terminal


class TicTacToeSim(Simulator):
    def __init__(self, brain, iteration_limit=0):
        super(TicTacToeSim, self).__init__(brain, 'tictactoe_simulator')

        self._env = TicTacToeGame()

    def episode_finish(self):
        log.gym("Episode {} reward: {}".format(
            self.episode_count, self.episode_reward))

    def episode_start(self, config):
        observation = self._env.reset()
        return {'image': observation}

    def simulate(self, action):
        observation, reward, done = self._env.advance(action)
        return {'image': observation}, reward, done


if __name__ == "__main__":
    config = Config(sys.argv)
    brain = Brain(config)
    sim = TicTacToeSim(brain)
    while sim.run():
        continue
