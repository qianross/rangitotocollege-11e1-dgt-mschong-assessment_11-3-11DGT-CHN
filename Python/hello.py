import tkinter as tk
import math
import os
import random

# Constants
WIDTH, HEIGHT = 1000, 1000
CIRCLE_RADIUS = 6
FRAME_DELAY = 16  # ~60 FPS
LEADER_SPEED = 4.1
FOLLOWER_SPEED = 4
CELL_SIZE = 80
WALL_THICKNESS = 7
GAP_SIZE = 25  # Size of entry hole in thin walls

# Global variables
canvas = None
bg_img = None
spotlight_src = None
spotlight_img = None
leader_pos = []
spotlight_pos = []
keys_pressed = set()
clock_label = None
game_time = 0
wall_rects = []

def rgb_to_hex(rgb_tuple):
    return "#%02x%02x%02x" % rgb_tuple

# Initialize window
root = tk.Tk()
root.title("Blinding Fear")
root.geometry(f"{WIDTH}x{HEIGHT}")
root.configure(bg="black")

def show_menu():
    menu_frame = tk.Frame(root, width=WIDTH, height=HEIGHT, bg="black")
    menu_frame.pack(fill="both", expand=True)

    title = tk.Label(menu_frame, text="BLINDING FEAR", fg="white", bg="black", font=("Courier", 20, "bold"))
    title.pack(pady=20)

    start_btn = tk.Button(menu_frame, text="START", font=("Courier", 14), fg="white", bg="black",
                          activeforeground="white", activebackground="black", highlightthickness=0, bd=0,
                          command=lambda: start_game(menu_frame))
    start_btn.pack(pady=10)

    exit_btn = tk.Button(menu_frame, text="EXIT", font=("Courier", 14), fg="white", bg="black",
                         activeforeground="white", activebackground="black", highlightthickness=0, bd=0,
                         command=root.destroy)
    exit_btn.pack(pady=10)

