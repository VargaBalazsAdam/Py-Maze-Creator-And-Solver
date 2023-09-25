import pygame
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import tkinter.filedialog as filedialog
import os

# Initialize Pygame
pygame.init()

# Constants
GRID_WIDTH = 20
GRID_HEIGHT = 20
GRID_SIZE = 25
MIN_GRID_SIZE = 25
MAX_GRID_SIZE = 100
DEFAULT_COLOR = "WHITE"

root = tk.Tk()
root.title("Create Map")

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
buttons = {
    "BLUE": ttk.Button(button_frame, text="Blue"),
    "GREEN": ttk.Button(button_frame, text="Green"),
}

for color, button in buttons.items():
    button.grid(row=0, column=list(buttons.keys()).index(color))

# Input fields (outside the canvas)
input_frame = ttk.Frame(root)
input_frame.pack()
width_label = ttk.Label(input_frame, text="Width:")
width_label.grid(row=0, column=0)
width_entry = ttk.Entry(input_frame, width=5)
width_entry.grid(row=0, column=1)
height_label = ttk.Label(input_frame, text="Height:")
height_label.grid(row=0, column=2)
height_entry = ttk.Entry(input_frame, width=5)
height_entry.grid(row=0, column=3)


apply_button = ttk.Button(input_frame, text="Apply")
apply_button.grid(row=0, column=4)
save_button = ttk.Button(input_frame, text="Save")
save_button.grid(row=0, column=5)
# Initialize current color
current_color = "BLUE"
previous_color = "BLUE"
# Create the grid
grid = [[DEFAULT_COLOR for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def draw_grid():
    for x in range(0, GRID_WIDTH * GRID_SIZE, GRID_SIZE):
        canvas.create_line(x, 0, x, GRID_HEIGHT * GRID_SIZE, fill="black")
    for y in range(0, GRID_HEIGHT * GRID_SIZE, GRID_SIZE):
        canvas.create_line(0, y, GRID_WIDTH * GRID_SIZE, y, fill="black")

def draw_squares():
    canvas.delete("all")
    draw_grid()
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            square_color = grid[y][x]
            if square_color != DEFAULT_COLOR:
                canvas.create_rectangle(x * GRID_SIZE, y * GRID_SIZE, (x + 1) * GRID_SIZE, (y + 1) * GRID_SIZE, fill=square_color)

# Variables for tracking mouse state
is_mouse_pressed = False
is_mouse_pressed_right = False
# Function to get the scroll position
def get_scroll_position():
    x_pos = canvas.canvasx(0)
    y_pos = canvas.canvasy(0)
    return x_pos, y_pos
# Function to handle mouse button press
def handle_canvas_press(event):
    global current_color, previous_color, is_mouse_pressed, is_mouse_pressed_right
    x_pos, y_pos = get_scroll_position()
    x = int((event.x + x_pos) // GRID_SIZE)
    y = int((event.y + y_pos) // GRID_SIZE)
    if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
        if event.num == 1:  # Left-click
            is_mouse_pressed = True
            grid[y][x] = current_color
        elif event.num == 3:  # Right-click
            is_mouse_pressed_right = True
            previous_color = current_color  # Store the previous color
            current_color = DEFAULT_COLOR
            grid[y][x] = current_color
        draw_squares()

# Function to handle mouse button release
def handle_canvas_release(event):
    global is_mouse_pressed, is_mouse_pressed_right, current_color, previous_color
    is_mouse_pressed = False
    is_mouse_pressed_right = False
    if event.num == 3:
        current_color = previous_color

# Function to handle mouse motion while the button is pressed (drawing)
def handle_canvas_motion(event):
    global is_mouse_pressed, is_mouse_pressed_right
    x_pos, y_pos = get_scroll_position()
    x = int((event.x + x_pos) // GRID_SIZE)
    y = int((event.y + y_pos) // GRID_SIZE)
    if is_mouse_pressed and 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
        grid[y][x] = current_color
    elif is_mouse_pressed_right and 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
        grid[y][x] = DEFAULT_COLOR
    draw_squares()

def handle_button_click(color):
    global current_color
    current_color = color

def resize_grid():
    global GRID_WIDTH, GRID_HEIGHT, GRID_SIZE, grid, current_color, previous_color

    try:
        new_width = int(width_entry.get())
        new_height = int(height_entry.get())

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
            GRID_SIZE = MIN_GRID_SIZE  # Reset the grid size to the minimum
            canvas.config(scrollregion=(0, 0, GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE))

            # Redraw the grid
            draw_grid()
            draw_squares()

    except ValueError:
        messagebox.showerror("Error", "Please enter valid dimensions.")

def save_grid_data():
    try:
        # Prompt the user for a filename
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if file_path:
            # Check if the file already exists
            if os.path.exists(file_path):
                overwrite = messagebox.askyesno("File Exists", "The file already exists. Do you want to overwrite it?")
                if not overwrite:
                    return

            # Save the grid data to the specified file
            with open(file_path, "w") as file:
                for row in grid:
                    file.write(" ".join(row) + "\n")
            messagebox.showinfo("Success", f"Grid data saved to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving grid data: {str(e)}")



def reset_grid():
    global grid
    grid = [[DEFAULT_COLOR for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    draw_squares()

# Bind button clicks to functions
buttons["BLUE"].configure(command=lambda: handle_button_click("BLUE"))
buttons["GREEN"].configure(command=lambda: handle_button_click("GREEN"))
save_button.configure(command=save_grid_data)  # Bind Save button to save_grid_data function
apply_button.configure(command=resize_grid)
# Bind mouse button press and release events
canvas.bind("<Button-1>", handle_canvas_press)  # Left-click
canvas.bind("<ButtonRelease-1>", handle_canvas_release)  # Left-click release
canvas.bind("<Button-3>", handle_canvas_press)  # Right-click
canvas.bind("<ButtonRelease-3>", handle_canvas_release)  # Right-click release

# Bind mouse motion event (drawing while mouse button is pressed)
canvas.bind("<B1-Motion>", handle_canvas_motion)  # Left-click motion
canvas.bind("<B3-Motion>", handle_canvas_motion)  # Right-click motion

# Initial grid drawing
draw_grid()
draw_squares()

# Run the Tkinter main loop
root.mainloop()
