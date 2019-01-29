"""
CSSE1001 Assignment 3
Semester 2, 2017
"""

# There are a number of jesting comments in the support code
# They should not be taken seriously. Keep it fun folks :D
# Students are welcome to add their own source code humour, provided it remains civil

import random
import tkinter as tk
from tkinter import messagebox

from game import ObjectiveManager
from dot import BasicDot
from util import ImageManager, create_animation, load_image

from a3_support import AdvancedGame, AdvancedGridView
from a3_task1 import InfoPanel, MainMenu
from a3_task2 import CompanionDot, BalloonDot, PenguinCompanion
from a3_task3 import AristotleCompanion, SaveManager, EndlessGame
from a3_task4 import EskimoCompanion, BuffaloCompanion, CaptainCompanion, ActionBar

__author__ = "Vu Anh Le (s4490763)"
__email__ = "s4490763@student.uq.edu.au"
__date__ = "26/10/2017"
__version__ = "1.5.1"

DEFAULT_ANIMATION_DELAY = 0  # (ms)
ANIMATION_DELAYS = {
    # step_name => delay (ms)
    'ACTIVATE_ALL': 50,
    'ACTIVATE': 100,
    'ANIMATION_BEGIN': 300,
    'ANIMATION_DONE': 0,
    'ANIMATION_STEP': 200
}

COMPANION_DOT_RATE = 0.2
BALLOON_DOT_RATE = 0.5


