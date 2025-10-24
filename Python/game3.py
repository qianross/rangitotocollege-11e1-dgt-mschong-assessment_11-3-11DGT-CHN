import tkinter as tk
from tkinter import messagebox
import random
import time
import os
import sys

BASE_DIR = os.path.dirname(__file__)
USERNAME_FILE = os.path.join(BASE_DIR, "username.txt")
NAME_FILE = os.path.join(BASE_DIR, "name.txt")

CELL = 20
COLUMNS = 20
ROWS = 20
WIDTH = CELL * COLUMNS
HEIGHT = CELL * ROWS
UPDATE_MS = 120

def read_user_lines():
    # return list of non-empty lines from username file
    if not os.path.exists(USERNAME_FILE):
        return []
    with open(USERNAME_FILE, "r", encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f if line.strip()]

def write_user_lines(lines):
    # write lines back, make sure file and newline are ok
    os.makedirs(BASE_DIR, exist_ok=True)
    with open(USERNAME_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + ("\n" if lines else ""))

def get_username():
    # try name.txt first, return first non-empty line
    if os.path.exists(NAME_FILE):
        with open(NAME_FILE, "r", encoding="utf-8") as nf:
            for line in nf:
                ln = line.strip()
                if ln:
                    return ln
    # none found -> return empty
    return ""

def ensure_user_exists(name):
    # add "name:" line if it's missing
    lines = read_user_lines()
    for line in lines:
        if ":" in line and line.split(":", 1)[0].strip() == name:
            return
    lines.append(f"{name}:")
    write_user_lines(lines)

def update_game3_score(name, score, time_seconds):
    # update only game3 and game3_time for the user
    lines = read_user_lines()
    found = False
    out = []
    for line in lines:
        line_strip = line.strip()
        if not line_strip:
            continue
        if line_strip.startswith(name + ":"):
            found = True
            parts = line_strip.split(":", 1)
            existing = {}
            if len(parts) > 1 and parts[1].strip():
                for part in parts[1].split(","):
                    if "=" in part:
                        k, v = part.split("=", 1)
                        existing[k.strip()] = v.strip()
            try:
                prev_score = int(existing.get("game3", "0"))
            except Exception:
                prev_score = 0
            if score > prev_score:
                existing["game3"] = str(int(score))
                existing["game3_time"] = str(int(time_seconds))
            else:
                # keep old score if it's better, ensure keys exist
                existing.setdefault("game3", str(prev_score))
                existing.setdefault("game3_time", str(int(time_seconds)))
            rest = ",".join(f"{k}={v}" for k, v in existing.items())
            out.append(f"{name}:{rest}")
        else:
            out.append(line_strip)
    if not found:
        out.append(f"{name}:game3={int(score)},game3_time={int(time_seconds)}")
    write_user_lines(out)

def get_last_username():
    # return username from last line of file
    lines = read_user_lines()
    if not lines:
        return ""
    last = lines[-1]
    if ":" in last:
        return last.split(":", 1)[0].strip()
    return last.strip()

