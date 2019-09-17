import math

from selenium.common.exceptions import NoSuchElementException

from js_classes import JSCanvas, JSContext
from vector_2d import Vector2D


class SeleniumCanvas:
    def __init__(self, driver):
        self.driver = driver
        # self.canvases = []
        self.contexts = {}

    def create_canvas_context(self, canvas, context):
        script = "window.{0} = document.createElement('canvas');" \
                 "{0}.id = {0};" \
                 "{0}.width = {1};" \
                 "{0}.height = {2};" \
                 "{0}.style.width = {3};" \
                 "{0}.style.height = {4};" \
                 "{0}.style.position = {5};" \
                 "{0}.style.left = {6};" \
                 "{0}.style.top = {7};" \
                 "{0}.style.zIndex = {8};" \
                 "{0}.style.pointerEvents = {9};" \
                 "document.body.appendChild({0});" \
                 "window.{10} = {0}.getContext('2d');" \
                 "{10}.id = {10};" \
                 "{10}.globalAlpha = {11};" \
                 "{10}.font = {12};".format(canvas.name,
                                            canvas.width,
                                            canvas.height,
                                            canvas.style_width,
                                            canvas.style_height,
                                            canvas.style_position,
                                            canvas.style_left,
                                            canvas.style_top,
                                            canvas.style_zIndex,
                                            canvas.style_pointerEvents,
                                            context.name,
                                            context.globalAlpha,
                                            context.font)

        self.driver.execute_script(script)

    def add_canvas_context(self, canvas_name, context_name):
        new_canvas = JSCanvas(canvas_name)
        new_context = JSContext(context_name, new_canvas)
        self.create_canvas_context(new_canvas, new_context)
        # self.canvases.append(new_canvas)
        # self.contexts.append(new_context)
        self.contexts[context_name] = new_context

    def check_missing_contexts(self):
        missing = []

        for context in self.contexts:
            try:
                self.driver.find_element_by_id(context.name)
            except NoSuchElementException:
                missing.append(context)

        for context in missing:
            self.create_canvas_context(context.canvas, context)

    def clear_context(self, context_name):
        context = self.contexts[context_name]
        script = "{0}.clearRect(0, 0, {1}.width, {1}.height);".format(context.name, context.canvas.name)
        self.driver.execute_script(script)

    def set_styles(self, context_name, visibility=None, strokeStyle=None, fillStyle=None, globalAlpha=None, font=None):
        context = self.contexts[context_name]
        canvas_name = context.canvas.name

        script = ""
        if visibility is not None:
            script += "{0}.style.visibility = {1};".format(canvas_name, visibility)
        if strokeStyle is not None:
            script += "{0}.strokeStyle = {1};".format(canvas_name, strokeStyle)
        if fillStyle is not None:
            script += "{0}.fillStyle = {1};".format(context.name, fillStyle)
        if globalAlpha is not None:
            script += "{0}.globalAlpha = {1};".format(context.name, globalAlpha)
        if font is not None:
            script += "{0}.font = {1};".format(context.name, font)

        self.driver.execute_script(script)

    def draw_text(self, context_name, text, pos):
        context = self.contexts[context_name]
        script = "{0}.fillText({1}, {2}, {3});".format(context.name, text, pos.x, pos.y)
        self.driver.execute_script(script)

    def draw_centered_text(self, context_name, text, pos, strokeStyle="'black'", fillStyle=None):
        context = self.contexts[context_name]
        script = ""
        script += "{0}.textAlign = 'center';".format(context.name)

        if strokeStyle is not None:
            self.set_styles(context.name, strokeStyle=strokeStyle, globalAlpha='1.0')
        script += "{0}.strokeText('{1}', {2}, {3});".format(context.name, text, pos.x, pos.y)

        if fillStyle is not None:
            self.set_styles(context.name, fillStyle=fillStyle)
        script += "{0}.fillText('{1}', {2}, {3});".format(context.name, text, pos.x, pos.y)

        self.driver.execute_script(script)

    def draw_filled_rect(self, context_name, pos, dim):
        context = self.contexts[context_name]
        script = "{0}.fillRect({1}, {2}, {3}, {4});".format(context.name, pos.x, pos.y, dim.x, dim.y)
        self.driver.execute_script(script)

    def draw_arrow(self, context_name, from_pos, to_pos):
        context = self.contexts[context_name]
        head_length = 20
        line_width = 5
        angle = math.atan2(to_pos.y - from_pos.y, to_pos.x - from_pos.x)
        off_from = Vector2D(to_pos.x - head_length * math.cos(angle - math.pi / 7),
                            to_pos.y - head_length * math.sin(angle - math.pi / 7))
        off_to = Vector2D(to_pos.x - head_length * math.cos(angle + math.pi / 7),
                          to_pos.y - head_length * math.sin(angle + math.pi / 7))
        script = "{0}.beginPath();" \
                 "{0}.lineWidth = {1};" \
                 "{0}.moveTo({2}, {3});" \
                 "{0}.lineTo({4}, {5});" \
                 "{0}.moveTo({4}, {5});" \
                 "{0}.lineTo({6}, {7});" \
                 "{0}.lineTo({8}, {9});" \
                 "{0}.lineTo({4}, {5});" \
                 "{0}.lineTo({6}, {7});" \
                 "{0}.stroke();" \
                 "{0}.fill();".format(context.name,
                                      line_width,
                                      from_pos.x,
                                      from_pos.y,
                                      to_pos.x,
                                      to_pos.y,
                                      off_from.x,
                                      off_from.y,
                                      off_to.x,
                                      off_to.y)

        self.driver.execute_script(script)