# You may edit as much of DotsApp as you wish
class DotsApp:
    """Top level GUI class for simple Dots & Co game"""

    def __init__(self, master):
        """Constructor

        Parameters:
            master (tk.Tk|tk.Frame): The parent widget
        """
        self._master = master
        self._playing = True
        self._image_manager = ImageManager('images/dots/', loader=load_image)

        # Game
        self._size = (8, 8)
        counts = [20, 15, 20, 25]
        random.shuffle(counts)
        # Randomly pair counts with each kind of dot
        objectives = zip([BasicDot(1), BasicDot(2), BasicDot(8), BasicDot(3)], counts)

        self._objectives = ObjectiveManager(objectives)

        # Define companions
        self._companions = {
            'penguin': PenguinCompanion(max_charge=6),
            'eskimo': EskimoCompanion(max_charge=6, dot_count=4),
            'buffalo': BuffaloCompanion(max_charge=5, dot_count=5),
            'captain': CaptainCompanion(max_charge=5, dot_count=4),
            'aristotle': AristotleCompanion(max_charge=4, dot_count=2)
        }

        # Define dead cell maps
        dead_cells = {
            'endless': {},
            'companion': {(2, 1), (2, 2),
                          (3, 1), (3, 2),
                          (5, 4), (5, 5), (5, 6)},
        }

        # Define game types
        self._games = {
            'endless': EndlessGame({BasicDot: 1},
                                   size=self._size,
                                   dead_cells=dead_cells['endless'],
                                   kinds=(1, 2, 3, 4, 8)
                                   ),
            'companion': AdvancedGame({BasicDot: 1, CompanionDot: COMPANION_DOT_RATE},
                                      size=self._size,
                                      dead_cells=dead_cells['companion'],
                                      kinds=(1, 2, 3, 8),
                                      companion=random.choice(list(self._companions.values())),
                                      objectives=self._objectives,
                                      moves=20,
                                      )
        }

        # Choose a initial game to play
        self._game_mode = 'companion'
        self._game = self._games[self._game_mode]

        # Info Panel
        self._info_panel = InfoPanel(master, image_manager=self._image_manager)
        self._info_panel.pack(expand=True, fill=tk.BOTH)
        self._info_panel.set_companion(self._game.companion.get_name())
        self._info_panel.set_interval(self._game.companion.get_max_charge(), self._game.companion.get_charge())

        # Grid View
        self._grid_view = AdvancedGridView(master, size=self._game.grid.size(), image_manager=self._image_manager)
        self._grid_view.pack()
        self.draw_grid()
        self.draw_grid_borders()

        # Action Panel
        self._action_bar = ActionBar(master)
        self._action_bar.pack()

        # Menu & Title
        self._main_menu = MainMenu(master)
        self._master.config(menu=self._main_menu)

        # Events
        self.bind_events()
        for game in self._games.values():
            self.bind_game_events(game)

        # Set initial score again to trigger view update automatically
        self._refresh_status()

        # Set windows position to center
        self._update_title()
        self._move_to_center()

    def change_companion(self, companion_name=None):
        """Change the companion of the current game

        Parameters:
            companion_name (str): The name of the companion to switch
        """
        if companion_name:
            self._game.companion = self._companions[companion_name]
        self._info_panel.set_companion(self._game.companion.get_name())

    def change_game(self, game_mode, companion_name):
        """Switch to another game mode with specific companion

        Parameters:
            game_mode (str): The mode of the game that defined
            companion_name (str): The name of the companion to switch
        """
        self._game_mode = game_mode
        self._game = self._games[self._game_mode]
        self.change_companion(companion_name)
        self._grid_view.reset()
        self._info_panel.show_moves()
        self.draw_grid_borders()
        self.draw_grid()
        self._update_title()
        self.reset()

        if self._game_mode == 'endless':
            # Remove action bar and hide move in endless mode
            self._action_bar.disable_all_buttons()
            self._info_panel.hide_moves()

    def companion_clicked(self):
        self._action_bar.disable_button('companion')
        self.activate_companion()

    def activate_companion(self):
        """Activate the companion"""
        steps = self._game.companion.activate(self._game)
        self.animate(steps)

    def erase_clicked(self):
        """Switch to erase mode"""
        # Disable the eraser button
        self._action_bar.disable_button('eraser')
        self._grid_view.bind_erase_mode()

    def erase_dot(self, position):
        """Erase the selected dot"""
        if position:
            cell = self._game.grid[position]
            if cell.get_dot():
                steps = self._game.activate_all([position])
                self.animate(steps)
                self._grid_view.bind_normal_mode()

    def save_game(self):
        """Save the current game"""
        if self._playing:
            disabled_buttons = self._action_bar.get_disabled_buttons()
            balloons_enabled = self._main_menu.is_balloons_enabled()
            SaveManager.save(self._game, self._game_mode, balloons_enabled, disabled_buttons)
        else:
            messagebox.showerror("Error", "Unable to save the game!\n\nThe game is already over.")

    def load_game(self):
        """Load the previous game from file"""
        data = SaveManager.load()
        if not data:
            return

        self.change_game(data['game_mode'], data['companion'])
        self._game.set_score(int(data['score']))
        self._game.set_moves(int(data['moves']))

        # Restore the companion's charge
        for i in range(int(data['companion_charge'])):
            self._game.companion.charge()

        # Load set the previous objectives
        self._game.objectives = SaveManager.generate_objectives(data['objectives'])

        # Replace all the dots on grid
        SaveManager.set_dots(self._game.grid, data['grid'])

        # Restore balloons mode and actions status
        self._main_menu.set_balloons_mode(bool(data['balloons_enabled']))
        for button_name in data['disabled_buttons']:
            self._action_bar.disable_button(button_name)

        self.draw_grid()
        self._refresh_status()

    def generate_balloons(self):
        """Places some balloons to the last row of grid"""
        if random.random() < BALLOON_DOT_RATE:
            last_row_cells = self._game.get_last_row()
            self._game.place_random_dots(BalloonDot, cells=last_row_cells, dot_count=1)
        self.draw_grid()

    def move_balloons_up(self):
        """Find all the balloons on grid and move them up"""
        for position, cell in self._game.get_dots_by_name('balloon').items():
            cell.get_dot().move_up(position, self._game)
        self.draw_grid()

    def _update_title(self):
        """Update the title of the app"""
        self._master.title(f'{self._game_mode.upper()} GAME - {self._game.companion.get_name().upper()}')

    def _move_to_center(self):
        """Move the app to the center of the screen"""
        self._master.update_idletasks()
        screen_width = self._master.winfo_screenwidth()
        screen_height = self._master.winfo_screenheight()
        size = self._master.geometry().split('+')[0]
        self._width, self._height = tuple(int(s) for s in size.split('x'))
        x = screen_width / 2 - self._width / 2
        y = screen_height / 2 - self._height / 2
        self._master.geometry("%dx%d+%d+%d" % (self._width, self._height, x, y))
        self._master.resizable(False, False)
        self._master.minsize(self._width, self._height)

    def bind_game_events(self, game):
        """Binds the events to specific game"""
        game.on('reset', self._refresh_status)
        game.on('complete', self._drop_complete)
        game.on('connect', self._connect)
        game.on('undo', self._undo)

    def bind_events(self):
        """Binds relevant events"""
        self._grid_view.on('start_connection', self._drag)
        self._grid_view.on('move_connection', self._drag)
        self._grid_view.on('end_connection', self._drop)
        self._grid_view.on('erase_dot', self.erase_dot)

        self._main_menu.on('change_game', self.change_game)
        self._main_menu.on('reset_game', self.reset)
        self._main_menu.on('save_game', self.save_game)
        self._main_menu.on('load_game', self.load_game)

        self._action_bar.on('companion_clicked', self.companion_clicked)
        self._action_bar.on('eraser_clicked', self.erase_clicked)

    def _animation_step(self, step_name):
        """Runs for each step of an animation

        Parameters:
            step_name (str): The name (type) of the step
        """
        # print(step_name)
        self._refresh_status()
        self.draw_grid()

    def animate(self, steps, callback=lambda: None):
        """Animates some steps (i.e. from selecting some dots, activating companion, etc.

        Parameters:
            steps (generator): Generator which yields step_name (str) for each step in the animation
        """

        if steps is None:
            steps = (None for _ in range(1))

        animation = create_animation(self._master, steps,
                                     delays=ANIMATION_DELAYS, delay=DEFAULT_ANIMATION_DELAY,
                                     step=self._animation_step, callback=callback)
        animation()

    def _drop(self, position):  # pylint: disable=unused-argument
        """Handles the dropping of the dragged connection

        Parameters:
            position (tuple<int, int>): The position where the connection was
                                        dropped
        """
        if not self._playing:
            return

        if self._game.is_resolving():
            return

        self._grid_view.clear_dragged_connections()
        self._grid_view.clear_connections()

        self.animate(self._game.drop())

    def _connect(self, start, end):
        """Draws a connection from the start point to the end point

        Parameters:
            start (tuple<int, int>): The position of the starting dot
            end (tuple<int, int>): The position of the ending dot
        """

        if self._game.is_resolving():
            return
        if not self._playing:
            return
        self._grid_view.draw_connection(start, end,
                                        self._game.grid[start].get_dot().get_kind())

    def _undo(self, positions):
        """Removes all the given dot connections from the grid view

        Parameters:
            positions (list<tuple<int, int>>): The dot connects to remove
        """
        for _ in positions:
            self._grid_view.undo_connection()

    def _drag(self, position):
        """Attempts to connect to the given position, otherwise draws a dragged
        line from the start

        Parameters:
            position (tuple<int, int>): The position to drag to
        """
        if self._game.is_resolving():
            return
        if not self._playing:
            return

        tile_position = self._grid_view.xy_to_rc(position)

        if tile_position is not None:
            cell = self._game.grid[tile_position]
            dot = cell.get_dot()

            if dot and self._game.connect(tile_position):
                self._grid_view.clear_dragged_connections()
                return

        kind = self._game.get_connection_kind()

        if not len(self._game.get_connection_path()):
            return

        start = self._game.get_connection_path()[-1]

        if start:
            self._grid_view.draw_dragged_connection(start, position, kind)

    @staticmethod
    def remove(*_):
        """Deprecated in 1.1.0"""
        raise DeprecationWarning("Deprecated in 1.1.0")

    def draw_grid(self):
        """Draws the grid"""
        self._grid_view.draw(self._game.grid)

    def draw_grid_borders(self):
        """Draws borders around the game grid"""
        borders = list(self._game.grid.get_borders())

        # this is a hack that won't work well for multiple separate clusters
        outside = max(borders, key=lambda border: len(set(border)))

        for border in borders:
            self._grid_view.draw_border(border, fill=border != outside)

    def reset(self):
        """Resets the game"""
        self._playing = True
        self._game.reset()
        self._game.objectives.reset()
        self._action_bar.enable_all_buttons()
        self._refresh_status()
        self.draw_grid()

    def check_game_over(self):
        """Checks whether the game is over and shows an appropriate message box if so"""
        state = self._game.get_game_state()
        if state == self._game.GameState.WON:
            self._playing = False
            message = f"You won!\nYou connected {self._game.get_score()} points. \
                        \n\nDo you want to play a new game?"

        elif state == self._game.GameState.LOST:
            self._playing = False
            message = f"You didn't reach the objective!\nYou connected {self._game.get_score()} points. \
                        \n\nDo you want to play a new game?"

        if not self._playing:
            self._action_bar.disable_all_buttons()
            if messagebox.askyesno("Game Over!", message):
                self.reset()

    def _drop_complete(self):
        """Handles the end of a drop animation"""

        self.move_balloons_up()
        if self._main_menu.is_balloons_enabled():
            self.generate_balloons()

        if self._game.companion.get_max_charge() and self._game.companion.is_fully_charged():
            self.activate_companion()
            self._game.companion.reset()
            self._refresh_status()

        self.check_game_over()

    def _refresh_status(self):
        """Handles change in score"""
        # Normally, this should raise the following error:
        # raise NotImplementedError()
        # But so that the game can work prior to this method being implemented,
        # we'll just print some information
        # Sometimes I believe Python ignores all my comments :(

        self._info_panel.set_score(self._game.get_score())
        self._info_panel.set_moves(self._game.get_moves())
        self._info_panel.set_objectives(self._game.objectives.get_status())
        self._info_panel.set_interval(self._game.companion.get_max_charge(), self._game.companion.get_charge())


def main():
    """Sets-up the GUI for Dots & Co"""
    # Write your GUI instantiation code here
    root = tk.Tk()
    app = DotsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
