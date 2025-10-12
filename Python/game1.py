import tkinter as tk
import math
import os
import random

# Constants
WIDTH, HEIGHT = 1000, 1000
CIRCLE_RADIUS = 6
FRAME_DELAY = 16  # ~60 FPS
LEADER_SPEED = 4.1
FOLLOWER_SPEED = 3.5
CELL_SIZE = 79
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

NUM_BLOBS = 4
BLOB_RADIUS = 6
blobs = []
score = 0
score_label = None

YELLOW_RADIUS = 12
yellow_pos = []

def rgb_to_hex(rgb_tuple):
    return "#%02x%02x%02x" % rgb_tuple

# Initialize window
root = tk.Tk()
root.title("Blinding Fear")
root.geometry(f"{WIDTH}x{HEIGHT}")
root.configure(bg="black")

def show_menu():
    # Create menu frame
    menu_frame = tk.Frame(root, width=WIDTH, height=HEIGHT, bg="black")
    menu_frame.pack(fill="both", expand=True)

    title = tk.Label(menu_frame, text="BLINDING FEAR", fg="white", bg="black", font=("Courier", 20, "bold"))
    title.pack(pady=20)

    start_btn = tk.Button(menu_frame, text="START", font=("Courier", 14), fg="white", bg="black",
                          activeforeground="white", activebackground="black", highlightthickness=0, bd=0,
                          command=lambda: start_game(menu_frame))
    start_btn.pack(pady=10)
    # Create EXIT button
    exit_btn = tk.Button(menu_frame, text="EXIT", font=("Courier", 14), fg="white", bg="black",
                         activeforeground="white", activebackground="black", highlightthickness=0, bd=0,
                         command=root.destroy)
    exit_btn.pack(pady=10)

def get_safe_blob_spawn():
    # Spawn blobs away from walls, player start, and other blobs
    while True:
        x = random.randint(BLOB_RADIUS, WIDTH - BLOB_RADIUS)
        y = random.randint(BLOB_RADIUS, HEIGHT - BLOB_RADIUS)
        # Avoid walls and player start
        if not will_collide(x, y):
            # Don't spawn on player or other blobs
            if math.hypot(x - leader_pos[0], y - leader_pos[1]) > CIRCLE_RADIUS + BLOB_RADIUS + 10:
                if all(math.hypot(x - bx, y - by) > BLOB_RADIUS * 2 for bx, by in blobs):
                    return [x, y]

def spawn_blobs():
    global blobs
    blobs = []
    for _ in range(NUM_BLOBS):
        blobs.append(get_safe_blob_spawn())

def draw_blobs():
    canvas.delete("blob")
    for bx, by in blobs:
        canvas.create_oval(
            bx - BLOB_RADIUS, by - BLOB_RADIUS,
            bx + BLOB_RADIUS, by + BLOB_RADIUS,
            fill="blue", outline="", tags="blob"
        )

def check_blob_collision():
    # Check if leader collides with any blobs
    global score
    for i, (bx, by) in enumerate(blobs):
        if math.hypot(leader_pos[0] - bx, leader_pos[1] - by) <= CIRCLE_RADIUS + BLOB_RADIUS:
            score += 1 # Increase score
            if score_label:
                score_label.config(text=f"Score: {score}")
            # Respawn this blob
            blobs[i] = get_safe_blob_spawn()

def start_game(menu_frame):
    menu_frame.destroy()

    global canvas, bg_img, spotlight_src, spotlight_img, leader_pos, spotlight_pos, clock_label, game_time, wall_rects, score, score_label, yellow_pos
    game_time = 0
    wall_rects.clear()
    score = 0

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
        # Carve passages using DFS
        maze[y][x][0] = True
        directions = [(0, -1, 1, 3), (1, 0, 2, 0), (0, 1, 3, 1), (-1, 0, 0, 2)] # (dx, dy, wall, opposite)
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
        # Spawn out of walls
        while True:
            x = random.randint(CIRCLE_RADIUS, WIDTH - CIRCLE_RADIUS)
            y = random.randint(CIRCLE_RADIUS, HEIGHT - CIRCLE_RADIUS)
            if not will_collide(x, y):
                return [x, y]

    leader_pos = get_safe_spawn()
    spotlight_pos = get_safe_spawn()

    spawn_blobs()  # Spawn blobs at game start

    yellow_pos = get_safe_yellow_spawn()

    clock_label = tk.Label(root, text="00:00", font=("Courier", 14), fg="white", bg="black")
    clock_label.place(x=10, y=10)

    score_label = tk.Label(root, text="Score: 0", font=("Courier", 14), fg="cyan", bg="black")
    score_label.place(x=10, y=40)

    root.bind("<KeyPress>", on_key_press)
    root.bind("<KeyRelease>", on_key_release)

    draw_spotlight()
    update_positions()
    update_clock()

