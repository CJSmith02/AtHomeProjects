#!/usr/bin/env python3 -tt
import random
import utils
import os
import requests
import pickle

"""Import more modules you might need here!"""

"""Constants, for your reference! (Don't overwrite them; they're
used in visualization.py)"""
MAZE_WIDTH = 40
MAZE_HEIGHT = 40
OUTPUT_FILENAME = 'unicorndata.pickle'

def get_url_data(x, y, url):
    """Queries the url, parses the data, and returns
    that information in a dict object.

    Arguments:
    x -- (only for visualization purposes) The x coordinate
    associated to the cell in the maze that you're currently
    standing at.
    y -- (only for visualization purposes) The y coordinate
    associated to the cell in the maze that you're currently
    standing at.
    url -- The url to query.
    """
    pass

def search_maze():
    """Exhaustively searches the maze (using your preferred
    searching algorithm) and returns a list of dicts with
    information about your distance from the unicorn"""
    pass

def save_data(data, filename):
    """Saves data into the file specified by filename
    using pickle.

    Arguments:
    data -- The data to store.
    filename -- The name of the file in which to store
    the data.
    """
    pass

def main():
    unicorn_data = search_maze()

    """This might seem like a strange way to delete a file,
    but in Python, using exceptions for flow control is common
    and normal! (Like StopIteration)"""
    try:
        os.remove(OUTPUT_FILENAME)
    except OSError:
        pass

    save_data(unicorn_data, OUTPUT_FILENAME)

if __name__ == '__main__':
    main()
