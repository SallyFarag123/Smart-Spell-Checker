import tkinter as tk
from tkinter import Toplevel, Listbox, Scrollbar, RIGHT, Y, BOTH, LEFT, filedialog, messagebox
from spellchecker import SpellChecker
import difflib
import re

APP_TITLE = "Sally & Rowan - Smart Spell Checker"
VERSION = "v3.2"

spell = SpellChecker(language='en')

LIGHT = {
    "bg": "#f6f8fa",
    "fg": "#111827",
    "input_bg": "#ffffff",
    "btn_bg": "#2563eb",
    "highlight_spell": "#ff4d4d"
}
DARK = {
    "bg": "#0f1724",
    "fg": "#e6eef8",
    "input_bg": "#06202e",
    "btn_bg": "#06b6d4",
    "highlight_spell": "#ff6b6b"
}
current_theme = DARK

root = tk.Tk()
root.title(f"{APP_TITLE}  {VERSION}")
root.geometry("1100x760")
root.minsize(1000, 700)

header_frame = tk.Frame(root)
header_frame.pack(fill="x", pady=8)
title_lbl = tk.Label(header_frame, text=APP_TITLE, font=("Helvetica", 22, "bold"))
title_lbl.pack(side="left", padx=18)
ver_lbl = tk.Label(header_frame, text=VERSION, font=("Helvetica", 10))
ver_lbl.pack(side="left", padx=6)

input_label = tk.Label(root, text="Input text:", font=("Helvetica", 14))
input_label.pack(anchor="w", padx=18)
input_text = tk.Text(root, height=12, width=120, font=("Segoe UI", 14), wrap="word")
input_text.pack(padx=18, pady=8)
input_scroll = tk.Scrollbar(root, command=input_text.yview)
input_scroll.place(in_=input_text, relx=1.0, relheight=1.0, x=-2)
input_text.config(yscrollcommand=input_scroll.set)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=6)

save_btn = tk.Button(btn_frame, text="Save Corrected", font=("Helvetica", 12))
suggest_btn = tk.Button(btn_frame, text="Suggestions", font=("Helvetica", 12))
theme_btn = tk.Button(btn_frame, text="Toggle Theme", font=("Helvetica", 12))
open_btn = tk.Button(btn_frame, text="Open .txt", font=("Helvetica", 12))
copy_btn = tk.Button(btn_frame, text="Copy Corrected", font=("Helvetica", 12))

save_btn.grid(row=0, column=0, padx=8)
suggest_btn.grid(row=0, column=1, padx=8)
open_btn.grid(row=0, column=2, padx=8)
copy_btn.grid(row=0, column=3, padx=8)
theme_btn.grid(row=0, column=4, padx=8)

output_label = tk.Label(root, text="Corrected text (live):", font=("Helvetica", 14))
output_label.pack(anchor="w", padx=18, pady=(12, 0))
output_text = tk.Text(root, height=16, width=120, font=("Segoe UI", 14), wrap="word")
output_text.pack(padx=18, pady=8)
output_scroll = tk.Scrollbar(root, command=output_text.yview)
output_scroll.place(in_=output_text, relx=1.0, relheight=1.0, x=-2)
output_text.config(yscrollcommand=output_scroll.set)
output_text.tag_configure("spell_fix", foreground=current_theme["highlight_spell"], font=("Segoe UI", 14, "bold"))

status_label = tk.Label(root, text="Ready", anchor="w", font=("Helvetica", 10))
status_label.pack(fill="x", padx=18, pady=(6, 12))

def preserve_case(orig, corr):
    if orig.isupper():
        return corr.upper()
    if orig.istitle():
        return corr.capitalize()
    return corr

token_re = re.compile(r"(\w+|\s+|[^\w\s])", re.UNICODE)

def live_process(event=None):
    raw = input_text.get("1.0", "end-1c")
    tokens = token_re.findall(raw)
    output_text.delete("1.0", "end")
    for tok in tokens:
        if tok.isspace() or not re.search(r'\w', tok, re.UNICODE):
            output_text.insert("end", tok)
            continue
        core = ''.join(ch for ch in tok if ch.isalpha())
        if not core:
            output_text.insert("end", tok)
            continue
        correction = spell.correction(core.lower())
        if correction and correction.lower() != core.lower():
            corrected_word = preserve_case(core, correction)
            start = output_text.index("end")
            output_text.insert("end", corrected_word)
            end = output_text.index("end")
            output_text.tag_add("spell_fix", f"{start}", f"{end}")
            output_text.insert("end", " ")
        else:
            output_text.insert("end", tok + " ")

