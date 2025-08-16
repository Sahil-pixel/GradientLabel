from kivy.app import App
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color

from kivy.metrics import dp, sp
from kivy.core.text import Label as CoreLabel
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, StringProperty
from kivy.lang import Builder

from gradient4kivy.gradient import GLGradient
import numpy as np


class GradientLabel(Label):
    start_color = ListProperty([1, 0, 0, 1])
    end_color = ListProperty([0, 0, 1, 1])
    mode = StringProperty("diagonal")  # default mode

    def __init__(self, start_color=None, end_color=None, mode="diagonal", **kwargs):
        super().__init__(**kwargs)
        if start_color:
            self.start_color = start_color
        if end_color:
            self.end_color = end_color
        self.mode = mode  # user can pass horizontal/vertical/radial/diagonal
        self.color = (1, 1, 1, 0)  # hide default text
        Clock.schedule_once(lambda dt: self._update(), 0)

    def _update(self):
        core = CoreLabel(text=self.text, font_size=self.font_size)
        core.refresh()
        w, h = core.texture.size
        self.texture_size = (w, h)

        # Create gradient based on mode
        if self.mode == "horizontal":
            grad_tex = GLGradient.horizontal(size=(w, h),
                                             left_color=self.start_color,
                                             right_color=self.end_color)
        elif self.mode == "vertical":
            grad_tex = GLGradient.vertical(size=(w, h),
                                           top_color=self.start_color,
                                           bottom_color=self.end_color)
        elif self.mode == "radial":
            grad_tex = GLGradient.radial(size=(w, h),
                                         border_color=self.start_color,
                                         center_color=self.end_color)
        else:  # default diagonal
            grad_tex = GLGradient.diagonal(size=(w, h),
                                           start_color=self.start_color,
                                           end_color=self.end_color)

        grad_pixels = np.frombuffer(
            grad_tex.pixels, dtype=np.uint8).reshape(h, w, 4).copy()
        alpha_mask = np.frombuffer(core.texture.pixels, dtype=np.uint8).reshape(
            h, w, 4)[:, :, 3] / 255.0
        grad_pixels[:, :, 3] = (grad_pixels[:, :, 3] *
                                alpha_mask).astype(np.uint8)

        final_tex = Texture.create(size=(w, h))
        final_tex.blit_buffer(grad_pixels.tobytes(),
                              colorfmt='rgba', bufferfmt='ubyte')
        final_tex.flip_vertical()

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(
                texture=final_tex, size=self.texture_size, pos=self.get_texture_pos())

        self.bind(pos=self._update_rect, size=self._update_rect,
                  halign=self._update_rect, valign=self._update_rect)

    def get_texture_pos(self):
        x, y = self.pos
        if self.halign == "center":
            x += (self.width - self.texture_size[0]) / 2
        elif self.halign == "right":
            x += self.width - self.texture_size[0]

        if self.valign == "middle":
            y += (self.height - self.texture_size[1]) / 2
        elif self.valign == "top":
            y += self.height - self.texture_size[1]
        return x, y

    def _update_rect(self, *args):
        if hasattr(self, "rect"):
            self.rect.pos = self.get_texture_pos()
            self.rect.size = self.texture_size


Kv = '''
#:import GLGradient gradient4kivy.gradient.GLGradient
BoxLayout:
    orientation: "vertical"
    padding: "10dp"
    spacing: "10dp"
    canvas.before:
        Color:
            rgba:(1,1,1,1)
        RoundedRectangle:
            pos:self.pos
            size:self.size
            radius:[dp(20),]
            texture:GLGradient.radial()


    GradientLabel:
        text: "Diagonal Gradient"
        font_size: sp(50)
        mode: "diagonal"
        start_color: 1, 0, 0, 1   # red
        end_color: 1, 1, 0, 1     # yellow
        halign: "center"
        valign: "middle"
        size_hint: 1, 1

    GradientLabel:
        text: "Horizontal Gradient"
        font_size: sp(50)
        mode: "horizontal"
        start_color: 0, 1, 0, 1   # green
        end_color: 0, 0, 1, 1     # blue
        halign: "center"
        valign: "middle"
        size_hint: 1, 1

    GradientLabel:
        text: "Vertical Gradient"
        font_size: sp(50)
        mode: "vertical"
        start_color: 1, 0, 1, 1   # magenta
        end_color: 0, 1, 1, 1     # cyan
        halign: "center"
        valign: "middle"
        size_hint: 1, 1

    GradientLabel:
        text: "Radial Gradient"
        font_size: sp(50)
        mode: "radial"
        start_color: 1, 0.5, 0, 1   # orange
        end_color: 0.2, 0.2, 0.8, 1 # bluish
        halign: "center"
        valign: "middle"
        size_hint: 1, 1


'''
# Example usage


class TestApp(App):
    def build(self):
        '''
        layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))

        labels = [
            {"text": "Diagonal Gradient", "mode": "diagonal",
             "start_color": [1, 0, 0, 1], "end_color": [1, 1, 0, 1]},  # red → yellow
            {"text": "Horizontal Gradient", "mode": "horizontal",
             "start_color": [0, 1, 0, 1], "end_color": [0, 0, 1, 1]},  # green → blue
            {"text": "Vertical Gradient", "mode": "vertical",
             "start_color": [1, 0, 1, 1], "end_color": [0, 1, 1, 1]},  # magenta → cyan
            {"text": "Radial Gradient", "mode": "radial",
             "start_color": [1, 0.5, 0, 1], "end_color": [0.0, 0.2, 0.8, 0.5]},  # orange → bluish
        ]

        for lbl in labels:
            label = GradientLabel(text=lbl["text"], font_size=sp(50),
                                  size_hint=(1,1),
                                  mode=lbl["mode"],
                                  start_color=lbl["start_color"],
                                  end_color=lbl["end_color"])
            label.halign = "center"
            label.valign = "middle"
            layout.add_widget(label)
        '''

        return Builder.load_string(Kv)


if __name__ == "__main__":
    TestApp().run()
