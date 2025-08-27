import tkinter as tk
import math

WIDTH, HEIGHT = 512, 512
CIRCLE_RADIUS = 20
FRAME_DELAY = 16  # ~60 FPS
MOVE_SPEED = 4

def rgb_to_hex(rgb_tuple):
    return "#%02x%02x%02x" % rgb_tuple

root = tk.Tk()
root.title("WASD-Controlled Spotlight")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
canvas.pack()

# Load background and spotlight textures
bg_img = tk.PhotoImage(file="C:/Users/182379.RANGIWORLD.000/Downloads/noiseTexture.png")
spotlight_src = tk.PhotoImage(file="C:/Users/182379.RANGIWORLD.000/Downloads/noiseTexture (1).png")

# Draw background once
canvas.create_image((0, 0), image=bg_img, anchor="nw")

# Create spotlight image layer
spotlight_img = tk.PhotoImage(width=WIDTH, height=HEIGHT)
canvas.create_image((0, 0), image=spotlight_img, anchor="nw")

circle_pos = [WIDTH // 2, HEIGHT // 2]
keys_pressed = set()

def draw_spotlight():
    cx, cy = int(circle_pos[0]), int(circle_pos[1])
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

    canvas.delete("circle")
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="", width=2, tags="circle")

def move_spotlight():
    moved = False
    if 'w' in keys_pressed:
        circle_pos[1] = max(circle_pos[1] - MOVE_SPEED, CIRCLE_RADIUS)
        moved = True
    if 's' in keys_pressed:
        circle_pos[1] = min(circle_pos[1] + MOVE_SPEED, HEIGHT - CIRCLE_RADIUS)
        moved = True
    if 'a' in keys_pressed:
        circle_pos[0] = max(circle_pos[0] - MOVE_SPEED, CIRCLE_RADIUS)
        moved = True
    if 'd' in keys_pressed:
        circle_pos[0] = min(circle_pos[0] + MOVE_SPEED, WIDTH - CIRCLE_RADIUS)
        moved = True

    if moved:
        draw_spotlight()

    root.after(FRAME_DELAY, move_spotlight)

def on_key_press(event):
    keys_pressed.add(event.keysym.lower())

def on_key_release(event):
    keys_pressed.discard(event.keysym.lower())

root.bind("<KeyPress>", on_key_press)
root.bind("<KeyRelease>", on_key_release)

draw_spotlight()
move_spotlight()
root.mainloop()