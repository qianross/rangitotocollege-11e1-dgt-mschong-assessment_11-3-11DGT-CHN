import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import os
import time
import sys

BASE_DIR = os.path.dirname(__file__)
NAME_FILE = os.path.join(BASE_DIR, "name.txt")
USERNAME_FILE = os.path.join(BASE_DIR, "username.txt")

# safe defaults so importing module won't open dialogs
GRID_SIZE = 10
NUM_MINES = 10

def get_game_settings():
    # ask user for grid size and mines (only called at runtime)
    root = tk.Tk()
    root.withdraw()
    grid_size = simpledialog.askinteger("Grid Size", "Enter grid size (e.g. 10):", minvalue=2, maxvalue=30)
    if not grid_size:
        messagebox.showerror("Error", "Grid size is required!")
        root.destroy()
        raise SystemExit
    max_mines = max(1, grid_size * grid_size - 1)
    num_mines = simpledialog.askinteger("Mines", f"Enter number of mines (max {max_mines}):",
                                        minvalue=1, maxvalue=max_mines)
    if not num_mines:
        messagebox.showerror("Error", "Number of mines is required!")
        root.destroy()
        raise SystemExit
    root.destroy()
    return grid_size, num_mines

def get_username():
    # return active name from name.txt or last username entry
    if os.path.exists(NAME_FILE):
        with open(NAME_FILE, "r", encoding="utf-8") as f:
            for line in f:
                ln = line.strip()
                if ln:
                    return ln
    if os.path.exists(USERNAME_FILE):
        with open(USERNAME_FILE, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
            if lines:
                last_line = lines[-1]
                if ":" in last_line:
                    return last_line.split(":", 1)[0].strip()
                return last_line
    return "guest"

def calculate_window_and_button_size(grid_size):
    # pick window size and button px based on grid size
    default_btn_px = 40
    window_size = grid_size * default_btn_px
    if window_size > 1000:
        window_size = 1000
        btn_px = max(20, window_size // grid_size)
    else:
        btn_px = default_btn_px
    return window_size, btn_px

# file helpers for username.txt
def read_user_lines():
    # read username file lines, return list
    if not os.path.exists(USERNAME_FILE):
        return []
    with open(USERNAME_FILE, "r", encoding="utf-8") as f:
        return [ln.rstrip("\n") for ln in f.readlines()]

def write_user_lines(lines):
    # write normalized lines back to file
    os.makedirs(BASE_DIR, exist_ok=True)
    with open(USERNAME_FILE, "w", encoding="utf-8") as f:
        f.writelines(line if line.endswith("\n") else line + "\n" for line in lines)

def parse_pairs(rest):
    # parse comma separated k=v pairs into dict
    pairs = {}
    for part in rest.split(","):
        if "=" in part:
            k, v = part.split("=", 1)
            pairs[k.strip()] = v.strip()
    return pairs

def save_game2_score(username, score):
    # update only game2_score for user, keep other keys
    lines = read_user_lines()
    found = False
    out = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(username + ":"):
            found = True
            parts = stripped.split(":", 1)
            existing = parse_pairs(parts[1]) if len(parts) > 1 else {}
            try:
                prev = int(existing.get("game2_score", "0"))
            except ValueError:
                prev = 0
            if score > prev:
                existing["game2_score"] = str(int(score))
            else:
                existing["game2_score"] = str(prev)
            rest = ",".join(f"{k}={v}" for k, v in existing.items())
            out.append(f"{username}:{rest}")
        else:
            out.append(line)
    if not found:
        out.append(f"{username}:game2_score={int(score)}")
    write_user_lines(out)

def save_game2_time(username, elapsed_time, grid_size, num_mines):
    # update best time, grid, mines for game2 (lower time is better)
    lines = read_user_lines()
    found = False
    out = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(username + ":"):
            found = True
            parts = stripped.split(":", 1)
            existing = parse_pairs(parts[1]) if len(parts) > 1 else {}
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
                # keep old time, but make sure grid/mines exist
                existing.setdefault("game2_grid", str(int(grid_size)))
                existing.setdefault("game2_mines", str(int(num_mines)))
                existing["game2_time"] = str(int(prev_time)) if prev_time is not None else str(int(elapsed_time))
            rest = ",".join(f"{k}={v}" for k, v in existing.items())
            out.append(f"{username}:{rest}")
        else:
            out.append(line)
    if not found:
        out.append(f"{username}:game2_time={int(elapsed_time)},game2_grid={int(grid_size)},game2_mines={int(num_mines)}")
    write_user_lines(out)

def get_game2_score(username):
    # read saved game2_score for username, return 0 if not found
    if os.path.exists(USERNAME_FILE):
        with open(USERNAME_FILE, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith(username + ":"):
                    parts = stripped.split(":", 1)
                    if len(parts) > 1:
                        for g in parts[1].split(","):
                            if g.startswith("game2_score="):
                                try:
                                    return int(g.split("=", 1)[1])
                                except ValueError:
                                    return 0
    return 0

class MineSweeper:
    def __init__(self, master, username):
        # setup UI and state
        self.master = master
        self.username = username
        self.score = get_game2_score(username)
        self.window_size, self.btn_px = calculate_window_and_button_size(GRID_SIZE)
        self.master.geometry(f"{self.window_size}x{self.window_size+150}")
        self.timer_label = tk.Label(self.master, text="Time: 0s", font=("Arial", 12))
        self.timer_label.pack(pady=5)
        self.start_time = None
        self.elapsed_time = 0
        self.timer_running = False
        self.reset_game()

    def reset_game(self):
        # create grid buttons and mines
        self.buttons = {}
        self.mines = set(random.sample(range(GRID_SIZE * GRID_SIZE), NUM_MINES))
        self.revealed = set()
        self.game_over = False

        for widget in self.master.winfo_children():
            if widget != self.timer_label:
                widget.destroy()

        self.frame = tk.Frame(self.master)
        self.frame.pack()

        for r in range(GRID_SIZE):
            self.frame.grid_rowconfigure(r, minsize=self.btn_px)
        for c in range(GRID_SIZE):
            self.frame.grid_columnconfigure(c, minsize=self.btn_px)

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                idx = r * GRID_SIZE + c
                btn = tk.Button(self.frame, width=2, height=1, command=lambda idx=idx: self.reveal(idx))
                btn.grid(row=r, column=c, sticky="nsew")
                self.buttons[idx] = btn

        btn_frame = tk.Frame(self.master)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Restart", command=self.reset_game).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Exit", command=self.master.destroy).pack(side="left", padx=10)

        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        # update elapsed time label
        if self.timer_running:
            self.elapsed_time = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Time: {self.elapsed_time}s")
            self.master.after(1000, self.update_timer)

    def reveal(self, idx):
        # reveal a cell, end game on mine
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
        # count mines around a cell
        r, c = divmod(idx, GRID_SIZE)
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                nidx = nr * GRID_SIZE + nc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and nidx in self.mines:
                    count += 1
        return count

    def check_win(self):
        # win if all non-mine cells revealed
        return len(self.revealed) == GRID_SIZE * GRID_SIZE - NUM_MINES

    def end_game(self, won):
        # show bombs and save results if win
        self.game_over = True
        self.timer_running = False
        for idx in self.mines:
            self.buttons[idx].config(text="💣", bg="red")
        if won:
            self.score += 1
            save_game2_score(self.username, self.score)
            save_game2_time(self.username, self.elapsed_time, GRID_SIZE, NUM_MINES)
            messagebox.showinfo("Mine Sweeper", f"You win!\nTime: {self.elapsed_time}s")
        else:
            messagebox.showinfo("Mine Sweeper", "You hit a mine! Game over.")

if __name__ == "__main__":
    # get settings at runtime to avoid dialogs on import
    try:
        GRID_SIZE, NUM_MINES = get_game_settings()
    except SystemExit:
        # user cancelled, exit cleanly
        sys.exit(0)

    root = tk.Tk()
    root.title("Minesweeper")
    # set a sensible minimum window size
    win_w = min(800, GRID_SIZE * 40)
    win_h = min(800, GRID_SIZE * 40 + 150)
    root.geometry(f"{win_w}x{win_h}")
    username = get_username()
    app = MineSweeper(root, username)
    root.mainloop()
