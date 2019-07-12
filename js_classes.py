class JSCanvas:
    def __init__(self, name):
        self.name = name
        self.set_defaults()

    def set_defaults(self):
        self.width = 'window.innerWidth'
        self.height = 'window.innerHeight'

        self.style_width = "'100%'"
        self.style_height = "'100%'"

        self.style_position = "'absolute'"

        self.style_left = '0'
        self.style_top = '0'

        self.style_zIndex = "'100000'"

        self.style_pointerEvents = "'none'"


class JSContext:
    def __init__(self, name, canvas):
        self.name = name
        self.canvas = canvas
        self.set_defaults()

    def set_defaults(self):
        self.globalAlpha = '0.3'
        self.font = "'30px Arial'"