def start_game(menu_frame):
    menu_frame.destroy()

    global canvas, bg_img, spotlight_src, spotlight_img, leader_pos, spotlight_pos, clock_label, game_time, wall_rects
    game_time = 0
    wall_rects.clear()

    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
    canvas.pack()

    # Load images
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bg_path = os.path.join(script_dir, "noiseTexture.png")
    spotlight_path = os.path.join(script_dir, "noiseTexture 1.png")

    if not os.path.exists(bg_path) or not os.path.exists(spotlight_path):
        print("Required image files not found.")
        root.destroy()
        return

    bg_img = tk.PhotoImage(file=bg_path)
    spotlight_src = tk.PhotoImage(file=spotlight_path)

    canvas.create_image((0, 0), image=bg_img, anchor="nw")
    spotlight_img = tk.PhotoImage(width=WIDTH, height=HEIGHT)
    canvas.create_image((0, 0), image=spotlight_img, anchor="nw")

    # Maze generation
    GRID_COLS = WIDTH // CELL_SIZE
    GRID_ROWS = HEIGHT // CELL_SIZE
    maze = [[[False, True, True, True, True] for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

    def carve_maze(x, y):
        maze[y][x][0] = True
        directions = [(0, -1, 1, 3), (1, 0, 2, 0), (0, 1, 3, 1), (-1, 0, 0, 2)]
        random.shuffle(directions)
        for dx, dy, wall, opposite in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS and not maze[ny][nx][0]:
                maze[y][x][wall + 1] = False
                maze[ny][nx][opposite + 1] = False
                carve_maze(nx, ny)

    start_x = random.randint(0, GRID_COLS - 1)
    start_y = random.randint(0, GRID_ROWS - 1)
    carve_maze(start_x, start_y)

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            x1 = col * CELL_SIZE
            y1 = row * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            _, top, right, bottom, left = maze[row][col]

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            x1 = col * CELL_SIZE
            y1 = row * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            _, top, right, bottom, left = maze[row][col]

            if top:
                if x2 - x1 >= CELL_SIZE:
                    offset = random.randint(1, 9)
                    mid_x1 = x1 + (CELL_SIZE - GAP_SIZE) // offset
                    mid_x2 = mid_x1 + GAP_SIZE
                    wall_rects.append((x1, y1, mid_x1, y1 + WALL_THICKNESS))
                    wall_rects.append((mid_x2, y1, x2, y1 + WALL_THICKNESS))
                else:
                    wall_rects.append((x1, y1, x2, y1 + WALL_THICKNESS))

            if right:
                if y2 - y1 >= CELL_SIZE:
                    offset = random.randint(1, 9)
                    mid_y1 = y1 + (CELL_SIZE - GAP_SIZE) // offset
                    mid_y2 = mid_y1 + GAP_SIZE
                    wall_rects.append((x2 - WALL_THICKNESS, y1, x2, mid_y1))
                    wall_rects.append((x2 - WALL_THICKNESS, mid_y2, x2, y2))
                else:
                    wall_rects.append((x2 - WALL_THICKNESS, y1, x2, y2))

            if bottom:
                if x2 - x1 >= CELL_SIZE:
                    offset = random.randint(1, 9)
                    mid_x1 = x1 + (CELL_SIZE - GAP_SIZE) // offset
                    mid_x2 = mid_x1 + GAP_SIZE
                    wall_rects.append((x1, y2 - WALL_THICKNESS, mid_x1, y2))
                    wall_rects.append((mid_x2, y2 - WALL_THICKNESS, x2, y2))
                else:
                    wall_rects.append((x1, y2 - WALL_THICKNESS, x2, y2))

            if left:
                if y2 - y1 >= CELL_SIZE:
                    offset = random.randint(1, 9)
                    mid_y1 = y1 + (CELL_SIZE - GAP_SIZE) // offset
                    mid_y2 = mid_y1 + GAP_SIZE
                    wall_rects.append((x1, y1, x1 + WALL_THICKNESS, mid_y1))
                    wall_rects.append((x1, mid_y2, x1 + WALL_THICKNESS, y2))
                else:
                    wall_rects.append((x1, y1, x1 + WALL_THICKNESS, y2))

    for x1, y1, x2, y2 in wall_rects:
        canvas.create_rectangle(x1, y1, x2, y2, fill="#000000", outline="", tags="wall")

    def get_safe_spawn():
        while True:
            x = random.randint(CIRCLE_RADIUS, WIDTH - CIRCLE_RADIUS)
            y = random.randint(CIRCLE_RADIUS, HEIGHT - CIRCLE_RADIUS)
            if not will_collide(x, y):
                return [x, y]

    leader_pos = get_safe_spawn()
    spotlight_pos = get_safe_spawn()

    clock_label = tk.Label(root, text="00:00", font=("Courier", 14), fg="white", bg="black")
    clock_label.place(x=10, y=10)

    root.bind("<KeyPress>", on_key_press)
    root.bind("<KeyRelease>", on_key_release)

    draw_spotlight()
    update_positions()
    update_clock()

def draw_spotlight():
    cx, cy = int(spotlight_pos[0]), int(spotlight_pos[1])
    r = CIRCLE_RADIUS

    x0 = max(cx - r, 0)
    y0 = max(cy - r, 0)
    x1 = min(cx + r, WIDTH - 1)
    y1 = min(cy + r, HEIGHT - 1)

    for x in range(x0, x1):
        for y in range(y0, y1):
            dist = math.hypot(x - cx, y - cy)
            if dist <= r:
                color = rgb_to_hex(spotlight_src.get(x, y))
            else:
                color = rgb_to_hex(bg_img.get(x, y))
            spotlight_img.put(color, (x, y))

    canvas.delete("leader")
    canvas.create_oval(
        leader_pos[0] - r, leader_pos[1] - r,
        leader_pos[0] + r, leader_pos[1] + r,
        fill="white", outline="", tags="leader"
    )

def will_collide(x, y):
    for x1, y1, x2, y2 in wall_rects:
        if x1 - CIRCLE_RADIUS < x < x2 + CIRCLE_RADIUS and y1 - CIRCLE_RADIUS < y < y2 + CIRCLE_RADIUS:
            return True
    return False

def update_positions():
    moving = False
    new_x, new_y = leader_pos[0], leader_pos[1]
    leader_speed = LEADER_SPEED
    pressing_into_wall = False

    if 'w' in keys_pressed:
        test_y = max(leader_pos[1] - LEADER_SPEED, CIRCLE_RADIUS)
        if will_collide(leader_pos[0], test_y):
            pressing_into_wall = True
    if 's' in keys_pressed:
        test_y = min(leader_pos[1] + LEADER_SPEED, HEIGHT - CIRCLE_RADIUS)
        if will_collide(leader_pos[0], test_y):
            pressing_into_wall = True
    if 'a' in keys_pressed:
        test_x = max(leader_pos[0] - LEADER_SPEED, CIRCLE_RADIUS)
        if will_collide(test_x, leader_pos[1]):
            pressing_into_wall = True
    if 'd' in keys_pressed:
        test_x = min(leader_pos[0] + LEADER_SPEED, WIDTH - CIRCLE_RADIUS)
        if will_collide(test_x, leader_pos[1]):
            pressing_into_wall = True

    if pressing_into_wall:
        leader_speed = int(LEADER_SPEED * 2)

    if 'w' in keys_pressed:
        test_y = max(leader_pos[1] - leader_speed, CIRCLE_RADIUS)
        if not will_collide(leader_pos[0], test_y):
            new_y = test_y
        moving = True
    if 's' in keys_pressed:
        test_y = min(leader_pos[1] + leader_speed, HEIGHT - CIRCLE_RADIUS)
        if not will_collide(leader_pos[0], test_y):
            new_y = test_y
        moving = True
    if 'a' in keys_pressed:
        test_x = max(leader_pos[0] - leader_speed, CIRCLE_RADIUS)
        if not will_collide(test_x, new_y):
            new_x = test_x
        moving = True
    if 'd' in keys_pressed:
        test_x = min(leader_pos[0] + leader_speed, WIDTH - CIRCLE_RADIUS)
        if not will_collide(test_x, new_y):
            new_x = test_x
        moving = True

    leader_pos[0], leader_pos[1] = new_x, new_y

    if moving:
        dx = leader_pos[0] - spotlight_pos[0]
        dy = leader_pos[1] - spotlight_pos[1]
        dist = math.hypot(dx, dy)
        if dist > 0:
            step = min(FOLLOWER_SPEED, dist)
            spotlight_pos[0] += step * dx / dist
            spotlight_pos[1] += step * dy / dist

    draw_spotlight()
    root.after(FRAME_DELAY, update_positions)

def update_clock():
    global game_time
    if any(k in keys_pressed for k in ['w', 'a', 's', 'd']):
        game_time += FRAME_DELAY / 1000

    minutes = int(game_time) // 60
    seconds = int(game_time) % 60
    clock_label.config(text=f"{minutes:02}:{seconds:02}")
    root.after(FRAME_DELAY, update_clock)

def on_key_press(event):
    keys_pressed.add(event.keysym.lower())

def on_key_release(event):
    keys_pressed.discard(event.keysym.lower())

# Launch menu
show_menu()
root.mainloop()