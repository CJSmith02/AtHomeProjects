#!/usr/bin/env python3 -tt
"""A module to help students visualize their path through the maze

@parthsarin 11-21-2019 created
"""
import tkinter
from tkinter import messagebox
import time
import exploremaze
import threading
import os

class MazeViz:
    def __init__(self, parent, maze_width, maze_height, scale=20):
        """Initializes the GUI and draws a grid on it.

        Keyword arguments:
        parent -- the parent Tk object
        maze_width -- the width of the maze
        maze_height -- the height of the maze
        scale -- 1 maze unit = `scale` many pixels
        """
        self.parent = parent
        self.parent.title("Maze Exploration Visualization")

        self.maze_width = maze_width
        self.maze_height = maze_height
        self.scale = scale

        # Compute actual width and height
        self.width = maze_width * scale
        self.height = maze_height * scale

        # Store tkinter object
        self.frame = tkinter.Frame(self.parent,
                                   width=self.width,
                                   height=self.height,
                                   highlightthickness=1,
                                   highlightbackground="black")
        self.canvas = tkinter.Canvas(self.frame,
                                     width=self.width, 
                                     height=self.height)
        self.canvas.pack(expand=False)
        self.frame.pack(expand=False)

        # Initialize look of grid
        self.draw_gray_grid()

        self.person = None
        self.draw_person(self.maze_width // 2, self.maze_height // 2)

    def draw_gray_grid(self):
        """Draws a grayed out grid on the canvas."""
        gray = "#D3D3D3"
        # Draw the vertical lines
        for x in range(0, self.width, self.scale):
            self.canvas.create_line(x, 0, x, self.height, fill=gray)

        # Draw the horizontal lines
        for y in range(0, self.height, self.scale):
            self.canvas.create_line(0, y, self.width, y, fill=gray)

    def draw_visited(self, x, y):
        """Highlights (x,y) as light green"""
        # Compute pixel coords
        upper_left = (y * self.scale, x * self.scale)
        lower_right = tuple(i + self.scale for i in upper_left)

        color = '#90ee90'
        self.canvas.create_rectangle(*upper_left, *lower_right, fill=color, outline='')

    def draw_person(self, x, y, color="blue"):
        """Draws a person at the location specified."""
        # Delete the old person
        if self.person is not None:
            self.canvas.delete(self.person)

        # Compute pixel coords
        upper_left = (y * self.scale, x * self.scale)
        lower_right = tuple(i + self.scale for i in upper_left)

        # Add some padding
        upper_left = tuple(i + self.scale / 10 for i in upper_left)
        lower_right = tuple(i - self.scale / 10 for i in lower_right)

        self.person = self.canvas.create_oval(*upper_left, *lower_right,
                                              fill=color)
        self.person_location = (x, y)

    def draw_lines(self, x, y,
                   north=False, south=False, east=False, west=False,
                   color="black"):
        """Draws lines on the canvas around the area where the
        student is currently standing based on the boolean parameters."""
        upper_left = (y * self.scale, x * self.scale)
        upper_right = (upper_left[0] + self.scale, upper_left[1])
        lower_left = (upper_left[0], upper_left[1] + self.scale)
        lower_right = (upper_left[0] + self.scale, upper_left[1] + self.scale)

        if north:
            self.canvas.create_line(*upper_left, *upper_right, fill=color)

        if south:
            self.canvas.create_line(*lower_left, *lower_right, fill=color)

        if east:
            self.canvas.create_line(*upper_right, *lower_right, fill=color)

        if west:
            self.canvas.create_line(*upper_left, *lower_left, fill=color)

    def draw_unicorn_hit(self, x, y, color="yellow"):
        """Draws a unicorn marker at the location specified.
        TODO: decompose this and draw_person
        """
        # Compute pixel coords
        upper_left = (y * self.scale, x * self.scale)
        lower_right = tuple(i + self.scale for i in upper_left)

        # Add some padding
        upper_left = tuple(i + self.scale / 10 for i in upper_left)
        lower_right = tuple(i - self.scale / 10 for i in lower_right)

        self.canvas.create_oval(*upper_left, *lower_right,
                                fill=color)

    def refresh(self):
        """Redraws the canvas. 
        TODO: find a safer way to do this (race cond'n warning)
        """
        self.parent.update()


def overwrite_student(old_fn, app):
    """Overwrites the student's function by updating the
    canvas and sleeping between function calls."""

    def new_fn(x, y, url):
        result = old_fn(x, y, url)

        # Draw the output
        if "neighbors" in result:
            all_directions = {"north", "south", "east", "west"}
            valid_directions = set(result["neighbors"].keys())
            blocked_directions = all_directions - valid_directions

            # Build a dict to use to draw the lines
            draw_kwargs = {d: (d in blocked_directions)
                           for d in all_directions}

            # Signal that x, y was visited
            app.draw_visited(x, y)

            # Draw the lines, move the person and refresh
            app.draw_lines(x, y, **draw_kwargs)
        
        if "unicorn_cry" in result:
            app.draw_unicorn_hit(x, y)

        app.draw_person(x, y)
        app.refresh()

        return result

    return new_fn


def full_app():
    """Call the student's exploremaze function (once it's
    been overwritten) and then prompt for saving the data
    collected."""
    unicorn_data = exploremaze.search_maze()
    save = messagebox.askyesno("Save?", 
                               "Do you want to save the unicorn data by calling save_data?",
                               icon='question')

    if save:
        try:
            os.remove(exploremaze.OUTPUT_FILENAME)
        except OSError:
            pass

        exploremaze.save_data(unicorn_data, exploremaze.OUTPUT_FILENAME)
        messagebox.showinfo("Save", "Data saved.", icon='info')

def main():
    """Initialize the GUI and start exploring!"""
    # Initialize GUI
    master = tkinter.Tk()
    app = MazeViz(master, exploremaze.MAZE_WIDTH, exploremaze.MAZE_HEIGHT)

    # Overwrite get_url_data
    old = exploremaze.get_url_data
    exploremaze.get_url_data = overwrite_student(old, app)

    # Call search_maze and explore
    t = threading.Thread(target=full_app)
    t.start()

    # Open app
    tkinter.mainloop()

    # End the function call
    t.join()


if __name__ == '__main__':
    main()