class SnakeGame:
    def __init__(self, master, initial_username=""):
        self.master = master
        master.title("Snake")
        master.resizable(False, False)

        self.menu_frame = tk.Frame(master)
        self.menu_frame.pack(fill="both", expand=True)

        tk.Label(self.menu_frame, text="Snake", font=("Arial", 18)).pack(pady=10)

        # determine active player name
        self.active_name = initial_username or get_username() or get_last_username() or "Guest"

        # simple menu with start and exit
        btn_frame = tk.Frame(self.menu_frame)
        btn_frame.pack(pady=30)
        tk.Button(btn_frame, text="Start Game", width=16, height=2, command=self.start_game).grid(row=0, column=0, padx=10, pady=5)
        tk.Button(btn_frame, text="Exit", width=16, height=2, command=self.master.quit).grid(row=0, column=1, padx=10, pady=5)

        # game UI (hidden until start)
        self.game_frame = tk.Frame(master)
        self.top_label = tk.Label(self.game_frame, text="", font=("Arial", 12))
        self.top_label.pack(anchor="nw", padx=6, pady=6)
        self.canvas = tk.Canvas(self.game_frame, width=WIDTH, height=HEIGHT, bg="black")
        self.canvas.pack()
        bottom_frame = tk.Frame(self.game_frame)
        bottom_frame.pack(fill="x", pady=6)
        tk.Button(bottom_frame, text="Exit to Menu", command=self.exit_to_menu).pack(side="left", padx=10)
        tk.Button(bottom_frame, text="Quit", command=self.master.quit).pack(side="right", padx=10)

        # game state
        self.running = False
        self.reset_game_state()

        # controls
        master.bind("<Up>", lambda e: self.change_dir("Up"))
        master.bind("<Down>", lambda e: self.change_dir("Down"))
        master.bind("<Left>", lambda e: self.change_dir("Left"))
        master.bind("<Right>", lambda e: self.change_dir("Right"))

    def reset_game_state(self):
        # reset snake, direction, food, score
        self.snake = [(COLUMNS//2, ROWS//2), (COLUMNS//2-1, ROWS//2)]
        self.direction = "Right"
        self.next_direction = "Right"
        self.food = self.place_food()
        self.score = 0
        self.start_time = None

    def place_food(self):
        # pick random empty cell for food
        while True:
            p = (random.randint(0, COLUMNS-1), random.randint(0, ROWS-1))
            if p not in self.snake:
                return p

    def start_game(self):
        # start game, make sure user exists in file
        self.username = self.active_name
        ensure_user_exists(self.username)
        self.menu_frame.pack_forget()
        self.game_frame.pack(fill="both", expand=True)
        self.reset_game_state()
        self.running = True
        self.start_time = time.time()
        self.update()

    def exit_to_menu(self):
        # stop game and save score/time if running
        if self.running:
            elapsed = time.time() - self.start_time if self.start_time else 0
            update_game3_score(self.username, self.score, elapsed)
        self.running = False
        self.game_frame.pack_forget()
        self.menu_frame.pack(fill="both", expand=True)

    def change_dir(self, dir):
        # change direction unless it's the opposite
        opposites = {"Up":"Down","Down":"Up","Left":"Right","Right":"Left"}
        if self.running and dir != opposites.get(self.direction):
            self.next_direction = dir

    def update(self):
        # main game loop tick
        if not self.running:
            return
        elapsed = int(time.time() - self.start_time)
        # move snake head
        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        if self.direction == "Up":
            head_y -= 1
        elif self.direction == "Down":
            head_y += 1
        elif self.direction == "Left":
            head_x -= 1
        elif self.direction == "Right":
            head_x += 1
        new_head = (head_x, head_y)

        # collision with wall or self -> game over
        if (head_x < 0 or head_x >= COLUMNS or head_y < 0 or head_y >= ROWS) or (new_head in self.snake):
            self.game_over()
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 10
            self.food = self.place_food()
        else:
            self.snake.pop()

        self.draw_game(elapsed)
        self.master.after(UPDATE_MS, self.update)

    def draw_game(self, elapsed_seconds):
        # draw food and snake, update top label
        self.canvas.delete("all")
        fx, fy = self.food
        self.canvas.create_rectangle(fx*CELL, fy*CELL, (fx+1)*CELL, (fy+1)*CELL, fill="red", outline="darkred")
        for i, (x, y) in enumerate(self.snake):
            color = "lime" if i == 0 else "green"
            self.canvas.create_rectangle(x*CELL, y*CELL, (x+1)*CELL, (y+1)*CELL, fill=color, outline="black")
        mins = elapsed_seconds // 60
        secs = elapsed_seconds % 60
        time_str = f"Time: {mins:02d}:{secs:02d}"
        score_str = f"Score: {self.score}"
        self.top_label.config(text=f"{time_str}    {score_str}    Player: {self.username}")

    def game_over(self):
        # stop and save score, then show message
        self.running = False
        elapsed = time.time() - self.start_time if self.start_time else 0
        update_game3_score(self.username, self.score, elapsed)
        messagebox.showinfo("Game Over", f"Game Over!\nScore: {self.score}\nTime: {int(elapsed)}s")
        self.game_frame.pack_forget()
        self.menu_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    initial_user = sys.argv[1] if len(sys.argv) > 1 else ""
    app = SnakeGame(root, initial_username=initial_user)
    root.mainloop()
