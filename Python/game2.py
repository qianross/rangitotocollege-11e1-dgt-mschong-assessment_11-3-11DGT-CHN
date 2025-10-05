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
    filename = "Python/username.txt"
    if os.path.exists(filename):
        with open(filename, "r") as f:
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
    filename = "Python/username.txt"
    lines = []
    if os.path.exists(filename):
        with open(filename, "r") as f:
            lines = f.readlines()
    found = False
    new_lines = []
    for line in lines:
        line_strip = line.strip()
        if line_strip.startswith(username + ":"):
            parts = line_strip.split(":")
            if len(parts) > 1:
                games = [g for g in parts[1].split(",") if not g.startswith("game2_score=")]
                prev_score = 0
                for g in parts[1].split(","):
                    if g.startswith("game2_score="):
                        try:
                            prev_score = int(g.split("=")[1])
                        except ValueError:
                            prev_score = 0
                # Only update if new score is higher
                if score > prev_score:
                    games.append(f"game2_score={score}")
                else:
                    games.append(f"game2_score={prev_score}")
                new_line = f"{username}:{','.join(games)}\n"
            else:
                new_line = f"{username}:game2_score={score}\n"
            new_lines.append(new_line)
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f"{username}:game2_score={score}\n")
    with open(filename, "w") as f:
        f.writelines(new_lines)

def save_game2_time(username, elapsed_time, grid_size, num_mines):
    filename = "Python/username.txt"
    lines = []
    if os.path.exists(filename):
        with open(filename, "r") as f:
            lines = f.readlines()
    found = False
    new_lines = []
    for line in lines:
        line_strip = line.strip()
        if line_strip.startswith(username + ":"):
            parts = line_strip.split(":")
            if len(parts) > 1:
                games = [g for g in parts[1].split(",") if not g.startswith("game2_time=") and not g.startswith("game2_grid=") and not g.startswith("game2_mines=")]
                prev_time = None
                for g in parts[1].split(","):
                    if g.startswith("game2_time="):
                        try:
                            prev_time = int(g.split("=")[1])
                        except ValueError:
                            prev_time = None
                # Only update if new time is better (lower)
                if prev_time is None or elapsed_time < prev_time:
                    games.append(f"game2_time={elapsed_time}")
                    games.append(f"game2_grid={grid_size}")
                    games.append(f"game2_mines={num_mines}")
                else:
                    games.append(f"game2_time={prev_time}")
                    # Find previous grid size if exists
                    prev_grid = None
                    for g in parts[1].split(","):
                        if g.startswith("game2_grid="):
                            prev_grid = g.split("=")[1]
                    if prev_grid is not None:
                        games.append(f"game2_grid={prev_grid}")
                    # Find previous mines if exists
                    prev_mines = None
                    for g in parts[1].split(","):
                        if g.startswith("game2_mines="):
                            prev_mines = g.split("=")[1]
                    if prev_mines is not None:
                        games.append(f"game2_mines={prev_mines}")
                new_line = f"{username}:{','.join(games)}\n"
            else:
                new_line = f"{username}:game2_time={elapsed_time},game2_grid={grid_size},game2_mines={num_mines}\n"
            new_lines.append(new_line)
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f"{username}:game2_time={elapsed_time},game2_grid={grid_size},game2_mines={num_mines}\n")
    with open(filename, "w") as f:
        f.writelines(new_lines)

def get_game2_score(username):
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
        self.score = get_game2_score(username)  # <-- FIXED
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

        # Remove the welcome label
        # tk.Label(
        #     self.master,
        #     text=f"Welcome, {self.username}! | Wins: {self.score}",
        #     font=("Arial", 12)
        # ).pack(pady=5)

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
        return len(self.revealed) == GRID_SIZE * GRID_SIZE - NUM_MINES

    def end_game(self, won):
        self.game_over = True
        self.timer_running = False
        for idx in self.mines:
            self.buttons[idx].config(text="💣", bg="red")
        if won:
            self.score += 1
            save_game2_score(self.username, self.score)  # <-- FIXED
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
