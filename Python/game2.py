import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import os
import time

def get_game_settings():
    root = tk.Tk()
    root.withdraw()  # Hide the root window for dialogs
    grid_size = simpledialog.askinteger("Grid Size", "Enter grid size (e.g. 10):", minvalue=2, maxvalue=20)
    if not grid_size:
        messagebox.showerror("Error", "Grid size is required!")
        root.destroy()
        exit()
    num_mines = simpledialog.askinteger("Mines", f"Enter number of mines (max {grid_size*grid_size-1}):", minvalue=1, maxvalue=grid_size*grid_size-1)
    if not num_mines:
        messagebox.showerror("Error", "Number of mines is required!")
        root.destroy()
        exit()
    root.destroy()
    return grid_size, num_mines

GRID_SIZE, NUM_MINES = get_game_settings()

def get_username():
    # First try active player written by the main menu to Python/name.txt
    name_path = os.path.join("Python", "name.txt")
    if os.path.exists(name_path):
        with open(name_path, "r", encoding="utf-8") as f:
            for line in f:
                ln = line.strip()
                if ln:
                    return ln
    # fallback to previous username.txt behavior
    filename = "Python/username.txt"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            if lines:
                last_line = lines[-1]
                if ":" in last_line:
                    return last_line.split(":")[0]
                return last_line
    return "guest"

