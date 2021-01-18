import os
from enum import Enum


class Side(Enum):
    WHITE = 1
    BLACK = 2
    NEITHER = 3

MULTIPV_MOVE_COLOURS = ["'red'", "'salmon'", "'darkred'"]

START_URL = 'https://www.chess.com/login_and_go?returnUrl=https%3A//www.chess.com/register'
PLAY_CHESS_URL = 'https://www.chess.com/live/'
START_POS_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

if os.name == 'nt':
    DRIVER_PATH = 'geckodriver.exe'
elif os.name == 'posix':
    DRIVER_PATH = './geckodriver'
