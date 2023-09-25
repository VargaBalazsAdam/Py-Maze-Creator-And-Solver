import pygame
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import tkinter.filedialog as filedialog
import os
from collections import deque
import heapq  

# Initialize Pygame
pygame.init()

# Constants
GRID_WIDTH = 20
GRID_HEIGHT = 20
GRID_SIZE = 25
MIN_GRID_SIZE = 25
MAX_GRID_SIZE = 100
DEFAULT_COLOR = "WHITE"
visited = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
# Add a variable to track placement mode
placement_mode = False
previous_square = None  # To store the previously placed square
red_square_coords = None
root = tk.Tk()
root.title("Find Path")

# Create a canvas for the grid and add vertical and horizontal scrollbars
canvas_frame = ttk.Frame(root)
canvas_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(canvas_frame, width=GRID_WIDTH * GRID_SIZE, height=GRID_HEIGHT * GRID_SIZE)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

canvas_vscrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
canvas_vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

canvas_hscrollbar = ttk.Scrollbar(root, orient=tk.HORIZONTAL, command=canvas.xview)
canvas_hscrollbar.pack(fill=tk.X)

canvas.configure(yscrollcommand=canvas_vscrollbar.set, xscrollcommand=canvas_hscrollbar.set)

# Create buttons (outside the canvas)
button_frame = ttk.Frame(root)
button_frame.pack()

# Input fields (outside the canvas)
input_frame = ttk.Frame(root)
input_frame.pack()

clear_button = ttk.Button(input_frame, text="Clear Path")
clear_button.grid(row=0, column=1)
load_button = ttk.Button(input_frame, text="Load Map")
load_button.grid(row=0, column=2)

# Create the grid
grid = [[DEFAULT_COLOR for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def toggle_placement_mode():
    global placement_mode
    placement_mode = not placement_mode

def resize_grid(new_width, new_height):
    global GRID_WIDTH, GRID_HEIGHT, grid

    if new_width >= 1 and new_height >= 1:
        # Store the old grid data
        old_grid = grid
        old_width = GRID_WIDTH
        old_height = GRID_HEIGHT

        # Initialize the new grid with DEFAULT_COLOR
        grid = [[DEFAULT_COLOR for _ in range(new_width)] for _ in range(new_height)]

        # Copy the data from the old grid to the new grid (up to the minimum size)
        for x in range(min(old_width, new_width)):
            for y in range(min(old_height, new_height)):
                grid[y][x] = old_grid[y][x]

        # Update other variables
        GRID_WIDTH = new_width
        GRID_HEIGHT = new_height
        canvas.config(scrollregion=(0, 0, GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE))

        # Redraw the grid
        draw_grid()
        draw_squares()

def draw_grid():
    for x in range(0, GRID_WIDTH * GRID_SIZE, GRID_SIZE):
        canvas.create_line(x, 0, x, GRID_HEIGHT * GRID_SIZE, fill="black")
    for y in range(0, GRID_HEIGHT * GRID_SIZE, GRID_SIZE):
        canvas.create_line(0, y, GRID_WIDTH * GRID_SIZE, y, fill="black")

def draw_squares():
    global grid  # Declare grid as a global variable here
    canvas.delete("all")
    draw_grid()
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            square_color = grid[y][x]
            if square_color != DEFAULT_COLOR:
                canvas.create_rectangle(x * GRID_SIZE, y * GRID_SIZE, (x + 1) * GRID_SIZE, (y + 1) * GRID_SIZE, fill=square_color)

def read_data():
    global grid  # Declare grid as a global variable here
    try:
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "r") as file:
                lines = file.readlines()
                new_width = len(lines[0].strip())
                new_height = len(lines)
                resize_grid(new_width, new_height)  # Resize the grid
                for y, line in enumerate(lines):
                    values = line.strip().split()
                    for x, value in enumerate(values):
                        if x < GRID_WIDTH and y < GRID_HEIGHT:
                            grid[y][x] = value
            draw_squares()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load data from file: {str(e)}")

def reset_grid():
    global grid
    grid = [[DEFAULT_COLOR for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    draw_squares()

# Bind the toggle_placement_mode function to a button
toggle_placement_button = ttk.Button(input_frame, text="Toggle Placement Mode", command=toggle_placement_mode)
toggle_placement_button.grid(row=0, column=0)

GREEN = "GREEN"
RED = "RED"
ORANGE = "ORANGE"
def canvas_click(event):
    global placement_mode, previous_square
    x = event.x // GRID_SIZE
    y = event.y // GRID_SIZE

    # Check if the click is within the grid bounds
    if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
        if placement_mode:
            # Check if the clicked square is white before placing the red square
            if grid[y][x] == DEFAULT_COLOR:
                # Delete the previous square
                if previous_square:
                    x_prev, y_prev, _ = previous_square
                    grid[y_prev][x_prev] = DEFAULT_COLOR
                # Place a RED square
                grid[y][x] = RED
                previous_square = (x, y, RED)
                draw_squares()
        else:
            if grid[y][x] == GREEN:
                find_shortest_path((x, y))




# Function to find the shortest path using the A* algorithm
def find_shortest_path(target):
    start = find_square_position(RED)
    if start is None:
        return

    open_set = [(0, start)]
    came_from = {}

    g_score = {pos: float("inf") for pos in grid_positions()}
    g_score[start] = 0

    f_score = {pos: float("inf") for pos in grid_positions()}
    f_score[start] = heuristic(start, target)

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == target:
            reconstruct_path(came_from, current)
            return

        for neighbor in neighbors(current):
            tentative_g_score = g_score[current] + 1

            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, target)

                if neighbor not in [item[1] for item in open_set]:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

def find_square_position(square_color):
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if grid[y][x] == square_color:
                return (x, y)
    return None

def grid_positions():
    return [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)]

def neighbors(pos):
    x, y = pos
    adjacent_positions = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    valid_neighbors = []

    for neighbor in adjacent_positions:
        x_neighbor, y_neighbor = neighbor
        if neighbor in grid_positions() and grid[y_neighbor][x_neighbor] != "BLUE":
            valid_neighbors.append(neighbor)

    return valid_neighbors

def heuristic(a, b):
    x1, y1 = a
    x2, y2 = b
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current):
    path = []
    while current in came_from:
        path.insert(0, current)
        current = came_from[current]

    for x, y in path[:-1]:  # Exclude the last position (the green square)
        if grid[y][x] != RED:
            grid[y][x] = ORANGE

    draw_squares()


def clear_path():
    # Reset the grid colors
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] == "ORANGE":
                grid[y][x] = DEFAULT_COLOR
    draw_squares()



canvas.bind("<Button-1>", canvas_click)

clear_button.configure(command=clear_path)
load_button.configure(command=read_data)  # Bind Load button to read_data function

# Initial grid drawing
draw_grid()
draw_squares()

# Run the Tkinter main loop
root.mainloop()
