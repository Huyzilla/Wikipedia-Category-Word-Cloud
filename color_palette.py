class ColorPalette(object):
    def __init__(self, colors):
        self.colors = colors
        self.name = self.__class__.__name__.replace('ColorPalette', '')

class MaterialColorPalette(ColorPalette):
    def __init__(self):
        super().__init__(["#E57373", "#F06292", "#FFCDD2", "#F8BBD0", "#FF99CC", "#E91E63"])

class BrightColorPalette(ColorPalette):
    def __init__(self):
        super().__init__(["#FFD700", "#FFC107", "#FF8F00", "#FF5722", "#F4511E", "#E64A19"])

class PastelColorPalette(ColorPalette):
    def __init__(self):
        super().__init__(["#C5CAE9", "#B3E5FC", "#66D9EF", "#4DB6AC", "#81C784", "#8BC34A"])

class DarkColorPalette(ColorPalette):
    def __init__(self):
        super().__init__(["#455A64", "#37474F", "#455A64", "#78909C", "#546E7A", "#455A64"])

class RGBColorPalette(ColorPalette):
    def __init__(self):
        super().__init__(["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#00FFFF", "#FF00FF"])

def get_all_color_palettes():
    return [MaterialColorPalette(), BrightColorPalette(), PastelColorPalette(), DarkColorPalette(), RGBColorPalette()]