def get_safe_yellow_spawn():
    # Spawn within 80-120 pixels of the leader, random direction, but not overlapping
    angle = random.uniform(0, 2 * math.pi)
    dist = random.randint(80, 120)
    x = int(leader_pos[0] + math.cos(angle) * dist)
    y = int(leader_pos[1] + math.sin(angle) * dist)
    # Clamp to screen bounds
    x = max(YELLOW_RADIUS, min(WIDTH - YELLOW_RADIUS, x))
    y = max(YELLOW_RADIUS, min(HEIGHT - YELLOW_RADIUS, y))
    return [x, y]

def draw_yellow():
    # Draw yellow blob
    canvas.delete("yellow")
    canvas.create_oval(
        yellow_pos[0] - YELLOW_RADIUS, yellow_pos[1] - YELLOW_RADIUS,
        yellow_pos[0] + YELLOW_RADIUS, yellow_pos[1] + YELLOW_RADIUS,
        fill="yellow", outline="", tags="yellow"
    )

def draw_spotlight():
    # Draws the leader/player
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
    draw_blobs()  # Draw blobs after leader
    draw_yellow()  # Draw yellow circle

def will_collide(x, y):
    # Check if (x, y) collides with any wall
    for x1, y1, x2, y2 in wall_rects:
        if x1 - CIRCLE_RADIUS < x < x2 + CIRCLE_RADIUS and y1 - CIRCLE_RADIUS < y < y2 + CIRCLE_RADIUS:
            return True
    return False

def get_current_username():
    # Get the last username in the file (current session)
    if os.path.exists("Python/username.txt"):
        with open("Python/username.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
            if lines:
                last_line = lines[-1]
                if ":" in last_line:
                    return last_line.split(":")[0]
                return last_line
    return "Unknown"

def save_score_and_time(username, score, game_time):
    # Save or update the score and time for the given username
    lines = []
    if os.path.exists("Python/username.txt"):
        with open("Python/username.txt", "r") as f:
            lines = f.readlines()
    found = False
    new_lines = []
    for line in lines:
        line_strip = line.strip()
        # Check for the correct username at the start of the line
        if line_strip.startswith(username + ":"):
            parts = line_strip.split(":")
            if len(parts) > 1:
                games = [g for g in parts[1].split(",") if not g.startswith("game1=") and not g.startswith("game1_time=")]
                # Get previous score if exists
                prev_score = 0
                for g in parts[1].split(","):
                    if g.startswith("game1="):
                        try:
                            prev_score = int(g.split("=")[1])
                        except ValueError:
                            prev_score = 0
                # Only update if new score is higher
                if score > prev_score:
                    games.append(f"game1={score}")
                    games.append(f"game1_time={int(game_time)}")
                else:
                    games.append(f"game1={prev_score}")
                    # Find previous time if exists
                    prev_time = None
                    for g in parts[1].split(","):
                        if g.startswith("game1_time="):
                            prev_time = g.split("=")[1]
                    if prev_time is not None:
                        games.append(f"game1_time={prev_time}")
                    else:
                        games.append(f"game1_time={int(game_time)}")
                new_line = f"{username}:{','.join(games)}\n"
            else:
                new_line = f"{username}:game1={score},game1_time={int(game_time)}\n"
            new_lines.append(new_line)
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f"{username}:game1={score},game1_time={int(game_time)}\n")
    with open("Python/username.txt", "w") as f:
        f.writelines(new_lines)

