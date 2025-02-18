import cv2
import pytesseract
import os
import sys
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
import pyperclip
import pyttsx3
import threading

# Variables
is_paused = False
stop_requested = False
engine = pyttsx3.init()

# Process Image and Extract Text
def process_image():
    global is_paused, stop_requested

    file_path = filedialog.askopenfilename(
        title="Select Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")])
    if not file_path:
        return

    try:
        image = cv2.imread(file_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        text = pytesseract.image_to_string(gray)
        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, text)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = image.resize((400, 400))
        img_tk = ImageTk.PhotoImage(image)
        image_display.config(image=img_tk, width=400, height=400)
        image_display.image = img_tk

        image_caption.config(text="Captured Image")

        is_paused = False
        stop_requested = False

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Copy text to clipboard
def copy_to_clipboard():
    text = text_output.get(1.0, tk.END).strip()
    if text:
        pyperclip.copy(text)
        messagebox.showinfo("Copied", "Text copied to clipboard!")
    else:
        messagebox.showwarning("Warning", "No text to copy!")

# Convert text to speech
def start_speech():
    global is_paused, stop_requested

    text = text_output.get(1.0, tk.END).strip()
    if not text:
        messagebox.showwarning("Warning", "No text to read aloud!")
        return

    try:
        stop_requested = False
        is_paused = False

        # Set voice properties
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1)

        threading.Thread(target=speak_text, args=(text,), daemon=True).start()

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Speak text in a thread
def speak_text(text):
    global is_paused, stop_requested

    words = text.split()
    chunk_size = 5  # Adjust chunk size as needed (number of words per chunk)
    for i in range(0, len(words), chunk_size):
        if stop_requested:
            break
        while is_paused:
            pass
        chunk = " ".join(words[i:i+chunk_size])  # Join a chunk of words
        engine.say(chunk)
        engine.runAndWait()
# Pause the speech
def pause_speech():
    global is_paused
    is_paused = True

# Resume the speech
def resume_speech():
    global is_paused
    is_paused = False

# Stop the speech
def stop_speech():
    global stop_requested
    stop_requested = True
    engine.stop()

# Close Application
def on_closing():
    root.quit()

# GUI Setup
root = tk.Tk()
root.title("Image to Text")
root.state('zoomed')
root.protocol("WM_DELETE_WINDOW", on_closing)
root.config(bg="#E0F7FA")

image_path = "./logo.jpg"
title_image = Image.open(image_path)
title_image = title_image.resize((300, 300))
title_img_tk = ImageTk.PhotoImage(title_image)
title_label = tk.Label(root, image=title_img_tk, bg="#E0F7FA")
title_label.image = title_img_tk
title_label.pack(pady=20)

button_style = {
    "font": ("Helvetica", 12, "bold"),
    "fg": "white",
    "bg": "#00796B",
    "relief": "flat",
    "bd": 0,
    "width": 20,
    "height": 2,
    "activebackground": "#004D40"
}

select_button = tk.Button(root, text="Choose Image", command=process_image, **button_style)
select_button.pack(pady=10)

side_by_side_frame = tk.Frame(root, bg="#E0F7FA")
side_by_side_frame.pack(pady=20)

image_frame = tk.Frame(side_by_side_frame, bg="#E0F7FA")
image_frame.pack(side=tk.LEFT, padx=20)

image_display = tk.Label(image_frame, bg="#E0F7FA", width=50, height=25)
image_display.pack()

image_caption = tk.Label(image_frame, text="Captured Image", font=("Helvetica", 14), bg="#E0F7FA", fg="#00796B")
image_caption.pack(pady=5)

text_frame = tk.Frame(side_by_side_frame, bg="#E0F7FA")
text_frame.pack(side=tk.LEFT, padx=20)

text_output = tk.Text(text_frame, wrap=tk.WORD, width=50, height=22, font=("Helvetica", 12), bg="#ffffff", fg="black")
text_output.pack()

converted_text_label = tk.Label(text_frame, text="Converted Text", font=("Helvetica", 14), bg="#E0F7FA", fg="#00796B")
converted_text_label.pack()

bottom_button_frame = tk.Frame(root, bg="#E0F7FA")
bottom_button_frame.pack(side=tk.BOTTOM, pady=20)

copy_button = tk.Button(bottom_button_frame, text="Copy Text", command=copy_to_clipboard, **button_style)
copy_button.pack(side=tk.LEFT, padx=10)

start_button = tk.Button(bottom_button_frame, text="Start Reading", command=start_speech, **button_style)
start_button.pack(side=tk.LEFT, padx=10)

pause_button = tk.Button(bottom_button_frame, text="Pause Reading", command=pause_speech, **button_style)
pause_button.pack(side=tk.LEFT, padx=10)

resume_button = tk.Button(bottom_button_frame, text="Resume Reading", command=resume_speech, **button_style)
resume_button.pack(side=tk.LEFT, padx=10)

stop_button = tk.Button(bottom_button_frame, text="Stop Reading", command=stop_speech, **button_style)
stop_button.pack(side=tk.LEFT, padx=10)

root.mainloop()