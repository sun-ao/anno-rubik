import tkinter as tk

def rgb_to_color(rgb):
    root = tk.Tk()
    color = '#%02x%02x%02x' % rgb
    label = tk.Label(root, bg=color, width=10, height=5)
    label.pack()
    root.mainloop()

def on_submit():
    r = int(entry_r.get())
    g = int(entry_g.get())
    b = int(entry_b.get())
    rgb = (r, g, b)
    rgb_to_color(rgb)

root = tk.Tk()
root.title("RGB to Color")

label_r = tk.Label(root, text="R:")
label_r.pack()
entry_r = tk.Entry(root)
entry_r.pack()

label_g = tk.Label(root, text="G:")
label_g.pack()
entry_g = tk.Entry(root)
entry_g.pack()

label_b = tk.Label(root, text="B:")
label_b.pack()
entry_b = tk.Entry(root)
entry_b.pack()

button_submit = tk.Button(root, text="Submit", command=on_submit)
button_submit.pack()

root.mainloop()