def calculate_window_and_button_size(grid_size):
    # Default button size (pixels)
    default_btn_px = 40
    window_size = grid_size * default_btn_px
    if window_size > 1000:
        window_size = 1000
        btn_px = max(20, window_size // grid_size)
    else:
        btn_px = default_btn_px
    return window_size, btn_px

def save_game2_score(username, score):
    """
    Update only the game2_score field for the given username in username.txt.
    Preserve all other key=value pairs on that user's line.
    Only replace if new score > previous saved game2_score. If user not present, append.
    """
    filename = os.path.join(os.path.dirname(__file__), "username.txt")
    lines = []
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            lines = [ln.rstrip("\n") for ln in f.readlines()]

    found = False
    new_lines = []
    for line in lines:
        line_strip = line.strip()
        if not line_strip:
            continue
        if line_strip.startswith(username + ":"):
            # parse existing key=val pairs into dict
            existing = {}
            parts = line_strip.split(":", 1)
            if len(parts) > 1 and parts[1].strip():
                for part in parts[1].split(","):
                    if "=" in part:
                        k, v = part.split("=", 1)
                        existing[k.strip()] = v.strip()
            try:
                prev_score = int(existing.get("game2_score", "0"))
            except ValueError:
                prev_score = 0

            if score > prev_score:
                existing["game2_score"] = str(int(score))
            else:
                # keep previous score as-is
                existing["game2_score"] = str(prev_score)

            # rebuild line preserving other keys
            rest = ",".join(f"{k}={v}" for k, v in existing.items())
            new_lines.append(f"{username}:{rest}\n")
            found = True
        else:
            new_lines.append(line + ("\n" if not line.endswith("\n") else ""))

    if not found:
        new_lines.append(f"{username}:game2_score={int(score)}\n")

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


def save_game2_time(username, elapsed_time, grid_size, num_mines):
    """
    Update only game2_time, game2_grid, game2_mines fields for the given username.
    Preserve other key=value pairs. Replace (or set) these fields only if new time is lower (better)
    than existing game2_time, or if there is no existing time. If user not present, append.
    """
    filename = os.path.join(os.path.dirname(__file__), "username.txt")
    lines = []
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            lines = [ln.rstrip("\n") for ln in f.readlines()]

    found = False
    new_lines = []
    for line in lines:
        line_strip = line.strip()
        if not line_strip:
            continue
        if line_strip.startswith(username + ":"):
            # parse existing key=val pairs into dict
            existing = {}
            parts = line_strip.split(":", 1)
            if len(parts) > 1 and parts[1].strip():
                for part in parts[1].split(","):
                    if "=" in part:
                        k, v = part.split("=", 1)
                        existing[k.strip()] = v.strip()

            prev_time = None
            try:
                if "game2_time" in existing:
                    prev_time = int(existing["game2_time"])
            except ValueError:
                prev_time = None

            if prev_time is None or int(elapsed_time) < prev_time:
                existing["game2_time"] = str(int(elapsed_time))
                existing["game2_grid"] = str(int(grid_size))
                existing["game2_mines"] = str(int(num_mines))
            else:
                # keep existing time/grid/mines (or set grid/mines if missing)
                if "game2_grid" not in existing:
                    existing["game2_grid"] = str(int(grid_size))
                if "game2_mines" not in existing:
                    existing["game2_mines"] = str(int(num_mines))
                existing["game2_time"] = str(int(prev_time)) if prev_time is not None else str(int(elapsed_time))

            # rebuild line preserving other keys
            rest = ",".join(f"{k}={v}" for k, v in existing.items())
            new_lines.append(f"{username}:{rest}\n")
            found = True
        else:
            new_lines.append(line + ("\n" if not line.endswith("\n") else ""))

    if not found:
        new_lines.append(f"{username}:game2_time={int(elapsed_time)},game2_grid={int(grid_size)},game2_mines={int(num_mines)}\n")

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

def get_game2_score(username):
    # Retrieve the game2 score for the user
    filename = "Python/username.txt"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            for line in f:
                line_strip = line.strip()
                if line_strip.startswith(username + ":"):
                    parts = line_strip.split(":")
                    if len(parts) > 1:
                        for g in parts[1].split(","):
                            if g.startswith("game2_score="):
                                try:
                                    return int(g.split("=")[1])
                                except ValueError:
                                    return 0
    return 0

class MineSweeper:
    def __init__(self, master, username):
        self.master = master
        self.username = username
        self.score = get_game2_score(username)
        self.window_size, self.btn_px = calculate_window_and_button_size(GRID_SIZE)
        # Increase window height for timer/buttons
        self.master.geometry(f"{self.window_size}x{self.window_size+150}")
        self.timer_label = tk.Label(self.master, text="Time: 0s", font=("Arial", 12))
        self.timer_label.pack(pady=5)
        self.start_time = None
        self.elapsed_time = 0
        self.timer_running = False
        self.reset_game()

    def reset_game(self):
        self.buttons = {}
        self.mines = set(random.sample(range(GRID_SIZE * GRID_SIZE), NUM_MINES))
        self.revealed = set()
        self.game_over = False

        # Remove all widgets except timer label
        for widget in self.master.winfo_children():
            if widget != self.timer_label:
                widget.destroy()

        self.frame = tk.Frame(self.master)
        self.frame.pack()

        # Set grid minsize for proper scaling
        for r in range(GRID_SIZE):
            self.frame.grid_rowconfigure(r, minsize=self.btn_px)
        for c in range(GRID_SIZE):
            self.frame.grid_columnconfigure(c, minsize=self.btn_px)

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                idx = r * GRID_SIZE + c
                btn = tk.Button(
                    self.frame,
                    width=2,
                    height=1,
                    command=lambda idx=idx: self.reveal(idx)
                )
                btn.grid(row=r, column=c, sticky="nsew")
                self.buttons[idx] = btn

        # Place buttons at the bottom
        btn_frame = tk.Frame(self.master)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Restart", command=self.reset_game).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Exit", command=self.master.destroy).pack(side="left", padx=10)

        # Timer setup
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if self.timer_running:
            self.elapsed_time = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Time: {self.elapsed_time}s")
            self.master.after(1000, self.update_timer)

    def reveal(self, idx):
        # Ignore if game over or already revealed
        if self.game_over or idx in self.revealed:
            return
        self.revealed.add(idx)
        btn = self.buttons[idx]
        if idx in self.mines:
            btn.config(text="💣", bg="red")
            self.end_game(False)
        else:
            count = self.count_adjacent_mines(idx)
            btn.config(text=str(count) if count > 0 else "", bg="lightgrey")
            if self.check_win():
                self.end_game(True)

    def count_adjacent_mines(self, idx):
        r, c = divmod(idx, GRID_SIZE)
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                nidx = nr * GRID_SIZE + nc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and nidx in self.mines:
                    count += 1
        return count

    def check_win(self):
        # Check if all non-mine cells are revealed
        return len(self.revealed) == GRID_SIZE * GRID_SIZE - NUM_MINES

    def end_game(self, won):
        # If won, increment score and save time
        self.game_over = True
        self.timer_running = False
        for idx in self.mines:
            self.buttons[idx].config(text="💣", bg="red")
        if won:
            self.score += 1
            save_game2_score(self.username, self.score)
            save_game2_time(self.username, self.elapsed_time, GRID_SIZE, NUM_MINES)
            tk.messagebox.showinfo("Mine Sweeper", f"You win!\nTime: {self.elapsed_time}s")
        else:
            tk.messagebox.showinfo("Mine Sweeper", "You hit a mine! Game over.")

root = tk.Tk()
root.title("Mine Sweeper")
root.geometry("600x600")

username = get_username()
MineSweeper(root, username)

root.mainloop()
