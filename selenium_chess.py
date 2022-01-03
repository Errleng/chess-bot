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
            'chessboard': 'chess-board',
            'bottom_player_white': '.clock-white.clock-bottom',
            'bottom_player_black': '.clock-black.clock-bottom',
            'move': '.node',
            'selected_move': '.node.selected',
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
            self.board = self.driver.find_element_by_css_selector(self.patterns['chessboard'])
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
            self.driver.find_element_by_css_selector(self.patterns['bottom_player_white'])
            return Side.WHITE
        except NoSuchElementException:  # Not white
            try:
                self.driver.find_element_by_css_selector(self.patterns["bottom_player_black"])
                return Side.BLACK
            except NoSuchElementException:  # Not white or black
                return Side.NEITHER

    def get_selected_move(self):
        try:
            selected_move = self.driver.find_element_by_css_selector(self.patterns["selected_move"])
            return selected_move.text
        except NoSuchElementException:
            print('Latest move not found')
        return None

    def get_move_list(self):
        script = ""
        script += f"const moves = document.querySelectorAll('{self.patterns['move']}');"
        script += 'console.log(moves);'
        script += "if (moves === null) { return [] }"
        script += "return [...moves].map((move) => move.innerText);"

        try:
            move_list = self.driver.execute_script(script)
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

    def get_move_text_pos(self, move, bottom_color):
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
        return text_pos

    def draw_move_text(self, context_name, move, text, bottom_color, fill_style):
        text_pos = self.get_move_text_pos(move, bottom_color)
        self.graphics.draw_centered_text(context_name, text, text_pos, fill_style=fill_style)