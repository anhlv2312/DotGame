"""
CSSE1001 Assignment 3 - Task 1
Semester 2, 2017
"""

import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image

from view import ObjectivesView
from util import ImageManager
from modules.colours import VIBRANT_COLOURS
from modules.ee import EventEmitter

__author__ = "Vu Anh Le (s4490763)"
__email__ = "s4490763@student.uq.edu.au"
__date__ = "26/10/2017"
__version__ = "1.5.1"


# -------------------------------------------------------------------------
# Info Panel Class
# -------------------------------------------------------------------------
class InfoPanel(tk.Frame):
    """This frame display game's information"""
    def __init__(self, master, image_manager: ImageManager = None):
        super().__init__(master)

        self._image_manager = image_manager

        self._moves_label = tk.Label(self, font=('Helvetica', 30))
        self._score_label = tk.Label(self, font=('Helvetica', 30), fg='gray')
        self._companion_label = tk.Label(self)
        self._objectives_view = ObjectivesView(self, image_manager=self._image_manager)
        self._interval_bar = IntervalBar(self)

        self._moves_label.grid(row=0, column=0, sticky=(tk.N, tk.W), padx=(20, 0), pady=10)
        self._score_label.grid(row=1, column=0, sticky=(tk.S, tk.E), padx=(0, 5), pady=(0, 10))
        self._companion_label.grid(row=0, column=1, rowspan=2, pady=(5, 0))
        self._objectives_view.grid(row=0, column=2, rowspan=2, padx=(10, 5))
        self._interval_bar.grid(row=2, column=0, columnspan=3, pady=(5, 0))

        self.columnconfigure(0, weight=1)

    def set_companion(self, companion_name):
        """Set the companion's image on info panel

        Parameters:
            companion_name (str): The name of the companion
        """
        image = Image.open('images/companions/' + companion_name + '.png').resize((200, 200))
        self._companion_label.image = ImageTk.PhotoImage(image)
        self._companion_label.configure(image=self._companion_label.image)

    def set_score(self, score):
        self._score_label.configure(text=str(score))

    def set_moves(self, moves):
        self._moves_label.configure(text=str(moves))

    def hide_moves(self):
        """Hide the moves on panel"""
        self._moves_label.configure(fg='white')

    def show_moves(self):
        """Show the moves on panel"""
        self._moves_label.configure(fg='black')

    def set_objectives(self, objectives_status):
        """Update the objectives view widget

        Parameters:
            objectives_status (list<dot, count>): The status of the objective
        """
        self._objectives_view.draw(objectives_status)

    def set_interval(self, max_charge, charge):
        """Update the interval bar

        Parameters:
            max_charge (int): The maximum number of charge
            charge (int): The current number of charge
        """
        self._interval_bar.draw(max_charge, charge)


# -------------------------------------------------------------------------
# Main Menu Class
# -------------------------------------------------------------------------
class MainMenu(EventEmitter, tk.Menu):
    """Main menu of DotsApp game"""
    def __init__(self, master):
        EventEmitter.__init__(self)
        tk.Menu.__init__(self, master)
        # Root Menu
        self._master = master
        self._balloons = tk.BooleanVar()
        self._balloons.set(True)
        # File Menu
        self.menu_file = tk.Menu(self)
        self.add_cascade(label="File", menu=self.menu_file)
        self.menu_file.add_command(label="New Game", command=self._reset_game)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Save Game", command=self._save_game)
        self.menu_file.add_command(label="Load Game", command=self._load_game)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Exit", command=self._quit_game)
        # Mode Menu
        self.menu_mode = tk.Menu(self)
        self.add_cascade(label="Mode", menu=self.menu_mode)
        self.menu_mode.add_command(label="Endless", command=lambda: self._change_game('endless'))
        self.menu_companion = tk.Menu(self.menu_mode)
        self.menu_mode.add_cascade(label="Companion", menu=self.menu_companion)
        self.menu_mode.add_separator()
        self.menu_mode.add_checkbutton(label="Balloons", onvalue=True, offvalue=False, variable=self._balloons)
        # Companions
        self.menu_companion.add_command(label="Penguin", command=lambda: self._change_game('companion', 'penguin'))
        self.menu_companion.add_command(label="Aristotle", command=lambda: self._change_game('companion', 'aristotle'))
        self.menu_companion.add_command(label="Eskimo", command=lambda: self._change_game('companion', 'eskimo'))
        self.menu_companion.add_command(label="Buffalo", command=lambda: self._change_game('companion', 'buffalo'))
        self.menu_companion.add_command(label="Captain", command=lambda: self._change_game('companion', 'captain'))

    def _change_game(self, game_mode, companion_name=None):
        if messagebox.askyesno("Switch Mode", "Do you want to switch to {} mode?".format(game_mode)):
            self.emit('change_game', game_mode, companion_name)

    def _reset_game(self):
        if messagebox.askyesno("New Game", "Do you want to start a new game?"):
            self.emit('reset_game')

    def _save_game(self):
        if messagebox.askyesno("Save Game", "Do you want to overwrite previous game?"):
            self.emit('save_game')

    def _load_game(self):
        if messagebox.askyesno("Load Game", "Do you want to load the previous game?"):
            self.emit('load_game')

    def _quit_game(self):
        if messagebox.askyesno("Confirm Exit", "Do you really want to quit?"):
            self._master.quit()

    def is_balloons_enabled(self):
        """Return if the balloons mode enabled"""
        return self._balloons.get()

    def set_balloons_mode(self, enabled=True):
        """Set the balloons mode on the menu"""
        self._balloons.set(enabled)


# -------------------------------------------------------------------------
# Interval Bar Class
# -------------------------------------------------------------------------
class IntervalBar(tk.Canvas):
    """This class display a progress bar with steps"""
    def __init__(self, master, width=45, height=22):
        super().__init__(master, bd=0, highlightthickness=0)
        self._width = width
        self._height = height

    def draw(self, max_charge, charge):
        """Draw the interval bar

        Parameters:
            max_charge (int): The maximum number of charge
            charge (int): The current number of charge
        """
        self.configure(width=self._width * max_charge + 1, height=self._height + 1)
        self.delete(tk.ALL)
        for c in range(max_charge):
            color = VIBRANT_COLOURS['blue'] if c < charge else 'white'
            top_left = (c * self._width, 0)
            bottom_right = (c * self._width + self._width, self._height)
            self.create_rectangle(top_left, bottom_right, fill=color, outline='gray')