"""
CSSE1001 Assignment 3 - Task 4
Semester 2, 2017
"""

import random
import tkinter as tk

from dot import BasicDot, WildcardDot

from modules.matrix import RADIAL_DELTAS
from modules.ee import EventEmitter

from a3_support import SpecialCompanion

__author__ = "Vu Anh Le (s4490763)"
__email__ = "s4490763@student.uq.edu.au"
__date__ = "26/10/2017"
__version__ = "1.5.1"


# -------------------------------------------------------------------------
# Action Bar Class
# -------------------------------------------------------------------------
class ActionBar(EventEmitter, tk.Frame):
    """The action bar allows the user access to special actions"""
    def __init__(self, master):
        EventEmitter.__init__(self)
        tk.Frame.__init__(self, master)
        self._buttons = {
            'companion': tk.Button(self, text="Companion", command=lambda: self.emit('companion_clicked')),
            'eraser': tk.Button(self, text="Eraser", command=lambda: self.emit('eraser_clicked'))
        }

        for button in self._buttons.values():
            button.pack(side=tk.LEFT, ipadx=10, ipady=5, padx=(0, 10), pady=(0, 10))

    def disable_button(self, button):
        """Save the current game to file

        Parameters:
            button (str): the name of the button to be disabled
        """
        self._buttons[button].configure(state="disabled")

    def get_disabled_buttons(self):
        """(list<str>) Return the list of disabled buttons"""
        return [key for key, value in self._buttons.items() if value.cget('state') == 'disabled']

    def disable_all_buttons(self):
        """Hide all the action buttons"""
        for button in self._buttons.values():
            button.configure(state="disabled")

    def enable_all_buttons(self):
        """Enable all the buttons"""
        for button in self._buttons.values():
            button.configure(state="active")


# -------------------------------------------------------------------------
# Swirl Dot Class
# -------------------------------------------------------------------------
class SwirlDot(BasicDot):
    """It wants to change the whole world to its kind."""
    DOT_NAME = 'swirl'

    def activate(self, position, game, activated, has_loop=False):
        self._expired = True

        # Find all the position of adjacent cell
        adjacent_positions = game.grid.get_adjacent_cells(position, deltas=RADIAL_DELTAS)

        for adjacent_position in adjacent_positions:
            # If the dot has kind, change its to the same kind of swirl dot
            adjacent_dot = game.grid[adjacent_position].get_dot()
            if adjacent_dot:
                if adjacent_dot.get_kind():
                    adjacent_dot.set_kind(self.get_kind())


# -------------------------------------------------------------------------
# Beam Dot Class
# -------------------------------------------------------------------------
class BeamDot(BasicDot):
    """It has laser gun, which can shots all the dot at the same horizontal and/or vertical axis"""
    DOT_NAME = 'beam'

    def __init__(self, kind):
        super().__init__(kind)
        orientations = ['x', 'y', 'xy']
        self._orientation = random.choice(orientations)

    def activate(self, position, game, activated, has_loop=False):
        self._expired = True
        row, col = position
        positions = []
        rows, cols = game.grid.size()

        # Check if the orientation contains x axis then add all position of the same row
        if 'x' in self._orientation:
            for i in range(cols):
                positions.append((row, i))

        # Check if the orientation contains y axis then add all position of the same column
        if 'y' in self._orientation:
            for j in range(rows):
                positions.append((j, col))

        # Activate all the dot in position list
        for position in positions:
            if game.grid[position].get_dot():
                dot = game.grid[position].get_dot()
                if not dot.will_be_removed():
                    dot.activate(position, game, None)

        return positions

    def get_view_id(self):
        """(str) Returns a string to identify the image for this dot"""
        return "{}/{}/{}".format(self.get_name(), self._orientation, self.get_kind())


# -------------------------------------------------------------------------
# Eskimo Companion Class
# -------------------------------------------------------------------------
class EskimoCompanion(SpecialCompanion):
    """He's from the North and he knows nothing, and he would give you some Swirl Dots"""
    NAME = 'eskimo'

    def __init__(self, max_charge=6, dot_count=4):
        super().__init__(SwirlDot, max_charge, dot_count=dot_count)


# -------------------------------------------------------------------------
# Buffalo Companion Class
# -------------------------------------------------------------------------
class BuffaloCompanion(SpecialCompanion):
    """Definitely not a cow! When it becomes crazy it will make some Wildcard Dots"""
    NAME = 'buffalo'

    def __init__(self, max_charge=6, dot_count=4):
        super().__init__(WildcardDot, max_charge, dot_count=dot_count)


# -------------------------------------------------------------------------
# Captain Companion Class
# -------------------------------------------------------------------------
class CaptainCompanion(SpecialCompanion):
    """Captain America doesn't have a laser gun, but he could give you some Beam Dots"""
    NAME = 'captain'

    def __init__(self, max_charge=6, dot_count=4):
        super().__init__(BeamDot, max_charge, dot_count=dot_count)




