#!/usr/bin/env python3 -tt
"""This file contains some helpful utility functions
that you might be able to use throughout the assignment.
"""

def direction_conversion(direction, x, y):
    """Moves in a specified direction from (x, y)
    and returns the coordinates of the new cell"""
    
    conversion = {
        'north': (x-1, y),
        'east': (x, y+1),
        'south': (x+1, y),
        'west': (x, y-1),
    }

    return conversion[direction]