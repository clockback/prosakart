def main():
    input("Start!")
    import tkinter as tk
    input("Tkinter imported")
    import sqlite3 as sql
    input("SQLite imported")
    from pathlib import Path
    input("pathlib imported")

    home = Path.home()
    path = Path(home, ".prosakart")
    if len(list(home.glob(".prosakart"))) == 0:
        path.mkdir(parents=True, exist_ok=True)
    db_file = str(Path(path, "vocab.db"))
    input("Database created!")
