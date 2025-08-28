import tkinter as tk
import math
import os

# Constants
WIDTH, HEIGHT = 512, 512
CIRCLE_RADIUS = 10
FRAME_DELAY = 16  # ~60 FPS
MOVE_SPEED = 4
FOLLOW_SPEED = 0.1  # How quickly the spotlight follows the leader

def rgb_to_hex(rgb_tuple):
    return "#%02x%02x%02x" % rgb_tuple

# Initialize window
root = tk.Tk()
root.title("Spotlight Follows Leader")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
canvas.pack()

# Get path to the current script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct full paths to the image files
bg_path = os.path.join(script_dir, "noiseTexture.png")
spotlight_path = os.path.join(script_dir, "noiseTexture 1.png")

# Check if image files exist
if not os.path.exists(bg_path):
    print(f"❌ Background image not found at: {bg_path}")
    root.destroy()
    exit()

if not os.path.exists(spotlight_path):
    print(f"❌ Spotlight image not found at: {spotlight_path}")
    root.destroy()
    exit()

# Load background and spotlight textures
bg_img = tk.PhotoImage(file=bg_path)
spotlight_src = tk.PhotoImage(file=spotlight_path)

# Draw background once
canvas.create_image((0, 0), image=bg_img, anchor="nw")

# Create spotlight image layer
spotlight_img = tk.PhotoImage(width=WIDTH, height=HEIGHT)
canvas.create_image((0, 0), image=spotlight_img, anchor="nw")

# Positions
leader_pos = [WIDTH // 2, HEIGHT // 2]
spotlight_pos = [WIDTH // 2, HEIGHT // 2]
keys_pressed = set()

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

def update_positions():
    # Move leader based on keys
    moving = False
    if 'w' in keys_pressed:
        leader_pos[1] = max(leader_pos[1] - MOVE_SPEED, CIRCLE_RADIUS)
        moving = True
    if 's' in keys_pressed:
        leader_pos[1] = min(leader_pos[1] + MOVE_SPEED, HEIGHT - CIRCLE_RADIUS)
        moving = True
    if 'a' in keys_pressed:
        leader_pos[0] = max(leader_pos[0] - MOVE_SPEED, CIRCLE_RADIUS)
        moving = True
    if 'd' in keys_pressed:
        leader_pos[0] = min(leader_pos[0] + MOVE_SPEED, WIDTH - CIRCLE_RADIUS)
        moving = True

    # Only update spotlight if movement keys are pressed
    if moving:
        spotlight_pos[0] += (leader_pos[0] - spotlight_pos[0]) * FOLLOW_SPEED
        spotlight_pos[1] += (leader_pos[1] - spotlight_pos[1]) * FOLLOW_SPEED

    draw_spotlight()
    root.after(FRAME_DELAY, update_positions)

def on_key_press(event):
    keys_pressed.add(event.keysym.lower())

def on_key_release(event):
    keys_pressed.discard(event.keysym.lower())

# Bind key events
root.bind("<KeyPress>", on_key_press)
root.bind("<KeyRelease>", on_key_release)

# Start animation
draw_spotlight()
update_positions()
root.mainloop()