import os
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
# USERNAME = 'orgnaan'
# PASSWORD = 'narnia'
# USERNAME = "FoolGarbage"
# PASSWORD = "manastry"

START_POS_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

ENGINE_PATHS_WINDOWS = {
    'stockfish': 'stockfish-10-win/Windows/stockfish_10_x64_popcnt.exe',
    'strangler': 'Rodent III - Strangler/windows/RodentIII_x64_POPCNT_pgo.exe',
    'karpov': 'Rodent III - Karpov/windows/RodentIII_x64_POPCNT_pgo.exe',
    'alekhine': 'Rodent III - Alekhine/windows/RodentIII_x64_POPCNT_pgo.exe',
    'opental': 'OpenTal/opental_x64popcnt.exe',
    'naum': 'naum.exe',
    'amyan': 'Amyan 1.72/amyan.exe',
}

ENGINE_PATHS_LINUX = {
    'stockfish': 'stockfish-10-linux/Linux/stockfish_10_x64_modern'
}

ENGINE_PROTOCOLS = {
    'stockfish': 'uci',
    'strangler': 'uci',
    'karpov': 'uci',
    'alekhine': 'uci',
    'opental': 'uci',
    'naum': 'uci',
    'amyan': 'uci',
}

ENGINE_RELATIVE_DIRECTORY = 'Engines'
ENGINE_NAME = 'karpov'

ENGINE_PROTOCOL = ENGINE_PROTOCOLS[ENGINE_NAME]
ENGINE_SEARCH_DEPTH = 8
ENGINE_SEARCH_TIME = 1
ENGINE_ELO = 2000

if os.name == 'nt':
    DRIVER_PATH = 'geckodriver.exe'
elif os.name == 'posix':
    DRIVER_PATH = './geckodriver'
