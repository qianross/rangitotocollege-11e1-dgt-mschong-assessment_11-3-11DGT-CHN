import tkinter as tk
import math
import os
import random

# Constants
WIDTH, HEIGHT = 512, 512
CIRCLE_RADIUS = 10
FRAME_DELAY = 16  # ~60 FPS
LEADER_SPEED = 2.75
FOLLOWER_SPEED = 2

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
wall_rect = (200, 200, 300, 300)  # x1, y1, x2, y2

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

    title = tk.Label(
        menu_frame,
        text="BLINDING FEAR",
        fg="white",
        bg="black",
        font=("Courier", 20, "bold")
    )
    title.pack(pady=20)

    start_btn = tk.Button(
        menu_frame,
        text="START",
        font=("Courier", 14),
        fg="white",
        bg="black",
        activeforeground="white",
        activebackground="black",
        highlightthickness=0,
        bd=0,
        command=lambda: start_game(menu_frame)
    )
    start_btn.pack(pady=10)

    exit_btn = tk.Button(
        menu_frame,
        text="EXIT",
        font=("Courier", 14),
        fg="white",
        bg="black",
        activeforeground="white",
        activebackground="black",
        highlightthickness=0,
        bd=0,
        command=root.destroy
    )
    exit_btn.pack(pady=10)

def start_game(menu_frame):
    menu_frame.destroy()

    global canvas, bg_img, spotlight_src, spotlight_img, leader_pos, spotlight_pos, clock_label, game_time
    game_time = 0

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

    # Draw wall
    canvas.create_rectangle(*wall_rect, fill="#353535", outline="", tags="wall")

    # Random initial positions
    leader_pos = [
        random.randint(CIRCLE_RADIUS, WIDTH - CIRCLE_RADIUS),
        random.randint(CIRCLE_RADIUS, HEIGHT - CIRCLE_RADIUS)
    ]
    spotlight_pos = [
        random.randint(CIRCLE_RADIUS, WIDTH - CIRCLE_RADIUS),
        random.randint(CIRCLE_RADIUS, HEIGHT - CIRCLE_RADIUS)
    ]

    # Clock label
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
    x1, y1, x2, y2 = wall_rect
    return x1 - CIRCLE_RADIUS < x < x2 + CIRCLE_RADIUS and y1 - CIRCLE_RADIUS < y < y2 + CIRCLE_RADIUS

def update_positions():
    moving = False
    new_x, new_y = leader_pos[0], leader_pos[1]

    # Default to base speed
    leader_speed = LEADER_SPEED

    # Check if pressing into wall
    pressing_into_wall = False

    # Check vertical collision intent
    if 'w' in keys_pressed:
        test_y = max(leader_pos[1] - LEADER_SPEED, CIRCLE_RADIUS)
        if will_collide(leader_pos[0], test_y):
            pressing_into_wall = True
    if 's' in keys_pressed:
        test_y = min(leader_pos[1] + LEADER_SPEED, HEIGHT - CIRCLE_RADIUS)
        if will_collide(leader_pos[0], test_y):
            pressing_into_wall = True

    # Check horizontal collision intent
    if 'a' in keys_pressed:
        test_x = max(leader_pos[0] - LEADER_SPEED, CIRCLE_RADIUS)
        if will_collide(test_x, leader_pos[1]):
            pressing_into_wall = True
    if 'd' in keys_pressed:
        test_x = min(leader_pos[0] + LEADER_SPEED, WIDTH - CIRCLE_RADIUS)
        if will_collide(test_x, leader_pos[1]):
            pressing_into_wall = True

    # Apply speed boost if pressing into wall
    if pressing_into_wall:
        leader_speed = int(LEADER_SPEED * 2)

    # Attempt vertical movement
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

    # Attempt horizontal movement
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

    # Move spotlight toward leader
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
        game_time += FRAME_DELAY / 1000  # Convert ms to seconds

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