import cv2
import pytesseract
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from tkinterdnd2 import TkinterDnD, DND_FILES
import copy
import time
import json

# Define the paths to tesseract.exe and the image
path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
image_save_path = r"C:\Users\shant\Pictures\Screenshots\captured_image.jpg"

# Set the path to your Tesseract executable
pytesseract.pytesseract.tesseract_cmd = path_to_tesseract

undo_stack = []
redo_stack = []
start_time = None
timer_label = None
theme = "light"

def capture_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Could not open webcam")
        return
    ret, frame = cap.read()
    cap.release()
    if ret:
        cv2.imwrite(image_save_path, frame)
        messagebox.showinfo("Success", "Image captured successfully")
        show_image(image_save_path)
    else:
        messagebox.showerror("Error", "Failed to capture image")

def show_image(image_path):
    try:
        image = Image.open(image_path)
        image = image.resize((400, 300), Image.Resampling.LANCZOS)
        image_tk = ImageTk.PhotoImage(image)
        image_label.config(image=image_tk)
        image_label.image = image_tk
    except Exception as e:
        messagebox.showerror("Error", str(e))

def preprocess_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    image = cv2.resize(image, (450, 450))
    image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return image

def extract_text(image_path):
    try:
        image = preprocess_image(image_path)
        custom_config = r'--oem 3 --psm 6'
        extracted_text = pytesseract.image_to_string(image, config=custom_config)
        
        extracted_text = ''.join(filter(str.isdigit, extracted_text))
        grid = []
        for i in range(0, len(extracted_text), 9):
            row = extracted_text[i:i+9]
            grid.append(' '.join(row))
        
        formatted_text = '\n'.join(grid)
        
        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, formatted_text)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def on_drop(event):
    image_path = event.data
    if image_path.startswith('{') and image_path.endswith('}'):
        image_path = image_path[1:-1]
    show_image(image_path)
    extract_text(image_path)

def upload_photo():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])
    if file_path:
        show_image(file_path)
        extract_text(file_path)

def create_sudoku_grid(root):
    entries = []
    for i in range(9):
        row_entries = []
        for j in range(9):
            entry = tk.Entry(root, width=2, font=('Arial', 18), justify='center')
            entry.grid(row=i, column=j, padx=5, pady=5)
            entry.bind("<KeyRelease>", lambda e, x=i, y=j: on_cell_change(e, x, y))
            row_entries.append(entry)
        entries.append(row_entries)
    return entries

def extract_numbers_from_grid(entries):
    board = []
    user_filled_cells = []
    for row_entries in entries:
        row = []
        user_filled_row = []
        for entry in row_entries:
            value = entry.get()
            if value == '':
                row.append('.')
                user_filled_row.append(False)
            else:
                row.append(value)
                user_filled_row.append(True)
        board.append(row)
        user_filled_cells.append(user_filled_row)
    return board, user_filled_cells

