import tkinter as tk
import random

WIDTH, HEIGHT = 512, 512
CIRCLE_RADIUS = 40

root = tk.Tk()
root.title("Noise Texture")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
canvas.pack()

# Create static noise image
img = tk.PhotoImage(width=WIDTH, height=HEIGHT)
canvas_img = canvas.create_image((0, 0), image=img, anchor="nw")

# Generate static black and white noise texture
bg_noise = [
    [f"#{v:02x}{v:02x}{v:02x}" for v in [random.choice([0, 255]) for _ in range(HEIGHT)]]
    for _ in range(WIDTH)
]

def draw_background():
    for x in range(WIDTH):
        for y in range(HEIGHT):
            img.put(bg_noise[x][y], (x, y))

draw_background()

# Initial spotlight position
circle_pos = [WIDTH // 2, HEIGHT // 2]
target_pos = [WIDTH // 2, HEIGHT // 2]

# Create spotlight as a canvas oval
spotlight_id = canvas.create_oval(
    circle_pos[0] - CIRCLE_RADIUS, circle_pos[1] - CIRCLE_RADIUS,
    circle_pos[0] + CIRCLE_RADIUS, circle_pos[1] + CIRCLE_RADIUS,
    fill="white", outline=""
)

def update_spotlight():
    cx, cy = int(circle_pos[0]), int(circle_pos[1])
    canvas.coords(
        spotlight_id,
        cx - CIRCLE_RADIUS, cy - CIRCLE_RADIUS,
        cx + CIRCLE_RADIUS, cy + CIRCLE_RADIUS
    )

def glide():
    speed = 0.2
    dx = target_pos[0] - circle_pos[0]
    dy = target_pos[1] - circle_pos[1]
    if abs(dx) > 1 or abs(dy) > 1:
        circle_pos[0] += dx * speed
        circle_pos[1] += dy * speed
        update_spotlight()
    root.after(24, glide)

def on_mouse_move(event):
    target_pos[0] = event.x
    target_pos[1] = event.y

canvas.bind("<Motion>", on_mouse_move)

glide()
root.mainloop()