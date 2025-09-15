import tkinter as tk
from tkinter import simpledialog, messagebox
import subprocess
import os

def save_username(name):
    with open("Python/username.txt", "w") as f:
        f.write(name)

def get_username():
    if os.path.exists("Python/username.txt"):
        with open("Python/username.txt", "r") as f:
            return f.read().strip()
    return None

def ask_username():
    name = simpledialog.askstring("Enter Name", "Please enter your name:")
    if name:
        save_username(name)
        return name
    else:
        messagebox.showerror("Error", "Name is required!")
        root.destroy()

def open_leaderboard():
    leaderboard = tk.Toplevel(root)
    leaderboard.title("Leaderboard")
    leaderboard.geometry("300x200")
    tk.Label(leaderboard, text="Leaderboard (placeholder)").pack(pady=20)

def launch_game(filename):
    subprocess.Popen(["python", filename])

root = tk.Tk()
root.title("Main Menu")
root.geometry("400x300")

username = get_username()
if not username:
    username = ask_username()

tk.Label(root, text=f"Welcome, {username}!", font=("Arial", 16)).pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=30)

btn1 = tk.Button(frame, text="Leaderboard", width=20, height=3, command=open_leaderboard)
btn1.grid(row=0, column=0, padx=10, pady=10)

btn2 = tk.Button(frame, text="Game 1", width=20, height=3, command=lambda: launch_game("Python\game1.py"))
btn2.grid(row=0, column=1, padx=10, pady=10)

btn3 = tk.Button(frame, text="Game 2", width=20, height=3, command=lambda: launch_game("Python\game2.py"))
btn3.grid(row=1, column=0, padx=10, pady=10)

btn4 = tk.Button(frame, text="Game 3", width=20, height=3, command=lambda: launch_game("Python\game3.py"))
btn4.grid(row=1, column=1, padx=10, pady=10)

root.mainloop()