def open_suggestions_popup():
    try:
        selected = input_text.get("sel.first", "sel.last").strip()
    except Exception:
        pos = input_text.index("insert")
        try:
            start = input_text.index("insert wordstart")
            end = input_text.index("insert wordend")
            selected = input_text.get(start, end).strip()
        except Exception:
            selected = ""
    if not selected:
        messagebox.showinfo("Suggestions", "Select a word or place cursor on a word.")
        return
    cand = list(spell.candidates(selected))
    close = difflib.get_close_matches(selected, list(spell.word_frequency), n=10, cutoff=0.6)
    suggestions = list(dict.fromkeys(cand + close))
    popup = Toplevel(root)
    popup.title(f"Suggestions for '{selected}'")
    lb = Listbox(popup, width=40, height=min(12, max(6, len(suggestions))), font=("Segoe UI", 12))
    for s in suggestions:
        lb.insert("end", s)
    lb.pack(side=LEFT, fill=BOTH, expand=True)
    sb = Scrollbar(popup, orient="vertical", command=lb.yview)
    sb.pack(side=RIGHT, fill=Y)
    lb.config(yscrollcommand=sb.set)

    def use_suggestion(evt=None):
        try:
            choice = lb.get(lb.curselection())
        except:
            return
        try:
            rstart = input_text.index("sel.first")
            rend = input_text.index("sel.last")
            input_text.delete(rstart, rend)
            input_text.insert(rstart, choice)
        except Exception:
            start = input_text.index("insert wordstart")
            end = input_text.index("insert wordend")
            input_text.delete(start, end)
            input_text.insert(start, choice + " ")
        popup.destroy()
        live_process()

    lb.bind("<Double-Button-1>", use_suggestion)
    lb.bind("<Return>", use_suggestion)

def open_text_file():
    path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All files", "*.*")])
    if not path:
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = f.read()
        input_text.delete("1.0", "end")
        input_text.insert("1.0", data)
        live_process()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open file: {e}")

def save_corrected_file():
    data = output_text.get("1.0", "end-1c")
    if not data.strip():
        messagebox.showwarning("Empty", "No corrected text to save.")
        return
    path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if not path:
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)
    status_label.config(text=f"Saved to {path}")

def copy_corrected():
    data = output_text.get("1.0", "end-1c")
    if not data.strip():
        return
    root.clipboard_clear()
    root.clipboard_append(data)
    status_label.config(text="Copied to clipboard")

def toggle_theme():
    global current_theme
    current_theme = LIGHT if current_theme == DARK else DARK
    apply_theme()

def apply_theme():
    root.config(bg=current_theme["bg"])
    header_frame.config(bg=current_theme["bg"])
    title_lbl.config(bg=current_theme["bg"], fg=current_theme["fg"])
    ver_lbl.config(bg=current_theme["bg"], fg=current_theme["fg"])
    input_label.config(bg=current_theme["bg"], fg=current_theme["fg"])
    output_label.config(bg=current_theme["bg"], fg=current_theme["fg"])
    status_label.config(bg=current_theme["bg"], fg=current_theme["fg"])
    input_text.config(bg=current_theme["input_bg"], fg=current_theme["fg"], insertbackground=current_theme["fg"])
    output_text.config(bg=current_theme["input_bg"], fg=current_theme["fg"], insertbackground=current_theme["fg"])
    btn_frame.config(bg=current_theme["bg"])
    for b in [save_btn, suggest_btn, theme_btn, open_btn, copy_btn]:
        b.config(bg=current_theme["btn_bg"], fg=current_theme["fg"])
    output_text.tag_configure("spell_fix", foreground=current_theme["highlight_spell"], font=("Segoe UI", 14, "bold"))

apply_theme()
input_text.bind("<KeyRelease>", live_process)
suggest_btn.config(command=open_suggestions_popup)
save_btn.config(command=save_corrected_file)
open_btn.config(command=open_text_file)
copy_btn.config(command=copy_corrected)
theme_btn.config(command=toggle_theme)

root.mainloop()
