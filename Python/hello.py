import tkinter as tk
from PIL import Image, ImageTk
import random

WIDTH, HEIGHT = 512, 512
CIRCLE_RADIUS = 40

root = tk.Tk()
root.title("Spotlight")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, highlightthickness=0)
canvas.pack()

# Generate static noise texture
def generate_noise_image(width, height):
    image = Image.new("RGB", (width, height))
    pixels = image.load()
    for x in range(width):
        for y in range(height):
            gray = random.randint(0, 255)
            pixels[x, y] = (gray, gray, gray)
    return image

# Create and display noise background
noise_image = generate_noise_image(WIDTH, HEIGHT)
noise_photo = ImageTk.PhotoImage(noise_image)
# Keep a reference to avoid garbage collection
canvas.noise_photo = noise_photo
canvas.create_image(0, 0, image=noise_photo, anchor=tk.NW, tags="background")

circle_pos = [WIDTH // 2, HEIGHT // 2]
target_pos = [WIDTH // 2, HEIGHT // 2]

def draw_spotlight():
    canvas.delete("spotlight")
    cx, cy = int(circle_pos[0]), int(circle_pos[1])
    canvas.create_oval(
        cx - CIRCLE_RADIUS, cy - CIRCLE_RADIUS,
        cx + CIRCLE_RADIUS, cy + CIRCLE_RADIUS,
        fill="white", outline="", tags="spotlight"
    )

def glide():
    speed = 0.2
    dx = target_pos[0] - circle_pos[0]
    dy = target_pos[1] - circle_pos[1]
    if abs(dx) > 1 or abs(dy) > 1:
        circle_pos[0] += dx * speed
        circle_pos[1] += dy * speed
        draw_spotlight()
    root.after(24, glide)

def on_mouse_move(event):
    target_pos[0] = event.x
    target_pos[1] = event.y

canvas.bind("<Motion>", on_mouse_move)

draw_spotlight()
glide()

root.mainloop()