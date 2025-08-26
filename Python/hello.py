import tkinter as tk
import math

WIDTH, HEIGHT = 512, 512
CIRCLE_RADIUS = 40
PIXEL_SIZE = 8
FRAME_DELAY = 16  # ~60 FPS

GRID_WIDTH = WIDTH // PIXEL_SIZE
GRID_HEIGHT = HEIGHT // PIXEL_SIZE

def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb

root = tk.Tk()
root.title("Optimized Spotlight")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
canvas.pack()

bg_img = tk.PhotoImage(file="C:/Users/182379.RANGIWORLD.000/Downloads/noiseTexture.png")
spotlight_src = tk.PhotoImage(file="C:/Users/182379.RANGIWORLD.000/Downloads/noiseTexture (1).png")
spotlight_img = tk.PhotoImage(width=WIDTH, height=HEIGHT)

canvas.create_image((0, 0), image=bg_img, anchor="nw")
canvas.create_image((0, 0), image=spotlight_img, anchor="nw")

circle_pos = [WIDTH // 2, HEIGHT // 2]
target_pos = [WIDTH // 2, HEIGHT // 2]

# Precompute pixel centers
pixel_centers = [(gx * PIXEL_SIZE + PIXEL_SIZE // 2, gy * PIXEL_SIZE + PIXEL_SIZE // 2)
                 for gx in range(GRID_WIDTH) for gy in range(GRID_HEIGHT)]

# Precompute hex color grids
bg_colors = [[rgb_to_hex(bg_img.get(x, y)) for y in range(HEIGHT)] for x in range(WIDTH)]
spotlight_colors = [[rgb_to_hex(spotlight_src.get(x, y)) for y in range(HEIGHT)] for x in range(WIDTH)]

def draw_spotlight():
    cx, cy = int(circle_pos[0]), int(circle_pos[1])
    pixels = []
    for x, y in pixel_centers:
        dist = math.hypot(x - cx, y - cy)
        color = spotlight_colors[x][y] if dist <= CIRCLE_RADIUS else bg_colors[x][y]
        pixels.append((color, (x - PIXEL_SIZE // 2, y - PIXEL_SIZE // 2,
                               x + PIXEL_SIZE // 2, y + PIXEL_SIZE // 2)))
    for color, box in pixels:
        spotlight_img.put(color, to=box)

    canvas.delete("test_circle")
    canvas.create_oval(cx - CIRCLE_RADIUS, cy - CIRCLE_RADIUS,
                       cx + CIRCLE_RADIUS, cy + CIRCLE_RADIUS,
                       outline="", width=2, tags="test_circle")

def glide():
    speed = 0.2
    dx = target_pos[0] - circle_pos[0]
    dy = target_pos[1] - circle_pos[1]
    if abs(dx) > 1 or abs(dy) > 1:
        circle_pos[0] += dx * speed
        circle_pos[1] += dy * speed
        draw_spotlight()
    root.after(FRAME_DELAY, glide)

def on_mouse_move(event):
    target_pos[0] = (event.x // PIXEL_SIZE) * PIXEL_SIZE + PIXEL_SIZE // 2
    target_pos[1] = (event.y // PIXEL_SIZE) * PIXEL_SIZE + PIXEL_SIZE // 2

canvas.bind("<Motion>", on_mouse_move)
draw_spotlight()
glide()
root.mainloop()