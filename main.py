import random
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.audio import SoundLoader
from kivy.utils import get_color_from_hex
from kivy.properties import NumericProperty

__version__ = "0.6"

WIN_STATEGY = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # по горизонтали
    (0, 3, 6), (4, 1, 7), (2, 5, 8),  # по вертикали
    (0, 4, 8), (2, 4, 6)  # по диагонали
)


# Цвет ноликов
def color_zero():
    return get_color_from_hex('#930200')


# Цвет крестиков
def color_crosses():
    return get_color_from_hex('#032F7A')


class Cell(Button):
    value = NumericProperty(0)


class GameMenu(RelativeLayout):
    pass


class GameEnd(RelativeLayout):

    def __init__(self, text, **kwargs):
        super(GameEnd, self).__init__(**kwargs)
        self.ids.winner.text = text


class GameRoot(RelativeLayout):
    sound = SoundLoader.load('music/NFF-confirm-02.wav')

    def end_game(self, player=0):
        self.clear_widgets()
        if player == 1:
            text = 'Победили крестик!'
        elif player == -1:
            text = 'Победили нолики!'
        else:
            text = 'Ничья!'
        self.add_widget(GameEnd(text=text))

    def show_game_menu(self):
        # создает меню
        self.clear_widgets()
        self.sound.play()
        self.add_widget(GameMenu())

    def show_game_field(self, computer):
        # создает игровое поле
        self.clear_widgets()
        self.sound.play()
        self.add_widget(GameField(computer))


class Computer:

    def __init__(self, side):
        self.side = side

    def choice(self, cells):
        self.cells = cells
        ok, cell = self.check(self.side)
        if ok:
            return cell
        ok, cell = self.check(-self.side)
        if ok:
            return cell
        if self.cells[4].value == 0:
            return 4
        strategy = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        random.shuffle(strategy)
        return self.free(strategy)

    def check(self, side):
        for strategy in WIN_STATEGY:
            result = sum([self.cells[s].value for s in strategy])
            if result == 2 * side:
                return True, self.free(strategy)

        return False, 0

    def free(self, strategy):
        for s in strategy:
            if self.cells[s].value == 0:
                return s


class GameField(GridLayout):
    stroke_number = 0
    sound = SoundLoader.load('music/NFF-menu-a.wav')

    def __init__(self, computer, **kwargs):
        super(GameField, self).__init__(**kwargs)
        for row in range(3):
            for col in range(3):
                btn = Cell()
                btn.bind(on_press=self.button_click)
                self.add_widget(btn)

        self.computer = computer
        if self.computer:
            random.seed()
            self.stroke = random.choice((-1, 1))
            self.comp = Computer(self.stroke)
            self.stroke_comp()

    def button_click(self, button):
        if button.text == '':
            if self.stroke_number % 2 == 0:
                button.value = 1
                button.text = 'X'
                button.background_color = color_crosses()
            else:
                button.value = -1
                button.text = 'O'
                button.background_color = color_zero()
            self.stroke_number += 1
            self.check()
        self.sound.play()

    def check(self):
        for stategy in WIN_STATEGY:
            result = sum([self.children[s].value for s in stategy])
            if result == 3:
                return self.parent.end_game(1)
            elif result == -3:
                return self.parent.end_game(-1)

        if self.stroke_number == 9:
            return self.parent.end_game()

        if self.computer:
            self.stroke_comp()

    def stroke_comp(self):
        if (self.stroke == 1 and self.stroke_number % 2 == 0) or \
                (self.stroke == -1 and self.stroke_number % 2 == 1):
            choice = self.comp.choice(self.children)
            self.button_click(self.children[choice])


class TicTacToeApp(App):

    def build(self):
        with open("main.kv", encoding='utf8') as f:
            root = Builder.load_string(f.read())

        return root


if __name__ == "__main__":
    TicTacToeApp().run()
