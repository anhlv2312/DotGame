"""
CSSE1001 Assignment 3 - Task 2
Semester 2, 2017
"""

import random

from dot import BasicDot, AbstractKindlessDot
from companion import AbstractCompanion

__author__ = "Vu Anh Le (s4490763)"
__email__ = "s4490763@student.uq.edu.au"
__date__ = "26/10/2017"
__version__ = "1.5.1"


# -------------------------------------------------------------------------
# Companion Dot Class
# -------------------------------------------------------------------------
class CompanionDot(BasicDot):
    """A bottle of mana, which helps companion to charge its super power"""
    DOT_NAME = 'companion'

    def activate(self, position, game, activated, has_loop=False):
        self._expired = True
        game.companion.charge()


# -------------------------------------------------------------------------
# Balloon Dot Class
# -------------------------------------------------------------------------
class BalloonDot(AbstractKindlessDot):
    """The dot that has nothing to do, just fly away"""
    DOT_NAME = 'balloon'

    def get_view_id(self):
        """(str) Returns a string to identify the image for this dot"""
        return "{}/{}".format(self.get_name(), self.get_name())

    def activate(self, position, game, activated, has_loop=False):
        self._expired = True

    def after_resolved(self, position, game):
        row, column = position
        if row == 0:
            return [position]

    def adjacent_activated(self, position, game, activated, activated_neighbours, has_loop=False):
        pass

    def can_connect(self):
        return False

    def move_up(self, position, game):
        """Move the balloon up until it can swap with upper dot

        Parameters:
            position (tuple<int, int>): The current position of the dot
            game (AdvanceGame): The game currently being played
        """
        row, column = position
        while row > 0:
            row += -1
            if self._swap(game.grid[position], game.grid[row, column]):
                break

    @staticmethod
    def _swap(source_cell, target_cell):
        """Swap two dot from source cell to target cell

        Parameters:
            source_cell (Cell): The source cell
            target_cell (Cell): The target cell
        """
        if target_cell.get_dot():
            temp_dot = source_cell.get_dot()
            source_cell.set_dot(target_cell.get_dot())
            target_cell.set_dot(temp_dot)
            return True


# -------------------------------------------------------------------------
# Penguin Companion Class
# -------------------------------------------------------------------------
class PenguinCompanion(AbstractCompanion):
    """This little creature will eat all the dots which are in its favourite color"""
    NAME = 'penguin'

    def activate(self, game):
        chosen_kind = random.choice(game.objectives.get_status())[0].get_kind()

        for position, cell in game.grid.items():
            if cell.get_dot():
                if cell.get_dot().get_kind() == chosen_kind:
                    cell.set_dot(None)
        for _ in game.grid.replace_blanks():
            yield "ANIMATION_STEP"


