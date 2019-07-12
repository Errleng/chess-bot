from enum import Enum


class Side(Enum):
    WHITE = 1
    BLACK = 2
    NEITHER = 3


DRAW_TYPE = 'arrow'

USING_MULTIPV = True
MULTIPV_MOVE_COUNT = 3
MULTIPV_MOVE_COLOURS = ["'red'", "'salmon'", "'darkred'"]

START_URL = 'https://www.chess.com/login_and_go?returnUrl=https%3A//www.chess.com/register'
PLAY_CHESS_URL = 'https://www.chess.com/live/'

USERNAME = 'monaeaei'
PASSWORD = 'emaaten'

START_POS_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

ENGINE_NAMES = {
    'stockfish': 'stockfish_9_x64.exe',
    'rybka': 'Rybkav2.3.2a.mp.x64',
}
ENGINE_RELATIVE_DIRECTORY = 'Engines'
ENGINE_NAME = ENGINE_NAMES['stockfish']
ENGINE_SEARCH_DEPTH = 6
