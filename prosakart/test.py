def main():
    import tkinter as tk
    top = tk.Tk()
    panel: tk.PanedWindow = tk.PanedWindow(top)
    panel.place(anchor=tk.CENTER, relx=0.5, rely=0.5)
    input("Make the button.")
    button = tk.Button(
            panel, text="Test",
            command=lambda: print("Hello"), width=10,
            font=("Ubuntu", 20)
        )
    input("Focus the button.")
    button.focus()
    input("Pack the button.")
    button.pack()
    input("All done!")
    top.mainloop()
