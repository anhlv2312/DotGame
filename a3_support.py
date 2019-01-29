"""
CSSE1001 Assignment 3 - Support
Semester 2, 2017
"""

import random
import tkinter as tk

from game import DotGrid, DotGame, ObjectiveManager
from dot import AbstractKindlessDot
from view import GridView
from factory import CellFactory
from companion import AbstractCompanion

__author__ = "Vu Anh Le (s4490763)"
__email__ = "s4490763@student.uq.edu.au"
__date__ = "26/10/2017"
__version__ = "1.5.1"


# -------------------------------------------------------------------------
# Abstract Special Companion Class
# -------------------------------------------------------------------------
class SpecialCompanion(AbstractCompanion):
    """A special companion that has special ability like Superman"""
    NAME = 'special'

    def __init__(self, dot_type, max_charge=6, dot_count=4):
        """Constructor

        Parameters:
            dot_type (type): The class of the Special Dot that the Companion can place on grid
            max_charge (int): The amount of charge required to activate the companion
            dot_count (int): The rate that special dots that the companion can add to the grid
        """
        super().__init__(max_charge)
        self._dot_type = dot_type
        self._dot_count = dot_count

    def activate(self, game):
        game.place_random_dots(self._dot_type, dot_count=self._dot_count)


# -------------------------------------------------------------------------
# Advance Grid View Class
# -------------------------------------------------------------------------
class AdvancedGridView(GridView):
    def reset(self):
        """Delete all the dots' image and empty the dots dictionary"""
        self.delete(tk.ALL)
        self._dots = {}

    def bind_normal_mode(self):
        """Bind mouse button to connect dots on grid"""
        self.bind("<Button-1>", self._start_connection)
        self.bind("<B1-Motion>", self._move_connection)
        self.bind("<ButtonRelease-1>", self._end_connection)

    def bind_erase_mode(self, ):
        """Bind mouse button to erase dot on grid"""
        self.bind("<Button-1>", self.erase_dot)
        self.bind("<B1-Motion>", None)
        self.bind("<ButtonRelease-1>", None)

    def erase_dot(self, event):
        position = self.xy_to_rc((event.x, event.y))
        self.emit('erase_dot', position)


# -------------------------------------------------------------------------
# Dot Grid Inheritance
# -------------------------------------------------------------------------
class AdvancedDotGrid(DotGrid):
    def serialize(self):
        """(dict) Serialize the dot grid into a dictionary"""
        grid = []
        for row in self.get_rows():
            cells = []
            for cell in row:
                if cell.get_dot():
                    dot = (cell.get_dot().get_name(), cell.get_dot().get_kind())
                else:
                    dot = (None, None)
                cells.append(dot)
            grid.append(cells)
        return grid


# -------------------------------------------------------------------------
# Advanced Game Class
# -------------------------------------------------------------------------
class AdvancedGame(DotGame):
    def __init__(self, dot_weights, companion: AbstractCompanion, kinds=(1, 2, 3), size=(6, 6), dead_cells=None,
                 objectives: ObjectiveManager = None, min_group=2, moves=20, animation=True):

        self.companion = companion
        super().__init__(dot_weights, kinds=kinds, size=size, dead_cells=dead_cells, objectives=objectives,
                         min_group=min_group, moves=moves, animation=animation)

        self.grid = AdvancedDotGrid(size, self.dot_factory, animation=animation, cell_factory=CellFactory(dead_cells))
        self.reset()

    def reset(self):
        """Resets the game"""
        self.companion.reset()
        super().reset()

    def get_last_row(self):
        """(list<Cell>) Get the cells of the last row of dot grid"""
        rows, columns = self.grid.size()
        cells = []
        for i in range(columns):
            cells.append(self.grid[rows - 1, i])
        return cells

    def place_random_dots(self, dot_type, kind=None, cells=None, dot_count=5, replace_dots=('basic', 'companion')):
        """Place a random dot on dot grid

        Parameters:
            dot_type (type): The type of the dot to be create
            kind (int): The kind of the dot (if None, the current dot kind will be used)
            cells (list<Cell>): The list of the cells will be placed a dot on (if None, choose all the grid)
            dot_count (int): The number of dots to be placed
            replace_dots (list<str>): The list of dot name to be replaced
        """
        if not cells:
            cells = list(self.grid.values())

        random.shuffle(cells)

        count = 0
        while count < dot_count:
            cell = cells.pop()

            if not cell.get_dot():
                continue

            if cell.get_dot().get_name() in replace_dots:
                # Check if the dot type is kind less dot
                if issubclass(dot_type, AbstractKindlessDot):
                    cell.set_dot(dot_type())
                else:
                    kind = cell.get_dot().get_kind() if kind is None else kind
                    cell.set_dot(dot_type(kind))
                count += 1

    def get_dots_by_name(self, name):
        """Find all the dot with name on the grid

        Parameters:
            name (str): The name of the dots to be found
        """
        result = {}
        for position, cell in self.grid.items():
            if cell.get_dot():
                if cell.get_dot().get_name() == name:
                    result[position] = cell
        return result

    def serialize_objectives(self):
        """(dict) Serialize the objectives into a dictionary"""
        objectives = []
        for dot, count in self.objectives.get_status():
            objective = dot.get_name(), dot.get_kind(), count
            objectives.append(objective)
        return objectives

    def serialize(self):
        """(dict) Serialize the game into a dictionary"""
        return {
            'companion': self.companion.get_name(),
            'companion_charge': self.companion.get_charge(),
            'score': self.get_score(),
            'moves': self.get_moves(),
            'objectives': self.serialize_objectives(),
            'grid': self.grid.serialize()
        }

    def set_score(self, score):
        """Set the score of the current game

        Parameters:
            score (int): The new score
        """
        self._score = score