def is_valid(board, row, col, ch):
    for i in range(9):
        if board[i][col] == ch:
            return False
        if board[row][i] == ch:
            return False
        if board[3*(row//3)+i//3][3*(col//3)+i%3] == ch:
            return False
    return True

def solve(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == '.':
                for ch in '123456789':
                    if is_valid(board, i, j, ch):
                        board[i][j] = ch
                        if solve(board):
                            return True
                        board[i][j] = '.'
                return False
    return True

def solve_sudoku():
    global start_time
    board, user_filled_cells = extract_numbers_from_grid(entries)
    solve(board)
    for i in range(9):
        for j in range(9):
            entries[i][j].delete(0, tk.END)
            entries[i][j].insert(0, board[i][j])
            if user_filled_cells[i][j]:
                entries[i][j].config(bg='red' if not is_valid(board, i, j, board[i][j]) else 'white')
            else:
                entries[i][j].config(bg='green')
    end_time = time.time()
    elapsed_time = end_time - start_time
    timer_label.config(text=f"Time: {elapsed_time:.2f} seconds")

def insert_numbers():
    global entries, start_time, timer_label
    if insert_button.config('relief')[-1] == 'sunken':
        insert_button.config(relief="raised")
        for widget in sudoku_frame.winfo_children():
            widget.destroy()
        submit_button.pack_forget()
        timer_label.pack_forget()
    else:
        insert_button.config(relief="sunken")
        entries = create_sudoku_grid(sudoku_frame)
        submit_button.pack(pady=10)
        start_time = time.time()
        timer_label = tk.Label(scrollable_frame, font=("Arial", 14))
        timer_label.pack(pady=10)

def on_cell_change(event, row, col):
    board_snapshot, _ = extract_numbers_from_grid(entries)
    undo_stack.append(copy.deepcopy(board_snapshot))
    redo_stack.clear()

def undo():
    if undo_stack:
        board_snapshot = undo_stack.pop()
        redo_stack.append(copy.deepcopy(board_snapshot))
        for i in range(9):
            for j in range(9):
                entries[i][j].delete(0, tk.END)
                if board_snapshot[i][j] != '.':
                    entries[i][j].insert(0, board_snapshot[i][j])
def redo():
    if redo_stack:
        board_snapshot = redo_stack.pop()
        undo_stack.append(copy.deepcopy(board_snapshot))
        for i in range(9):
            for j in range(9):
                entries[i][j].delete(0, tk.END)
                if board_snapshot[i][j] != '.':
                    entries[i][j].insert(0, board_snapshot[i][j])

def save_progress():
    board, user_filled_cells = extract_numbers_from_grid(entries)
    progress = {
        "board": board,
        "user_filled_cells": user_filled_cells,
        "start_time": start_time,
        "theme": theme
    }
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if file_path:
        with open(file_path, "w") as file:
            json.dump(progress, file)
        messagebox.showinfo("Success", "Progress saved successfully.")

def load_progress():
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if file_path:
        with open(file_path, "r") as file:
            progress = json.load(file)
        board = progress["board"]
        user_filled_cells = progress["user_filled_cells"]
        global start_time, theme
        start_time = progress["start_time"]
        theme = progress["theme"]
        switch_theme(theme)
        for i in range(9):
            for j in range(9):
                entries[i][j].delete(0, tk.END)
                if board[i][j] != '.':
                    entries[i][j].insert(0, board[i][j])
                if user_filled_cells[i][j]:
                    entries[i][j].config(bg='red' if not is_valid(board, i, j, board[i][j]) else 'white')
                else:
                    entries[i][j].config(bg='green')

def show_hint():
    board, user_filled_cells = extract_numbers_from_grid(entries)
    for i in range(9):
        for j in range(9):
            if board[i][j] == '.':
                for ch in '123456789':
                    if is_valid(board, i, j, ch):
                        entries[i][j].delete(0, tk.END)
                        entries[i][j].insert(0, ch)
                        messagebox.showinfo("Hint", f"The correct number in row {i+1}, column {j+1} is {ch}.")
                        return

def switch_theme(new_theme):
    global theme
    theme = new_theme
    if theme == "dark":
        root.config(bg="black", fg="white")
        canvas_frame.config(bg="black")
        scrollable_frame.config(bg="black")
        button_frame.config(bg="black")
        option_frame.config(bg="black")
        sudoku_frame.config(bg="black")
        for widget in root.winfo_children():
            widget.config(bg="black", fg="white")
    else:
        root.config(bg="white", fg="black")
        canvas_frame.config(bg="white")
        scrollable_frame.config(bg="white")
        button_frame.config(bg="white")
        option_frame.config(bg="white")
        sudoku_frame.config(bg="white")
        for widget in root.winfo_children():
            widget.config(bg="white", fg="black")

def set_difficulty():
    difficulty = simpledialog.askinteger("Set Difficulty", "Enter the difficulty level (1-5):", minvalue=1, maxvalue=5)
    if difficulty:
        # Load the corresponding Sudoku puzzle based on the difficulty level
        pass

root = TkinterDnD.Tk()
root.title("OCR Scanner")

canvas_frame = tk.Frame(root)
canvas_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(canvas_frame)
scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

button_frame = tk.Frame(scrollable_frame)
button_frame.pack(pady=10)

capture_button = tk.Button(button_frame, text="Capture Image", command=capture_image)
capture_button.pack(side=tk.LEFT, padx=5)

upload_button = tk.Button(button_frame, text="Upload Photo", command=upload_photo)
upload_button.pack(side=tk.LEFT, padx=5)

insert_button = tk.Button(button_frame, text="Insert Number", command=insert_numbers)
insert_button.pack(side=tk.LEFT, padx=5)

extract_button = tk.Button(button_frame, text="Extract Text", command=lambda: extract_text(image_save_path))
extract_button.pack(side=tk.LEFT, padx=5)

undo_button = tk.Button(button_frame, text="Undo", command=undo)
undo_button.pack(side=tk.LEFT, padx=5)

redo_button = tk.Button(button_frame, text="Redo", command=redo)
redo_button.pack(side=tk.LEFT, padx=5)

save_button = tk.Button(button_frame, text="Save Progress", command=save_progress)
save_button.pack(side=tk.LEFT, padx=5)

# load_button = tk.Button(button_frame, text="Load Progress", command=load_progress)
# load_button.pack(side=tk.LEFT, padx=5)

hint_button = tk.Button(button_frame, text="Hint", command=show_hint)
hint_button.pack(side=tk.LEFT, padx=5)

# difficulty_button = tk.Button(button_frame, text="Set Difficulty", command=set_difficulty)
# difficulty_button.pack(side=tk.LEFT, padx=5)

theme_button = tk.Button(button_frame, text="Switch Theme", command=lambda: switch_theme("dark" if theme == "light" else "light"))
theme_button.pack(side=tk.LEFT, padx=5)

option_frame = tk.Frame(scrollable_frame)
option_frame.pack(pady=10)

extract_option = tk.StringVar(value="text")
text_radio = tk.Radiobutton(option_frame, text="Text", variable=extract_option, value="text")
text_radio.pack(side=tk.LEFT, padx=5)

number_radio = tk.Radiobutton(option_frame, text="Number", variable=extract_option, value="number")
number_radio.pack(side=tk.LEFT, padx=5)

sudoku_frame = tk.Frame(scrollable_frame)
sudoku_frame.pack(pady=10)

submit_button = tk.Button(scrollable_frame, text="Submit", command=solve_sudoku)

image_label = tk.Label(scrollable_frame)
image_label.pack(pady=10)

text_box = tk.Text(scrollable_frame, height=20, width=50)
text_box.pack(pady=10)

root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>'), on_drop

root.mainloop()
