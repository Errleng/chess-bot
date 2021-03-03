import time
from configparser import ConfigParser

import chess
import chess.engine
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException

from constants import *
from selenium_chess import SeleniumChess


class Bot:
    def __init__(self):
        self.move_list = []
        self.cvs_ctx = []
        self.engine_infos = []
        self.engine_moves = []
        self.engine_scores = []
        self.player = None
        self.board = None
        self.last_move_list = []
        self.position_eval_count = 0

        self.config = ConfigParser()
        self.config.read('config.ini')

        self.driver = webdriver.Firefox(executable_path=DRIVER_PATH)
        self.load_engine(self.config['engine']['name'])
        self.interface = SeleniumChess(self.driver)

        self.setup_browser()
        self.setup_selenium_chess()
        self.limit = chess.engine.Limit(depth=self.config['engine'].getint('search_depth'))

    def game_end(move):
        return move == '1-0' or move == '0-1' or move == '1/2-1/2'

    def login(self, username, password):
        name = self.driver.find_element_by_id("username")
        pw = self.driver.find_element_by_id("password")
        name.send_keys(username)
        pw.send_keys(password)
        self.driver.find_element_by_name("login").click()

    def can_play(self):
        return len(self.move_list) > 0 and not Bot.game_end(self.move_list[-1]) or len(
            self.move_list) == 0 and self.player == Side.WHITE

    def load_engine(self, engine_name):
        engine_path = self.config['engine']['directory'] + '/'
        if os.name == 'nt':  # Windows
            engine_path += self.config['engine_paths_windows'][engine_name]
        elif os.name == 'posix':
            engine_path += self.config['engine_paths_linux'][engine_name]
        else:
            raise Exception('Unknown operating system: {0}'.format(os.name))

        engine_protocol = self.config['engine']['protocol']
        if engine_protocol == 'uci':
            self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        elif engine_protocol == 'xboard':
            self.engine = chess.engine.SimpleEngine.popen_xboard(engine_path)

        if 'name' in self.engine.id:
            print('Loaded engine {0}'.format(self.engine.id['name']))
        else:
            print('Engine name is unknown')

        options = {'UCI_LimitStrength': 'true',
                   'UCI_Elo': self.config['engine'].getint('elo')}

        for option in list(options.keys()):
            if option in self.engine.options:
                print(f'{option} is not an option for this engine')
                del options[option]

        self.engine.configure(options)

        print('Engine options')
        for option in self.engine.options.values():
            print(option)

    def setup_browser(self):
        self.driver.maximize_window()
        self.driver.get(START_URL)
        self.login(self.config['settings']['username'], self.config['settings']['password'])
        self.driver.get(PLAY_CHESS_URL)

    def setup_selenium_chess(self):
        self.cvs_ctx.append(('first_cvs', 'first_ctx'))
        self.interface.graphics.add_canvas_context(self.cvs_ctx[0][0], self.cvs_ctx[0][1])

    def run(self):
        while True:
            try:
                # print(f'sleep factor = {self.sleep_factor}')
                # time.sleep(self.sleep_factor)
                # self.sleep_factor = min(self.sleep_factor * 2, 10)
                time.sleep(0.1)

                start_time = time.time()

                if not self.interface.try_set_elements():
                    print('Cannot find chessboard')
                    continue

                intermediate_start_time = time.time()

                self.last_move_list = list(self.move_list)
                self.scrape_move_list()

                # check if position has updated
                if len(self.move_list) != len(self.last_move_list):
                    print('Position has changed')
                    self.position_eval_count = 0
                elif self.position_eval_count > self.config['engine'].getint('evaluation_tries'):
                    continue

                print('Time to get moves: {0} seconds'.format(time.time() - intermediate_start_time))

                intermediate_start_time = time.time()

                self.interface.update_variables()
                self.player = self.interface.find_player_colour()

                print('Time to update variables: {0} seconds'.format(time.time() - intermediate_start_time))

                print('Player = {0}'.format(self.player))
                print('Move list = {0}'.format(self.move_list))

                if not self.can_play():
                    print('Game has ended')
                    continue

                intermediate_start_time = time.time()
                self.make_board()  # self.board is None if failed
                if self.board is None:
                    self.move_list = []  # rebuild move list if there's an error
                    continue

                print('Time to make board: {0} seconds'.format(time.time() - intermediate_start_time))

                print(self.board)

                if self.board.turn:
                    turn = Side.WHITE
                    turn_name = "WHITE"
                else:
                    turn = Side.BLACK
                    turn_name = "BLACK"

                intermediate_start_time = time.time()

                try:
                    self.engine_eval()
                except Exception as e:
                    print('Exception evaluating: {0}'.format(e))
                    continue

                print('Time to evaluate: {0} seconds'.format(time.time() - intermediate_start_time))

                print('{0} is playing'.format(turn_name))
                for i in range(len(self.engine_moves)):
                    output_line = f'Move {i} = {self.engine_moves[i]}, Score = {self.engine_scores[i]}'
                    if self.config['engine'].getboolean('use_multipv'):
                        try:
                            output_line += f', PV = {self.board.variation_san(self.engine_infos[i]["pv"])}'
                        except Exception as e:
                            print(f'Exception in multi PV output: {e}')
                    print(output_line)

                intermediate_start_time = time.time()

                self.display_moves()

                print('Time to display: {0} seconds'.format(time.time() - intermediate_start_time))

                self.position_eval_count += 1

                end_time = time.time()
                print('Time elapsed = {0}s'.format(end_time - start_time))

                time.sleep(1)
            except StaleElementReferenceException:
                print('Stale elements. Retrying...')
            except Exception as exception:
                print(f'Main loop exception: {exception}')

    def scrape_move_list(self):
        # if len(self.move_list) > 0:
        #     last_move = self.interface.get_selected_move()  # by default the latest move is selected
        #     if last_move != self.move_list[-1]:
        #         self.move_list = self.interface.get_move_list()
        # else:
        self.move_list = self.interface.get_move_list()

    def make_board(self):
        self.board = chess.Board(START_POS_FEN)
        try:
            for move in self.move_list:
                self.board.push_san(move)
        except Exception as e:
            self.board = None
            print("Exception in pushing moves onto board: {0}".format(e))
            print(self.board)

    def engine_eval(self):
        try:
            if self.config['engine'].getboolean('use_multipv') and 'MultiPV' in self.engine.options:
                self.engine_infos.clear()
                self.engine_moves.clear()
                self.engine_scores.clear()

                infos = self.engine.analyse(self.board, self.limit,
                                            multipv=self.config['engine'].getint('multipv_count'))
                self.engine_infos = infos
                for i in range(len(infos)):
                    info = infos[i]
                    self.engine_moves.append(info['pv'][0])
                    self.engine_scores.append(info['score'])
            else:
                info = self.engine.analyse(self.board, self.limit)
                self.engine_moves = [info['pv'][0]]
                self.engine_scores = [info['score']]
        except Exception as e:
            print('Exception in evaluating: {0}'.format(e))
            print('Falling back on Stockfish')

            self.load_engine('stockfish')
            self.engine_eval()
            self.load_engine(self.config['engine']['name'])

    def draw_evaluation(self, context, move, score, player):
        main_ctx_name = self.cvs_ctx[0][1]
        if score.relative.is_mate():
            if score.relative > chess.engine.Cp(0):
                fill_style = "'Blue'"
            else:
                fill_style = "'DarkRed'"
        else:
            numeric_score = score.relative.score()
            if numeric_score > 0:
                fill_style = "'Green'"
            elif numeric_score < 0:
                fill_style = "'Red'"
            else:
                fill_style = "'Gray'"

        if self.config['interface'].getboolean('draw_wdl'):
            pov_wdl = score.wdl(ply=len(self.move_list))
            wdl = pov_wdl.relative
            win_prob, draw_prob, loss_prob = wdl.winning_chance(), wdl.drawing_chance(), wdl.losing_chance()
            expected_game_score = wdl.expectation()
            evaluation_text = f'{score.relative} ({int(100 * win_prob)}%)'
        else:
            evaluation_text = str(score.relative)

        self.interface.draw_move_text(main_ctx_name, move, evaluation_text, player, fill_style)

    def display_moves(self):
        try:
            main_ctx_name = self.cvs_ctx[0][1]
            self.interface.graphics.clear_context(main_ctx_name)
            if self.config['engine'].getboolean('use_multipv'):
                if self.config['interface']['draw_type'] == 'square':
                    for i in range(len(self.engine_moves)):
                        self.interface.graphics.set_styles(main_ctx_name,
                                                           fill_style=MULTIPV_MOVE_COLOURS[
                                                               i - self.config['engine'].getint('multipv_count')])
                        self.interface.draw_move_squares(main_ctx_name, self.engine_moves[i], self.player)
                        self.draw_evaluation(main_ctx_name, self.engine_moves[i], self.engine_scores[i], self.player)
                elif self.config['interface']['draw_type'] == 'arrow':
                    alpha_step = 1 / len(self.engine_moves)
                    for i in range(len(self.engine_moves)):
                        alpha = 1 - (i * alpha_step)
                        self.interface.graphics.set_styles(main_ctx_name, fill_style="'black'", global_alpha=str(alpha))
                        self.interface.draw_move_arrows(main_ctx_name, self.engine_moves[i], self.player)
                        self.draw_evaluation(main_ctx_name, self.engine_moves[i], self.engine_scores[i], self.player)
            else:
                if self.config['interface']['draw_type'] == 'square':
                    self.interface.graphics.set_styles(main_ctx_name, fill_style="'blue'", global_alpha='0.25')
                    self.interface.draw_move_squares(main_ctx_name, self.engine_moves[0], self.player)
                elif self.config['interface']['draw_type'] == 'arrow':
                    self.interface.graphics.set_styles(main_ctx_name, fill_style="'black'", global_alpha='1.0')
                    self.interface.draw_move_arrows(main_ctx_name, self.engine_moves[0], self.player)
                self.interface.draw_move_text(main_ctx_name, self.engine_moves[0], self.engine_scores[0], self.player)
        except Exception as e:
            print('Exception displaying moves: {0}'.format(e))
            print('Recreating contexts')
            self.setup_selenium_chess()