def game_over():
    # Remove game canvas and show Game Over screen
    if canvas:
        canvas.pack_forget()
    if clock_label:
        clock_label.place_forget()
    if score_label:
        score_label.place_forget()

    # Save score and time
    username = get_current_username()
    save_score_and_time(username, score, game_time)

    over_frame = tk.Frame(root, width=WIDTH, height=HEIGHT, bg="black")
    over_frame.pack(fill="both", expand=True)

    over_label = tk.Label(over_frame, text="GAME OVER", fg="red", bg="black", font=("Courier", 32, "bold"))
    over_label.pack(pady=60)

    score_display = tk.Label(over_frame, text=f"Score: {score}", fg="cyan", bg="black", font=("Courier", 18))
    score_display.pack(pady=10)

    time_display = tk.Label(over_frame, text=f"Time Survived: {int(game_time)//60:02}:{int(game_time)%60:02}", fg="white", bg="black", font=("Courier", 18))
    time_display.pack(pady=10)

    menu_btn = tk.Button(over_frame, text="RETURN TO MENU", font=("Courier", 14), fg="white", bg="black",
                         activeforeground="white", activebackground="black", highlightthickness=0, bd=0,
                         command=lambda: [over_frame.destroy(), show_menu()])
    menu_btn.pack(pady=20)

def update_positions():
    # Update positions of leader, spotlight, and yellow blob
    global leader_pos, spotlight_pos, yellow_pos, score
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

    # Store old position
    old_x, old_y = leader_pos[0], leader_pos[1]

    if 'w' in keys_pressed:
        test_y = max(leader_pos[1] - leader_speed, CIRCLE_RADIUS)
        if not will_collide(leader_pos[0], test_y):
            new_y = test_y
    if 's' in keys_pressed:
        test_y = min(leader_pos[1] + leader_speed, HEIGHT - CIRCLE_RADIUS)
        if not will_collide(leader_pos[0], test_y):
            new_y = test_y
    if 'a' in keys_pressed:
        test_x = max(leader_pos[0] - leader_speed, CIRCLE_RADIUS)
        if not will_collide(test_x, new_y):
            new_x = test_x
    if 'd' in keys_pressed:
        test_x = min(leader_pos[0] + leader_speed, WIDTH - CIRCLE_RADIUS)
        if not will_collide(test_x, new_y):
            new_x = test_x

    leader_pos[0], leader_pos[1] = new_x, new_y

    # Only move follower if player actually moved
    moving = (old_x != new_x or old_y != new_y)

    if moving:
        dx = leader_pos[0] - spotlight_pos[0]
        dy = leader_pos[1] - spotlight_pos[1]
        dist = math.hypot(dx, dy)
        if dist > 0:
            step = min(FOLLOWER_SPEED, dist)
            spotlight_pos[0] += step * dx / dist
            spotlight_pos[1] += step * dy / dist

    # Only move yellow if player actually moved
    if moving:
        dx = leader_pos[0] - yellow_pos[0]
        dy = leader_pos[1] - yellow_pos[1]
        dist = math.hypot(dx, dy)
        if dist > 0:
            step = min(FOLLOWER_SPEED, dist)
            # Move in the opposite direction from the leader
            yellow_pos[0] -= step * dx / dist
            yellow_pos[1] -= step * dy / dist

        # Teleport yellow to center if it touches the edge
        if (
            yellow_pos[0] <= YELLOW_RADIUS or yellow_pos[0] >= WIDTH - YELLOW_RADIUS or
            yellow_pos[1] <= YELLOW_RADIUS or yellow_pos[1] >= HEIGHT - YELLOW_RADIUS
        ):
            yellow_pos[0] = WIDTH // 2
            yellow_pos[1] = HEIGHT // 2

    check_blob_collision()  # Check for blob pickup

    # Yellow ball collection check
    if math.hypot(leader_pos[0] - yellow_pos[0], leader_pos[1] - yellow_pos[1]) <= CIRCLE_RADIUS + YELLOW_RADIUS:
        score += 10
        if score_label:
            score_label.config(text=f"Score: {score}")
        yellow_pos[:] = get_safe_yellow_spawn()  # respawn yellow ball near player

    # Game Over Check
    dx = leader_pos[0] - spotlight_pos[0]
    dy = leader_pos[1] - spotlight_pos[1]
    dist = math.hypot(dx, dy)
    if dist <= CIRCLE_RADIUS * 2:
        game_over()
        return

    draw_spotlight()
    root.after(FRAME_DELAY, update_positions)

def update_clock():
    # Updates the game timer when moving
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