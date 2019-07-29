import time

import chess.engine
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from constants import Side
from selenium_canvas import SeleniumCanvas
from vector_2d import Vector2D


class SeleniumChess:
    def __init__(self, driver):
        self.patterns = {
            'chessboard': 'game-board',
            'bottom_player_white': 'board-player-component board-player-bottom board-player-white undefined',
            'bottom_player_black': 'board-player-component board-player-bottom board-player-black undefined',
            'top_player_white': 'board-player-component board-player-top board-player-white undefined',
            'top_player_black': 'board-player-component board-player-top board-player-black undefined',
            'move': 'vertical-move-list-clickable',
            'selected_move': 'move-text-selectednf',
        }

        self.driver = driver

        self.graphics = SeleniumCanvas(self.driver)

        self.board = None
        self.chains = None
        self.board_dim = None
        self.piece_dim = None
        self.board_pos = None

    def try_set_elements(self):
        try:
            self.board = self.driver.find_element_by_id(self.patterns['chessboard'])
        except NoSuchElementException:
            return False  # All elements must be found. No point in continuing if even one is missing
        except Exception as e:
            print('Exception in getting chessboard element: {0}'.format(e))
            return False
        return True

    def update_variables(self):
        self.chains = webdriver.ActionChains(self.driver)
        self.board_dim = self.board.size.get('width')  # Board is square; either dimension will do
        self.piece_dim = self.board_dim // 8
        self.board_pos = Vector2D(self.board.location.get('x'), self.board.location.get('y'))

    def find_player_colour(self):
        try:
            self.driver.find_element_by_xpath("//div[@class='{0}']".format(self.patterns['bottom_player_white']))
            return Side.WHITE
        except NoSuchElementException:  # Not white
            try:
                self.driver.find_element_by_xpath("//div[@class='{0}']".format(self.patterns['bottom_player_black']))
                return Side.BLACK
            except NoSuchElementException:  # Not white or black
                return Side.NEITHER

    def get_selected_move(self):
        try:
            selected_move = self.driver.find_element_by_xpath(
                "//span[@class='{0}']".format(self.patterns['selected_move']))
            return selected_move.text
        except NoSuchElementException:
            print('Latest move not found')
        return None

    def get_move_list(self):
        script = ""
        script += "let elements = document.getElementsByClassName('{0}');".format(self.patterns['move'])
        script += "let contents = [];"
        script += "for (let i = 0; i < elements.length; i++) { contents.push(elements[i].innerText); }"
        script += "return contents;"

        try:
            start_time = time.time()

            move_list = self.driver.execute_script(script)

            print('Time to get move text: {0} seconds'.format(time.time() - start_time))

            return move_list
        except StaleElementReferenceException:
            return self.get_move_list()

    def notation_to_pos(self, ply, bottom_color):
        if bottom_color == Side.WHITE:
            pos = Vector2D(self.piece_dim * (ord(ply[0]) - 97), self.board_dim - self.piece_dim * int(ply[1]))
        elif bottom_color == Side.BLACK:
            pos = Vector2D(self.piece_dim * (7 - (ord(ply[0]) - 97)),
                           self.board_dim - self.piece_dim * (9 - int(ply[1])))
        else:
            print('Side to move should not be Side.NEITHER')
            return
        pos.x += self.board_pos.x
        pos.y += self.board_pos.y
        return pos

    def draw_move_squares(self, context_name, move, bottom_color):
        move_uci_string = move.uci()
        start_ply = move_uci_string[:2]
        end_ply = move_uci_string[2:4]
        first_pos = self.notation_to_pos(start_ply, bottom_color)
        second_pos = self.notation_to_pos(end_ply, bottom_color)
        dims = Vector2D(self.piece_dim, self.piece_dim)
        self.graphics.set_styles(context_name, visibility="'visible'")
        self.graphics.draw_filled_rect(context_name, first_pos, dims)
        self.graphics.draw_filled_rect(context_name, second_pos, dims)

    def draw_move_arrows(self, context_name, move, bottom_color):
        move_uci_string = move.uci()
        center_offset = self.piece_dim // 2
        start_ply = move_uci_string[:2]
        end_ply = move_uci_string[2:4]
        first_pos = self.notation_to_pos(start_ply, bottom_color)
        first_pos.x += center_offset
        first_pos.y += center_offset
        second_pos = self.notation_to_pos(end_ply, bottom_color)
        second_pos.x += center_offset
        second_pos.y += center_offset
        self.graphics.set_styles(context_name, visibility="'visible'")
        self.graphics.draw_arrow(context_name, first_pos, second_pos)

    def draw_score(self, context_name, move, score, bottom_color):
        move_uci_string = move.uci()
        center_offset = self.piece_dim // 2
        start_ply = move_uci_string[:2]
        end_ply = move_uci_string[2:4]
        first_pos = self.notation_to_pos(start_ply, bottom_color)
        first_pos.x += center_offset
        first_pos.y += center_offset
        second_pos = self.notation_to_pos(end_ply, bottom_color)
        second_pos.x += center_offset
        second_pos.y += center_offset
        text_pos = Vector2D((first_pos.x + second_pos.x) / 2, (first_pos.y + second_pos.y) / 2)

        relative_score = score.relative
        if relative_score.is_mate():
            if relative_score > chess.engine.Cp(0):
                fillStyle = "'Blue'"
            else:
                fillStyle = "'DarkRed'"
        else:
            numeric_score = relative_score.score()
            if numeric_score > 0:
                fillStyle = "'Green'"
            elif numeric_score < 0:
                fillStyle = "'Red'"
            else:
                fillStyle = "'Gray'"
        self.graphics.draw_centered_text(context_name, str(score), text_pos, fillStyle=fillStyle)
