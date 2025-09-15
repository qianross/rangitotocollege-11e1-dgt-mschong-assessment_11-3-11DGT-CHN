import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import os

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
    python_folder = os.path.dirname(__file__)
    username_path = os.path.join(python_folder, "username.txt")
    if os.path.exists(username_path):
        with open(username_path, "r") as f:
            return f.read().strip()
    return "guest"

def get_score(username):
    python_folder = os.path.dirname(__file__)
    filename = os.path.join(python_folder, f"minesweeper_score_{username}.txt")
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return int(f.read().strip())
    return 0

def save_score(username, score):
    python_folder = os.path.dirname(__file__)
    filename = os.path.join(python_folder, f"minesweeper_score_{username}.txt")
    with open(filename, "w") as f:
        f.write(str(score))

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

class MineSweeper:
    def __init__(self, master, username):
        self.master = master
        self.username = username
        self.score = get_score(username)
        self.window_size, self.btn_px = calculate_window_and_button_size(GRID_SIZE)
        self.master.geometry(f"{self.window_size}x{self.window_size+100}")
        self.reset_game()

    def reset_game(self):
        self.buttons = {}
        self.mines = set(random.sample(range(GRID_SIZE * GRID_SIZE), NUM_MINES))
        self.revealed = set()
        self.game_over = False

        for widget in self.master.winfo_children():
            widget.destroy()

        tk.Label(
            self.master,
            text=f"Welcome, {self.username}! | Wins: {self.score}",
            font=("Arial", 12)
        ).pack(pady=5)
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
                    width=2,  # width in text units, keep small for scaling
                    height=1, # height in text units
                    command=lambda idx=idx: self.reveal(idx)
                )
                btn.grid(row=r, column=c, sticky="nsew")
                self.buttons[idx] = btn

        tk.Button(self.master, text="Restart", command=self.reset_game).pack(pady=5)
        tk.Button(self.master, text="Exit", command=self.master.destroy).pack(pady=5)

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
        for idx in self.mines:
            self.buttons[idx].config(text="💣", bg="red")
        if won:
            self.score += 1
            save_score(self.username, self.score)
            tk.messagebox.showinfo("Mine Sweeper", "You win!")
        else:
            tk.messagebox.showinfo("Mine Sweeper", "You hit a mine! Game over.")

root = tk.Tk()
root.title("Mine Sweeper")
root.geometry("600x600")

username = get_username()
MineSweeper(root, username)

root.mainloop()
