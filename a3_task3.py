"""
CSSE1001 Assignment 3 - Task 3
Semester 2, 2017
"""

import json
from tkinter import messagebox

from game import ObjectiveManager
from dot import AbstractKindlessDot, BasicDot, WildcardDot
from companion import UselessCompanion

from modules.matrix import RADIAL_DELTAS

from a3_support import SpecialCompanion, AdvancedGame
from a3_task2 import CompanionDot, BalloonDot
from a3_task4 import BeamDot, SwirlDot

__author__ = "Vu Anh Le (s4490763)"
__email__ = "s4490763@student.uq.edu.au"
__date__ = "26/10/2017"
__version__ = "1.5.1"


# -------------------------------------------------------------------------
# Butterfly Dot Class
# -------------------------------------------------------------------------
class ButterflyDot(BasicDot):
    """The most beautiful dot in this game, it will make nearby dots fall in love with it"""
    DOT_NAME = 'butterfly'

    def __init__(self, kind):
        super().__init__(kind=kind)
        self._states = ['coocoon', 'butterfly-0', 'butterfly-2']

    def get_view_id(self):
        """(str) Returns a string to identify the image for this dot"""
        return "{}/{}".format(self.get_name(), self._states[self._kind])

    def activate(self, position, game, activated, has_loop=False):
        self._expired = True
        positions = [position]
        # Find all the position of adjacent cell
        adjacent_positions = game.grid.get_adjacent_cells(position, deltas=RADIAL_DELTAS)

        # Add the adjacent positions to the list
        for adjacent_position in adjacent_positions:
            if game.grid[adjacent_position].get_dot():
                positions.append(adjacent_position)

        # Return the positions to activate
        return positions

    def adjacent_activated(self, position, game, activated, activated_neighbours, has_loop=False):
        if self._kind == len(self._states) - 1:
            positions = self.activate(position, game, None)
            return positions
        else:
            self._kind += 1

    def can_connect(self):
        return False


# -------------------------------------------------------------------------
# Aristotle Companion Class
# -------------------------------------------------------------------------
class AristotleCompanion(SpecialCompanion):
    """Captain America doesn't have a laser gun, but he could give you some Beam Dots"""
    NAME = 'aristotle'

    def __init__(self, max_charge=6, dot_count=4):
        super().__init__(ButterflyDot, max_charge, dot_count=dot_count)

    def activate(self, game):
        game.place_random_dots(self._dot_type, kind=0, dot_count=self._dot_count)


# -------------------------------------------------------------------------
# Endless Game Inheritance
# -------------------------------------------------------------------------
class EndlessGame(AdvancedGame):
    def __init__(self, dot_weights, kinds=(1, 2, 3), size=(6, 6), dead_cells=None, min_group=2, animation=True):

        self.companion = UselessCompanion(max_charge=0)

        super().__init__(dot_weights, companion=self.companion, kinds=kinds, size=size, dead_cells=dead_cells,
                         min_group=min_group, moves=0, animation=animation)

        self.objectives = ObjectiveManager(())

    def get_game_state(self):
        return self.GameState.PLAYING


# -------------------------------------------------------------------------
# Save Manager Class
# -------------------------------------------------------------------------
class SaveManager:
    FILENAME = 'save.json'

    @classmethod
    def save(cls, game, game_mode, balloons_enabled, disabled_buttons):
        """Save the current game to file

        Parameters:
            game (AdvancedGame): The game to be save
            game_mode (str): The current game mode
            balloons_enabled (bool): The balloons mode status
            disabled_buttons (list<str>): The list of actions have been used
        """
        data = game.serialize()
        data['game_mode'] = game_mode
        data['balloons_enabled'] = balloons_enabled
        data['disabled_buttons'] = disabled_buttons
        try:
            with open(cls.FILENAME, 'w') as file:
                file.writelines(json.dumps(data, indent=4))
            messagebox.showinfo("Save Game", "Your game has been saved!")
        except Exception as exception:
            messagebox.showerror("Error", "Unable to save the game!\n\n" + str(exception))

    @classmethod
    def load(cls):
        """(dict) Load previous game data from file"""
        try:
            with open(cls.FILENAME, 'r') as file:
                data = json.loads(file.read())
            return data
        except Exception as exception:
            messagebox.showerror("Error", "Unable to load the game!\n\n" + str(exception))

    @classmethod
    def generate_objectives(cls, data):
        """(ObjectiveManager) Create the new objectives from data

        Parameters:
            data (list<list>): The list of objective dot, kind and count
        """
        objectives = []
        for name, kind, count in data:
            objective = (cls.generate_dot(name, kind), count)
            objectives.append(objective)
        return ObjectiveManager(objectives)

    @classmethod
    def set_dots(cls, grid, data):
        """Load previous game data from file

        Parameters:
            grid (AdvancedDotGrid): The gird to be save
            data (list<list>): The list of dot name and kind
        """
        for x, row in enumerate(grid.get_rows()):
            for y, cell in enumerate(row):
                if cell.get_dot():
                    name, kind = data[x][y]
                    cell.set_dot(cls.generate_dot(name, kind))

    @staticmethod
    def generate_dot(name, kind):
        """(AbstractDot) Load previous game data from file

        Parameters:
            name (str): The name of the dot to be create
            kind (str): The kind of the dot
        """
        dot = None
        if name == 'basic':
            dot = BasicDot(kind)
        elif name == 'companion':
            dot = CompanionDot(kind)
        elif name == 'wildcard':
            dot = WildcardDot()
        elif name == 'balloon':
            dot = BalloonDot()
        elif name == 'butterfly':
            dot = ButterflyDot()
        elif name == 'swirl':
            dot = SwirlDot(kind)
        elif name == 'beam':
            dot = BeamDot(kind)
        return dot



