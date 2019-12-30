# collections is needed for remembering recent words.
from collections import deque

from difflib import SequenceMatcher
from os import path

# tkinter is needed for the GUI interface.
import tkinter as tk
from tkinter import ttk

# typing is needed for the type annotation.
from typing import Any, Callable, Deque, Iterable, Optional, Tuple, Type

# Import local files.
from . sql_handle import SQLHandler
from . misc import linspace


def separate(panel: tk.PanedWindow, row: Optional[int] = None) -> None:
    """
    Creates the gap.
    :param panel: tk.PanedWindow
        The panel onto which the gap must be placed.
    :param row: Optional[int]
        The row number on which to place the separator.
    :return: None
    """
    fake_label = tk.Label(panel, font=("Ubuntu", 1))

    if row is None:
        fake_label.pack()
    else:
        fake_label.grid(row=row)


def h_separate(
        panel: tk.PanedWindow, col: int, row: Optional[int] = None
) -> None:
    """
    Creates the horizontal gap.
    :param panel: tk.PanedWindow
        The panel onto which the gap must be placed.
    :param col: int
        The column number on which to place the separator.
    :param row: Optional[int]
        The row number on which to place the separator.
    :return: None
    """
    label = tk.Label(panel, text=" ", font=("Ubuntu", 7))
    if row is None:
        label.grid(column=col)
    else:
        label.grid(row=row, column=col)


class MainWidget:
    """
    This is the main widget. It is open as long as the application is
    open.
    """
    def __init__(self, handler: SQLHandler) -> None:
        """
        Creates the window.
        :return None:
        """
        # Creates the window.
        self.top: tk.Tk = tk.Tk()
        icon = tk.PhotoImage(file=path.join(
            path.dirname(path.realpath(__file__)), "images", "icon.png"
        ))
        self.top.wm_iconphoto(True, icon)
        self.top.title('ProSakart')
        self.top.geometry("500x400")
        self.top.update()
        self.top.minsize(self.top.winfo_width(), self.top.winfo_height())
        self.interface: Optional[BaseInterface] = None

        # Generates the main menu interface.
        MenuInterface(self, handler)


class BaseInterface:
    """
    This is the base class for the interfaces.
    """
    def __init__(
            self, main_widget: MainWidget, handler: SQLHandler, *_: Any
    ) -> None:
        """
        Creates the base class for the interfaces.
        :param main_widget: MainWidget
            The widget on which to create the interface.
        :param _: T
        :return: None
        """
        # Remembers the widget.
        self.widget: MainWidget = main_widget
        if self.widget.interface:
            self.widget.interface.destroy()
        self.widget.interface = self

        # Remembers the handler.
        self.handler = handler

        # Whether the interface has yet been discarded.
        self.destroyed: bool = False

    def destroy(self) -> None:
        """
        Destroys the interface.
        :return: None
        """
        self.destroyed = True

    def go_to(self, new_interface: Type['BaseInterface'], *args: Any) -> None:
        """
        Switches to a different interface.
        :param new_interface: BaseInterface
            The interface to which to switch.
        :return: None
        """
        if not self.destroyed:
            new_interface(self.widget, self.handler, *args)

    @staticmethod
    def bind_escape(
            elements: Iterable[tk.Widget], func: Callable[[], None]
    ) -> None:
        """
        Binds the escape event to the appropriate function for all
        given elements.
        :param elements: Iterable[tk.Widget]
            The list or iterable of widgets to be bound.
        :param func: Callable[[], None]
            The function to be bound.
        :return: None
        """
        for element in elements:
            element.bind("<Escape>", lambda _: func())


class MenuInterface(BaseInterface):
    """
    This is the main menu interface.
    """
    def __init__(self, main_widget: MainWidget, handler: SQLHandler) -> None:
        """
        Creates the test interface.
        :param main_widget: MainWidget
            The widget on which to create the test interface.
        :return: None
        """
        # Initializes the general aspects of the interface.
        super().__init__(main_widget, handler)

        # Creates the central panel.
        self.panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.panel.place(anchor=tk.CENTER, relx=0.5, rely=0.5)

        # Places an image at the bottom of the window.
        self.img = tk.PhotoImage(file=path.join(
            path.dirname(path.realpath(__file__)), "images", "logo.png"
        ))

        self.canvas = tk.Canvas(
            self.widget.top, width=self.img.width(),
            height=self.img.height()
        )
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)
        self.canvas.place(anchor=tk.CENTER, relx=0.5, rely=0.2)

        # Adding test button.
        self.test_button: tk.Button = tk.Button(
            self.panel, text="Test",
            command=lambda: self.go_to(TranslatorInterface), width=10,
            font=("Ubuntu", 20)
        )
        self.test_button.focus()
        self.test_button.pack()

        separate(self.panel)

        # Adding create button.
        self.create_button: tk.Button = tk.Button(
            self.panel, text="Create",
            command=lambda: self.go_to(EditInterface), width=10,
            font=("Ubuntu", 20)
        )
        self.create_button.pack()

        # Creates a small cluster of stars at the bottom-left of the
        # screen.
        self.star_img: tk.PhotoImage = tk.PhotoImage(file=path.join(
            path.dirname(path.realpath(__file__)), "images", "star.png"
        ))

        self.star_panel: tk.PanedWindow = tk.PanedWindow(
            self.widget.top, width=200, height=40
        )
        self.star_panel.place(anchor=tk.SW, relx=0, rely=1)

        self.stars: tk.Canvas = tk.Canvas(self.star_panel, width=60, height=40)
        self.stars.place(anchor=tk.NW, relx=0, rely=0)
        self.stars.create_image(5, 5, anchor=tk.NW, image=self.star_img)
        self.stars.create_image(15, 5, anchor=tk.NW, image=self.star_img)
        self.stars.create_image(25, 5, anchor=tk.NW, image=self.star_img)

        points = self.handler.get_points()
        self.no_stars: tk.Label = tk.Label(
            self.star_panel, text=points if points else 0,
            font=("Ubuntu", 20)
        )
        self.no_stars.place(anchor=tk.NW, relx=0, rely=0, x=65)

    def destroy(self) -> None:
        """
        Destroys the interface.
        :return: None
        """
        self.panel.destroy()
        self.canvas.destroy()
        super().destroy()


class EditInterface(BaseInterface):
    """
    This is the edit menu interface.
    """
    def __init__(self, main_widget: MainWidget, handler: SQLHandler) -> None:
        """
        Creates the edit interface.
        :param main_widget: MainWidget
            The widget on which to create the edit interface.
        :return: None
        """
        # Initializes the general aspects of the interface.
        super().__init__(main_widget, handler)

        # Creates the central panel.
        self.panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.panel.place(anchor=tk.CENTER, relx=0.5, rely=0.45)

        # Creates the edit languages button.
        self.edit_languages_button: tk.Button = tk.Button(
            self.panel, text="Edit languages", font=("Ubuntu", 20),
            command=lambda: self.go_to(EditLanguagesInterface), width=12,
        )
        self.edit_languages_button.focus()
        self.edit_languages_button.pack()

        separate(self.panel)

        # Creates the edit sheets button.
        self.edit_sheets_button: tk.Button = tk.Button(
            self.panel, text="Edit sheets", width=12, font=("Ubuntu", 20),
            command=lambda: self.go_to(EditSheetsInterface)
        )
        self.edit_sheets_button.pack()

        separate(self.panel)

        # Creates the new entries button.
        self.edit_entries_button: tk.Button = tk.Button(
            self.panel, text="Edit entries", width=12, font=("Ubuntu", 20),
            command=lambda: self.go_to(EditEntriesInterface)
        )
        self.edit_entries_button.pack()

        # Creates the back button.
        self.back_button: tk.Button = tk.Button(
            self.widget.top, text="Back", font=("Ubuntu", 20),
            command=lambda: self.go_to(MenuInterface), width=10
        )
        self.back_button.place(relx=0.01, rely=0.99, anchor=tk.SW)

        self.bind_escape(
            (
                self.edit_languages_button, self.edit_sheets_button,
                self.edit_entries_button, self.back_button,
            ), lambda: self.go_to(MenuInterface)
        )

    def destroy(self) -> None:
        """
        Destroys the interface.
        :return: None
        """
        self.panel.destroy()
        self.back_button.destroy()
        super().destroy()


class EditLanguagesInterface(BaseInterface):
    """
    This is the editing-languages interface.
    """
    def __init__(self, main_widget: MainWidget, handler: SQLHandler) -> None:
        """
        Creates the edit interface.
        :param main_widget: MainWidget
            The widget on which to create the edit interface.
        :return: None
        """
        # Initializes the general aspects of the interface.
        super().__init__(main_widget, handler)

        # Creates the central panel.
        self.panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.panel.place(anchor=tk.CENTER, relx=0.5, rely=0.5)

        # Creates the list of languages.
        self.language_list: tk.Listbox = tk.Listbox(
            self.panel, width=17, height=8, exportselection=False,
            font=("Ubuntu", 20)
        )
        self.language_list.grid(row=0, column=0)
        for language in self.handler.get_languages(sort=True):
            self.language_list.insert(tk.END, language)
        self.language_list.select_set(0)
        self.language_list.focus()

        h_separate(self.panel, col=1)

        # Creates a minor panel for the buttons.
        self.minor_panel: tk.PanedWindow = tk.PanedWindow(self.panel)
        self.minor_panel.grid(row=0, column=2, sticky=tk.NW)

        # Creates the new language button.
        self.new_language_button: tk.Button = tk.Button(
            self.minor_panel, text="New",
            command=lambda: self.go_to(CreateLanguageInterface), width=10,
            font=("Ubuntu", 20)
        )
        self.new_language_button.pack()

        separate(self.minor_panel)

        # Creates the edit language button.
        self.edit_language_button: tk.Button = tk.Button(
            self.minor_panel, text="Edit", width=10, font=("Ubuntu", 20),
            command=lambda: self.go_to(
                EditLanguageInterface, self.language_list.get(
                    self.language_list.curselection()
                )
            ),
        )
        self.edit_language_button.pack()

        separate(self.minor_panel)

        # Creates the delete language button.
        self.delete_language_button: tk.Button = tk.Button(
            self.minor_panel, text="Delete", width=10, font=("Ubuntu", 20),
            command=lambda: self.go_to(
                DeleteLanguageInterface, self.language_list.get(
                    self.language_list.curselection()
                )
            )

        )
        self.delete_language_button.pack()

        # Disables edit and delete buttons if no language is selected.
        if self.language_list.curselection() == ():
            self.edit_language_button.config(state=tk.DISABLED)
            self.delete_language_button.config(state=tk.DISABLED)

        # Creates the back button.
        self.back_button: tk.Button = tk.Button(
            self.widget.top, text="Back", width=10, font=("Ubuntu", 20),
            command=lambda: self.go_to(EditInterface),
        )
        self.back_button.place(relx=0.01, rely=0.99, anchor=tk.SW)

        self.bind_escape(
            (
                self.language_list, self.new_language_button,
                self.edit_language_button, self.delete_language_button,
                self.back_button
            ),
            lambda: self.go_to(EditInterface)
        )

    def delete_language(self) -> None:
        """
        Prompts the user to check if they wish to delete the language.
        :return: None
        """
        self.go_to(DeleteLanguageInterface, self.language_list.get(
            self.language_list.curselection()
        ))

    def go_to_single_language_editor(self) -> None:
        """
        Goes to the single language editor.
        :return: None
        """
        name = self.language_list.get(
            self.language_list.curselection()
        )
        self.go_to(EditLanguageInterface, name)

    def destroy(self) -> None:
        """
        Destroys the interface.
        :return: None
        """
        self.panel.destroy()
        self.back_button.destroy()
        super().destroy()


class CreateLanguageInterface(BaseInterface):
    """
    This is the language-creation interface.
    """
    def __init__(
            self, main_widget: MainWidget, handler: SQLHandler
    ) -> None:
        """
        Creates the sheet-picking interface.
        :param main_widget: MainWidget
            The widget on which to create the test interface.
        :return: None
        """
        # Initializes the general aspects of the interface.
        super().__init__(main_widget, handler)

        # Creates the central panel.
        self.panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.panel.place(anchor=tk.CENTER, relx=0.5, rely=0.5)

        # Creates the label.
        self.label: tk.Label = tk.Label(
            self.panel, text="Language name:", font=("Ubuntu", 20)
        )
        self.label.pack()

        separate(self.panel)

        # Creates the language name entry.
        self.string_var: tk.StringVar = tk.StringVar()
        self.string_var.trace_add("write", self.check_language)
        self.entry: tk.Entry = tk.Entry(
            self.panel, width=25, textvariable=self.string_var,
            font=("Ubuntu", 20)
        )
        self.entry.focus()
        self.entry.pack()

        # Creates the language name entry.
        self.back_button: tk.Button = tk.Button(
            self.widget.top, text="Back", width=10, font=("Ubuntu", 20),
            command=lambda: self.go_to(EditLanguagesInterface)
        )
        self.back_button.place(relx=0.01, rely=0.99, anchor=tk.SW)

        # Creates the language name entry.
        self.save_button: tk.Button = tk.Button(
            self.widget.top, text="Save", width=10,
            command=self.save_language, font=("Ubuntu", 20), state=tk.DISABLED
        )
        self.save_button.place(anchor=tk.SE, relx=0.99, rely=0.99)

        self.bind_escape(
            (self.entry, self.back_button, self.save_button),
            lambda: self.go_to(EditLanguagesInterface)
        )

    def save_language(self):
        """
        Saves the language to the database and returns to the menu.
        :return: None
        """
        self.handler.add_language(self.string_var.get())
        self.go_to(EditLanguagesInterface)

    def check_language(self, *_) -> bool:
        """
        Checks if the language in the entry is valid for creation.
        :return: None
        """
        name = self.string_var.get().strip()
        already_exists = bool(self.handler.get_language(name, r_none=True))
        correct_length = 1 <= len(name) <= 40

        if already_exists or not correct_length:
            if self.save_button["state"] == "normal":
                self.save_button.config(state=tk.DISABLED)
            return True
        else:
            if self.save_button["state"] == "disabled":
                self.save_button.config(state=tk.NORMAL)
            return False

    def destroy(self) -> None:
        """
        Destroys the interface.
        :return: None
        """
        self.panel.destroy()
        self.back_button.destroy()
        self.save_button.destroy()
        super().destroy()


class EditLanguageInterface(BaseInterface):
    """
    This is the single language-editing interface.
    """
    def __init__(
            self, main_widget: MainWidget, handler: SQLHandler, name: str
    ) -> None:
        """
        Creates the sheet-picking interface.
        :param main_widget: MainWidget
            The widget on which to create the test interface.
        :param name: str
            The name of the language being edited.
        :return: None
        """
        # Initializes the general aspects of the interface.
        super().__init__(main_widget, handler)

        # Remembers the previous name of the language.
        self.name = name

        # Creates the central panel.
        self.panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.panel.place(anchor=tk.CENTER, relx=0.5, rely=0.5)

        # Creates the label.
        self.label: tk.Label = tk.Label(
            self.panel, text="Language name:", font=("Ubuntu", 20)
        )
        self.label.pack()

        separate(self.panel)

        # Creates the language name entry.
        self.string_var: tk.StringVar = tk.StringVar()
        self.string_var.set(self.name)
        self.string_var.trace_add("write", self.check_language)
        self.entry: tk.Entry = tk.Entry(
            self.panel, width=25, textvariable=self.string_var,
            font=("Ubuntu", 20)
        )
        self.entry.focus()
        self.entry.icursor(tk.END)
        self.entry.pack()

        # Creates the language name entry.
        self.back_button: tk.Button = tk.Button(
            self.widget.top, text="Back", width=10, font=("Ubuntu", 20),
            command=lambda: self.go_to(EditLanguagesInterface)
        )
        self.back_button.place(relx=0.01, rely=0.99, anchor=tk.SW)

        # Creates the language name entry.
        self.save_button: tk.Button = tk.Button(
            self.widget.top, text="Save", width=10, command=self.save_language,
            font=("Ubuntu", 20)
        )
        self.save_button.place(anchor=tk.SE, relx=0.99, rely=0.99)

        self.bind_escape(
            (self.entry, self.back_button, self.save_button),
            lambda: self.go_to(EditLanguagesInterface)
        )

    def save_language(self):
        """
        Saves the language to the database and returns to the menu.
        :return: None
        """
        self.handler.change_language(self.name, self.string_var.get())
        self.go_to(EditLanguagesInterface)

    def check_language(self, *_) -> bool:
        """
        Checks if the language in the entry is valid for creation.
        :return: None
        """
        name = self.string_var.get().strip()
        exists_elsewhere = (
                name != self.name
                and bool(self.handler.get_language(name, r_none=True))
        )
        correct_length = 1 <= len(name) <= 40

        if exists_elsewhere or not correct_length:
            if self.save_button["state"] == "normal":
                self.save_button.config(state=tk.DISABLED)
            return True
        else:
            if self.save_button["state"] == "disabled":
                self.save_button.config(state=tk.NORMAL)
            return False

    def destroy(self) -> None:
        """
        Destroys the interface.
        :return: None
        """
        self.panel.destroy()
        self.back_button.destroy()
        self.save_button.destroy()
        super().destroy()


class DeleteLanguageInterface(BaseInterface):
    """
    This is the language-deleting interface.
    """
    def __init__(
            self, main_widget: MainWidget, handler: SQLHandler, name: str
    ) -> None:
        """
        Creates the sheet-picking interface.
        :param main_widget: MainWidget
            The widget on which to create the test interface.
        :param name: str
            The name of the language being deleted.
        :return: None
        """
        # Initializes the general aspects of the interface.
        super().__init__(main_widget, handler)

        # Remembers the previous name of the language.
        self.name = name

        # Creates the central panel.
        self.panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.panel.place(anchor=tk.CENTER, relx=0.5, rely=0.5)

        # Creates the label.
        self.label: tk.Label = tk.Label(
            self.panel, font=("Ubuntu", 20), wraplength=500,
            text=f"Are you sure you wish to delete \"{name}\" and all of "
            + "its sheets and entries?"
        )
        self.label.pack()

        separate(self.panel)

        # Creates the language name entry.
        self.back_button: tk.Button = tk.Button(
            self.widget.top, text="Back", width=10, font=("Ubuntu", 20),
            command=lambda: self.go_to(EditLanguagesInterface)
        )
        self.back_button.place(relx=0.01, rely=0.99, anchor=tk.SW)
        self.back_button.focus()

        # Creates the language name entry.
        self.delete_button: tk.Button = tk.Button(
            self.widget.top, text="Delete", width=10,
            command=self.delete_language, font=("Ubuntu", 20)
        )
        self.delete_button.place(anchor=tk.SE, relx=0.99, rely=0.99)

        self.bind_escape(
            (self.back_button, self.delete_button),
            lambda: self.go_to(EditLanguagesInterface)
        )

    def delete_language(self):
        """
        Saves the language to the database and returns to the menu.
        :return: None
        """
        self.handler.delete_language(self.name)
        self.go_to(EditLanguagesInterface)

    def destroy(self) -> None:
        """
        Destroys the interface.
        :return: None
        """
        self.panel.destroy()
        self.back_button.destroy()
        self.delete_button.destroy()
        super().destroy()


class EditSheetsInterface(BaseInterface):
    """
    This is the sheets-editing interface.
    """
    def __init__(
            self, main_widget: MainWidget, handler: SQLHandler

    ) -> None:
        """
        Creates the sheets-editing interface.
        :param main_widget: MainWidget
            The widget on which to create the test interface.
        :return: None
        """
        # Initializes the general aspects of the interface.
        super().__init__(main_widget, handler)

        # Creates the central panel.
        self.panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.panel.pack()

        # Creates the first language label.
        self.from_label: tk.Label = tk.Label(
            self.panel, text="From:", font=("Ubuntu", 20)
        )
        self.from_label.grid(row=0, column=0, sticky=tk.W)

        # Creates the first second label.
        self.to_label: tk.Label = tk.Label(
            self.panel, text="To:", font=("Ubuntu", 20)
        )
        self.to_label.grid(row=0, column=2, sticky=tk.W)

        # Creates the first list of languages.
        self.listbox_1: tk.Listbox = tk.Listbox(
            self.panel, width=15, height=9, exportselection=False,
            font=("Ubuntu", 20)
        )
        for language in self.handler.get_languages():
            self.listbox_1.insert(tk.END, language)
        self.listbox_1.focus()
        self.listbox_1.bind("<<ListboxSelect>>", self.check_both_clicked)
        self.listbox_1.grid(row=1, column=0)

        # Creates the second list of languages.
        self.listbox_2: tk.Listbox = tk.Listbox(
            self.panel, width=15, height=9, exportselection=False,
            font=("Ubuntu", 20)
        )
        for language in self.handler.get_languages():
            self.listbox_2.insert(tk.END, language)
        self.listbox_2.bind("<<ListboxSelect>>", self.check_both_clicked)
        self.listbox_2.grid(row=1, column=2)

        h_separate(self.panel, col=1)

        # Creates the new entry button.
        self.back_button: tk.Button = tk.Button(
            self.widget.top, text="Back",
            command=lambda: self.go_to(EditInterface), width=10,
            font=("Ubuntu", 20)
        )
        self.back_button.place(relx=0.01, rely=0.99, anchor=tk.SW)

        # Creates the button to progress.
        self.advance_button: tk.Button = tk.Button(
            self.widget.top, text="Advance", width=10, font=("Ubuntu", 20),
            command=lambda: self.go_to(
                EditTranslatorSheetsInterface,
                self.listbox_1.get(self.listbox_1.curselection()),
                self.listbox_2.get(self.listbox_2.curselection())
            )
        )
        self.advance_button.config(state=tk.DISABLED)
        self.advance_button.place(anchor=tk.SE, relx=0.99, rely=0.99)

        self.bind_escape(
            (
                self.listbox_1, self.listbox_2, self.back_button,
                self.advance_button
            ),
            lambda: self.go_to(EditInterface)
        )

    def check_both_clicked(self, _) -> None:
        """
        Activates the advance button if appropriate.
        :param _: tk.Event
            The event triggering the function.
        :return: None
        """
        if (
            self.listbox_1.curselection()
            and self.listbox_2.curselection()
            and self.listbox_1.curselection() != self.listbox_2.curselection()
            and self.advance_button["state"] == "disabled"
        ):
            self.advance_button.config(state=tk.NORMAL)
        elif (
            self.advance_button["state"] == "normal"
            and self.listbox_1.curselection() == self.listbox_2.curselection()
        ):
            self.advance_button.config(state=tk.DISABLED)

    def destroy(self) -> None:
        """
        Destroys the interface.
        :return: None
        """
        self.panel.destroy()
        self.advance_button.destroy()
        self.back_button.destroy()
        super().destroy()


class EditTranslatorSheetsInterface(BaseInterface):
    """
    This is the particular translator sheets-editing interface.
    """
    def __init__(
            self, main_widget: MainWidget, handler: SQLHandler, from_l: str,
            to_l: str
    ) -> None:
        """
        Creates the particular translator sheets-editing interface.
        :param main_widget: MainWidget
            The widget on which to create the edit interface.
        :return: None
        """
        # Initializes the general aspects of the interface.
        super().__init__(main_widget, handler)

        # Creates the central panel.
        self.panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.panel.pack(pady=10)

        # Creates the list of languages.
        self.sheet_list: tk.Listbox = tk.Listbox(
            self.panel, width=17, height=10, exportselection=False,
            font=("Ubuntu", 20)
        )
        self.sheet_list.grid(row=0, column=0)
        for sheet in self.handler.get_all_sheets(from_l, to_l, sort=True):
            self.sheet_list.insert(tk.END, sheet)
        self.sheet_list.select_set(0)
        self.sheet_list.focus()

        h_separate(self.panel, col=1)

        # Creates a minor panel for the buttons.
        self.minor_panel: tk.PanedWindow = tk.PanedWindow(self.panel)
        self.minor_panel.grid(row=0, column=2, sticky=tk.NW)

        # Creates the new sheet button.
        self.new_sheet_button: tk.Button = tk.Button(
            self.minor_panel, text="New", width=10, font=("Ubuntu", 20),
            command=lambda: self.go_to(
                CreateSheetInterface, from_l, to_l
            )
        )
        self.new_sheet_button.pack()

        separate(self.minor_panel)

        # Creates the edit language button.
        self.edit_sheet_button: tk.Button = tk.Button(
            self.minor_panel, text="Edit", width=10, font=("Ubuntu", 20),
            command=lambda: self.go_to(
                EditSheetInterface, self.sheet_list.get(
                    self.sheet_list.curselection()
                ), from_l, to_l
            )
        )
        self.edit_sheet_button.pack()

        separate(self.minor_panel)

        # Creates the delete language button.
        self.delete_sheet_button: tk.Button = tk.Button(
            self.minor_panel, text="Delete", width=10, font=("Ubuntu", 20),
            command=lambda: self.delete_sheet(from_l, to_l)
        )
        self.delete_sheet_button.pack()

        # Disables edit and delete buttons if no language is selected.
        if self.sheet_list.curselection() == ():
            self.edit_sheet_button.config(state=tk.DISABLED)
            self.delete_sheet_button.config(state=tk.DISABLED)

        # Creates the back button.
        self.back_button: tk.Button = tk.Button(
            self.widget.top, text="Back", width=10, font=("Ubuntu", 20),
            command=lambda: self.go_to(EditSheetsInterface)
        )
        self.back_button.place(relx=0.01, rely=0.99, anchor=tk.SW)

        self.bind_escape(
            (
                self.sheet_list, self.new_sheet_button, self.edit_sheet_button,
                self.delete_sheet_button, self.back_button
            ),
            lambda: self.go_to(EditSheetsInterface)
        )

    def delete_sheet(self, from_l: str, to_l: str) -> None:
        """
        Deletes the sheet from the database.
        :return: None
        """
        index = self.sheet_list.curselection()[0]
        name = self.sheet_list.get(index)
        self.handler.delete_sheet(name, from_l, to_l)
        self.sheet_list.delete(index)

        no_sheets = self.sheet_list.size()
        if no_sheets > 0:
            self.sheet_list.select_set(
                min((no_sheets - 1, index))
            )

        # Disables edit and delete buttons if no language is selected.
        if self.sheet_list.curselection() == ():
            self.edit_sheet_button.config(state=tk.DISABLED)
            self.delete_sheet_button.config(state=tk.DISABLED)
            self.sheet_list.focus()

    def destroy(self) -> None:
        """
        Destroys the interface.
        :return: None
        """
        self.panel.destroy()
        self.back_button.destroy()
        super().destroy()


class CreateSheetInterface(BaseInterface):
    """
    This is the sheet-creation interface.
    """
    def __init__(
            self, main_widget: MainWidget, handler: SQLHandler, from_l: str,
            to_l: str
    ) -> None:
        """
        Creates the sheet-creation interface.
        :param main_widget: MainWidget
            The widget on which to create the sheet-creation interface.
        :return: None
        """
        # Initializes the general aspects of the interface.
        super().__init__(main_widget, handler)

        # Creates the notebook, providing tabs
        self.notebook: ttk.Notebook = ttk.Notebook(self.widget.top)
        self.notebook.pack(expand=1, fill=tk.BOTH)

        # Creates the central panel for naming the sheet.
        self.n_panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.n_panel.pack(expand=1, fill=tk.Y)
        self.notebook.add(self.n_panel, text="Name")
        self.n_sub_panel: tk.PanedWindow = tk.PanedWindow(self.n_panel)
        self.n_sub_panel.place(anchor=tk.CENTER, relx=0.5, rely=0.5)

        # Creates the label.
        self.label: tk.Label = tk.Label(
            self.n_sub_panel, text="Sheet name:", font=("Ubuntu", 20)
        )
        self.label.grid(row=0, column=0, columnspan=2)

        separate(self.n_sub_panel, 1)

        # Creates the language name entry.
        self.name_var: tk.StringVar = tk.StringVar()
        self.name_var.trace_add(
            "write", lambda _, __, ___: self.check_sheet(from_l, to_l)
        )
        self.entry: tk.Entry = tk.Entry(
            self.n_sub_panel, width=25, textvariable=self.name_var,
            font=("Ubuntu", 20)
        )
        self.entry.focus()
        self.entry.grid(row=2, column=0, columnspan=2)

        # Remembers which entries have been selected
        self.current = set()
        self.current_shown = set()

        # Creates the central panel for adding entries.
        self.e_panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.e_panel.pack(expand=1, fill=tk.Y)
        self.notebook.add(self.e_panel, text="Entries")
        self.e_sub_panel: tk.PanedWindow = tk.PanedWindow(self.e_panel)
        self.e_sub_panel.place(anchor=tk.N, relx=0.5, rely=0.01)

        # Create the search entry at the top.
        self.find_var: tk.StringVar = tk.StringVar()
        self.find_var.trace_add(
            "write", lambda _, __, ___: self.search_entries(from_l, to_l)
        )
        self.search: tk.Entry = tk.Entry(
            self.e_sub_panel, width=25, textvariable=self.find_var,
            font=("Ubuntu", 20)
        )
        self.search.grid(row=0, column=0)

        separate(self.e_sub_panel, row=1)

        # Create the list of entries.
        self.entries: tk.Listbox = tk.Listbox(
            self.e_sub_panel, width=25, height=8, exportselection=False,
            font=("Ubuntu", 20), selectmode=tk.MULTIPLE
        )
        for (_, question) in handler.search_entries('', from_l, to_l):
            self.entries.insert(tk.END, question)
        self.entries.grid(row=2, column=0)
        self.entries.bind("<<ListboxSelect>>", self.add_entry)

        # Creates the language name entry.
        self.back_button: tk.Button = tk.Button(
            self.widget.top, text="Back", width=10, font=("Ubuntu", 20),
            command=lambda: self.go_to(
                EditTranslatorSheetsInterface, from_l, to_l
            )
        )
        self.back_button.place(relx=0.01, rely=0.99, anchor=tk.SW)

        # Creates the language name entry.
        self.save_button: tk.Button = tk.Button(
            self.widget.top, text="Save", width=10, font=("Ubuntu", 20),
            command=lambda: self.save_sheet(from_l, to_l)
        )
        self.save_button.config(state=tk.DISABLED)
        self.save_button.place(relx=0.99, rely=0.99, anchor=tk.SE)

        self.bind_escape(
            (
                self.notebook, self.entry, self.search, self.entries,
                self.back_button, self.save_button
            ),
            lambda: self.go_to(EditTranslatorSheetsInterface, from_l, to_l)
        )

    def add_entry(self, _: tk.EventType):
        """
        Adds an entry to the set of entries for the sheet, although
        does not yet save it.
        :param _: tk.EventType
            The event with the selection. (unused)
        :return: None
        """
        # Adds the newly selected entry to the set of current entries
        to_add = set(map(
            self.entries.get, self.entries.curselection()
        )).difference(self.current_shown)
        self.current.update(to_add)
        self.current_shown.update(to_add)

        to_remove = self.current_shown.difference(
            map(self.entries.get, self.entries.curselection())
        )
        self.current.difference_update(to_remove)
        self.current_shown.difference_update(to_remove)

    def search_entries(self, from_l: str, to_l: str) -> None:
        """
        Searches for all related entries.
        :return: None
        """
        results = self.handler.search_entries(
            self.find_var.get(), from_l, to_l
        )
        self.entries.delete(0, tk.END)
        self.current_shown.clear()

        for (_, question) in results:
            self.entries.insert(tk.END, question)
            if question in self.current:
                self.entries.select_set(tk.END)
                self.current_shown.add(question)

    def save_sheet(self, from_l, to_l):
        """
        Saves the sheet to the database and returns to the menu.
        :return: None
        """
        self.handler.add_sheet(
            self.name_var.get(), from_l, to_l, self.current_shown
        )
        self.go_to(EditTranslatorSheetsInterface, from_l, to_l)

    def check_sheet(self, from_l: str, to_l: str) -> bool:
        """
        Checks if the sheet in the entry is valid for creation.
        :return: None
        """
        name = self.name_var.get().strip()
        already_exists = bool(self.handler.get_sheet(
            name, from_l, to_l, r_none=True
        ))
        correct_length = 1 <= len(name) <= 80

        if already_exists or not correct_length:
            if self.save_button["state"] == "normal":
                self.save_button.config(state=tk.DISABLED)
            return True
        else:
            if self.save_button["state"] == "disabled":
                self.save_button.config(state=tk.NORMAL)
            return False

    def destroy(self) -> None:
        """
        Destroys the interface.
        :return: None
        """
        self.notebook.destroy()
        self.back_button.destroy()
        self.save_button.destroy()
        super().destroy()


class EditSheetInterface(BaseInterface):
    """
    This is the single sheet-editing interface.
    """
    def __init__(
            self, main_widget: MainWidget, handler: SQLHandler, name: str,
            from_l: str, to_l: str
    ) -> None:
        """
        Creates the sheet-picking interface.
        :param main_widget: MainWidget
            The widget on which to create the test interface.
        :param name: str
            The name of the language being edited.
        :return: None
        """
        # Initializes the general aspects of the interface.
        super().__init__(main_widget, handler)

        # Remembers the previous name of the language.
        self.name = name

        # Creates the notebook, providing tabs
        self.notebook: ttk.Notebook = ttk.Notebook(self.widget.top)
        self.notebook.pack(expand=1, fill=tk.BOTH)

        # Creates the central panel for naming the sheet.
        self.n_panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.n_panel.pack(expand=1, fill=tk.Y)
        self.notebook.add(self.n_panel, text="Name")
        self.n_sub_panel: tk.PanedWindow = tk.PanedWindow(self.n_panel)
        self.n_sub_panel.place(anchor=tk.CENTER, relx=0.5, rely=0.5)

        # Creates the label.
        self.label: tk.Label = tk.Label(
            self.n_sub_panel, text="Sheet name:", font=("Ubuntu", 20)
        )
        self.label.grid(row=0, column=0, columnspan=2)

        separate(self.n_sub_panel, 1)

        # Creates the language name entry.
        self.string_var: tk.StringVar = tk.StringVar()
        self.string_var.set(self.name)
        self.string_var.trace_add(
            "write", lambda _, __, ___: self.check_sheet(from_l, to_l)
        )
        self.entry: tk.Entry = tk.Entry(
            self.n_sub_panel, width=25, textvariable=self.string_var,
            font=("Ubuntu", 20)
        )
        self.entry.focus()
        self.entry.icursor(tk.END)
        self.entry.grid(row=2, column=0, columnspan=2)

        # Remembers which entries have been selected
        self.current = set(
            x[1] for x in self.handler.get_entries_from_sheet(
                self.name, from_l, to_l
            )
        )
        self.current_shown = self.current.copy()

        # Creates the central panel for adding entries.
        self.e_panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.e_panel.pack(expand=1, fill=tk.Y)
        self.notebook.add(self.e_panel, text="Entries")
        self.e_sub_panel: tk.PanedWindow = tk.PanedWindow(self.e_panel)
        self.e_sub_panel.place(anchor=tk.N, relx=0.5, rely=0.01)

        # Create the search entry at the top.
        self.find_var: tk.StringVar = tk.StringVar()
        self.find_var.trace_add(
            "write", lambda _, __, ___: self.search_entries(from_l, to_l)
        )
        self.search: tk.Entry = tk.Entry(
            self.e_sub_panel, width=25, textvariable=self.find_var,
            font=("Ubuntu", 20)
        )
        self.search.grid(row=0, column=0)

        separate(self.e_sub_panel, row=1)

        # Create the list of entries.
        self.entries: tk.Listbox = tk.Listbox(
            self.e_sub_panel, width=25, height=8, exportselection=False,
            font=("Ubuntu", 20), selectmode=tk.MULTIPLE
        )
        for (_, question) in handler.search_entries('', from_l, to_l):
            self.entries.insert(tk.END, question)
            if question in self.current:
                self.entries.selection_set(tk.END)
        self.entries.grid(row=2, column=0)
        self.entries.bind("<<ListboxSelect>>", self.add_entry)

        # Creates the language name entry.
        self.back_button: tk.Button = tk.Button(
            self.widget.top, text="Back", width=10, font=("Ubuntu", 20),
            command=lambda: self.go_to(
                EditTranslatorSheetsInterface, from_l, to_l
            )
        )
        self.back_button.place(relx=0.01, rely=0.99, anchor=tk.SW)

        # Creates the language name entry.
        self.save_button: tk.Button = tk.Button(
            self.widget.top, text="Save", width=10, font=("Ubuntu", 20),
            command=lambda: self.save_sheet(from_l, to_l)
        )
        self.save_button.place(relx=0.99, rely=0.99, anchor=tk.SE)

        self.bind_escape(
            (
                self.notebook, self.entry, self.search, self.entries,
                self.back_button, self.save_button
            ),
            lambda: self.go_to(EditTranslatorSheetsInterface, from_l, to_l)
        )

    def check_sheet(self, from_l: str, to_l: str) -> bool:
        """
        Checks if the sheet in the entry is valid for creation.
        :return: None
        """
        name = self.string_var.get().strip()
        exists_elsewhere = (
                name != self.name
                and bool(
                    self.handler.get_sheet(name, from_l, to_l, r_none=True)
                )
        )
        correct_length = 1 <= len(name) <= 80

        if exists_elsewhere or not correct_length:
            if self.save_button["state"] == "normal":
                self.save_button.config(state=tk.DISABLED)
            return True
        else:
            if self.save_button["state"] == "disabled":
                self.save_button.config(state=tk.NORMAL)
            return False

    def save_sheet(self, from_l: str, to_l: str):
        """
        Saves the sheet to the database and returns to the menu.
        :return: None
        """
        self.handler.change_sheet(
            self.name, self.string_var.get(), from_l, to_l, self.current
        )
        self.go_to(EditTranslatorSheetsInterface, from_l, to_l)

    def add_entry(self, _: tk.EventType):
        """
        Adds an entry to the set of entries for the sheet, although
        does not yet save it.
        :param _: tk.EventType
            The event with the selection. (unused)
        :return: None
        """
        # Adds the newly selected entry to the set of current entries
        to_add = set(map(
            self.entries.get, self.entries.curselection()
        )).difference(self.current_shown)
        self.current.update(to_add)
        self.current_shown.update(to_add)

        to_remove = self.current_shown.difference(
            map(self.entries.get, self.entries.curselection())
        )
        self.current.difference_update(to_remove)
        self.current_shown.difference_update(to_remove)

    def search_entries(self, from_l: str, to_l: str) -> None:
        """
        Searches for all related entries.
        :return: None
        """
        results = self.handler.search_entries(
            self.find_var.get(), from_l, to_l
        )
        self.entries.delete(0, tk.END)
        self.current_shown.clear()

        for (_, question) in results:
            self.entries.insert(tk.END, question)
            if question in self.current:
                self.entries.select_set(tk.END)
                self.current_shown.add(question)

    def destroy(self) -> None:
        """
        Destroys the interface.
        :return: None
        """
        self.notebook.destroy()
        self.back_button.destroy()
        self.save_button.destroy()
        super().destroy()


class EditEntriesInterface(BaseInterface):
    """
    This is the entries-editing interface.
    """
    def __init__(
            self, main_widget: MainWidget, handler: SQLHandler
    ) -> None:
        """
        Creates the entries-editing interface.
        :param main_widget: MainWidget
            The widget on which to create the test interface.
        :return: None
        """
        # Initializes the general aspects of the interface.
        super().__init__(main_widget, handler)

        # Creates the central panel.
        self.panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.panel.pack()

        # Creates the first language label.
        self.from_label: tk.Label = tk.Label(
            self.panel, text="From:", font=("Ubuntu", 20)
        )
        self.from_label.grid(row=0, column=0, sticky=tk.W)

        # Creates the first second label.
        self.to_label: tk.Label = tk.Label(
            self.panel, text="To:", font=("Ubuntu", 20)
        )
        self.to_label.grid(row=0, column=2, sticky=tk.W)

        # Creates the first list of languages.
        self.listbox_1: tk.Listbox = tk.Listbox(
            self.panel, width=15, height=9, exportselection=False,
            font=("Ubuntu", 20)
        )
        for language in self.handler.get_languages():
            self.listbox_1.insert(tk.END, language)
        self.listbox_1.focus()
        self.listbox_1.bind("<<ListboxSelect>>", self.check_both_clicked)
        self.listbox_1.grid(row=1, column=0)

        # Creates the second list of languages.
        self.listbox_2: tk.Listbox = tk.Listbox(
            self.panel, width=15, height=9, exportselection=False,
            font=("Ubuntu", 20)
        )
        for language in self.handler.get_languages():
            self.listbox_2.insert(tk.END, language)
        self.listbox_2.bind("<<ListboxSelect>>", self.check_both_clicked)
        self.listbox_2.grid(row=1, column=2)

        h_separate(self.panel, col=1)

        # Creates the new entry button.
        self.back_button: tk.Button = tk.Button(
            self.widget.top, text="Back",
            command=lambda: self.go_to(EditInterface), width=10,
            font=("Ubuntu", 20)
        )
        self.back_button.place(relx=0.01, rely=0.99, anchor=tk.SW)

        # Creates the button to progress.
        self.advance_button: tk.Button = tk.Button(
            self.widget.top, text="Advance", width=10, font=("Ubuntu", 20),
            command=lambda: self.go_to(
                EditTranslatorEntriesInterface,
                self.listbox_1.get(self.listbox_1.curselection()),
                self.listbox_2.get(self.listbox_2.curselection())
            )
        )
        self.advance_button.config(state=tk.DISABLED)
        self.advance_button.place(anchor=tk.SE, relx=0.99, rely=0.99)

        self.bind_escape(
            (
                self.listbox_1, self.listbox_2, self.back_button,
                self.advance_button,
            ), lambda: self.go_to(EditInterface)
        )

    def check_both_clicked(self, _) -> None:
        """
        Activates the advance button if appropriate.
        :param _: tk.Event
            The event triggering the function.
        :return: None
        """
        if (
            self.listbox_1.curselection()
            and self.listbox_2.curselection()
            and self.listbox_1.curselection() != self.listbox_2.curselection()
            and self.advance_button["state"] == "disabled"
        ):
            self.advance_button.config(state=tk.NORMAL)
        elif (
            self.advance_button["state"] == "normal"
            and self.listbox_1.curselection() == self.listbox_2.curselection()
        ):
            self.advance_button.config(state=tk.DISABLED)

    def destroy(self) -> None:
        """
        Destroys the interface.
        :return: None
        """
        self.panel.destroy()
        self.advance_button.destroy()
        self.back_button.destroy()
        super().destroy()


class EditTranslatorEntriesInterface(BaseInterface):
    """
    This is the translator-specific entries-editing interface.
    """
    def __init__(
            self, main_widget: MainWidget, handler: SQLHandler, from_l: str,
            to_l: str
    ) -> None:
        """
        Creates the translator-specific entries-editing interface.
        :param main_widget: MainWidget
            The widget on which to create the test interface.
        :return: None
        """
        # Initializes the general aspects of the interface.
        super().__init__(main_widget, handler)

        # Creates the central panel.
        self.panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.panel.pack()

        # Create the search entry at the top.
        self.string_var: tk.StringVar = tk.StringVar()
        self.string_var.trace_add(
            "write", lambda _, __, ___: self.search_entries(from_l, to_l)
        )
        self.search: tk.Entry = tk.Entry(
            self.panel, width=25, textvariable=self.string_var,
            font=("Ubuntu", 20)
        )
        self.search.focus()
        self.search.grid(row=0, column=0, columnspan=3)

        separate(self.panel, row=1)

        # Create the list of entries.
        self.entries: tk.Listbox = tk.Listbox(
            self.panel, width=19, height=9, exportselection=False,
            font=("Ubuntu", 20)
        )
        for (_, question) in handler.search_entries('', from_l, to_l):
            self.entries.insert(tk.END, question)
        self.entries.grid(row=2, column=0)
        self.entries.bind("<<ListboxSelect>>", self.check_selected)

        h_separate(self.panel, col=1, row=2)

        # Creates a minor panel for the buttons.
        self.minor_panel: tk.PanedWindow = tk.PanedWindow(self.panel)
        self.minor_panel.grid(row=2, column=2, sticky=tk.NW)

        # Create a button for adding entry.
        self.create_entry_button: tk.Button = tk.Button(
            self.minor_panel, text="New", width=10, font=("Ubuntu", 20),
            command=lambda: self.go_to(CreateEntryInterface, from_l, to_l)
        )
        self.create_entry_button.pack()

        separate(self.minor_panel)

        # Create a button for editing entry.
        self.edit_entry_button: tk.Button = tk.Button(
            self.minor_panel, text="Edit", width=10, font=("Ubuntu", 20),
            command=lambda: self.go_to(
                EditEntryInterfaceNew, handler.get_entry(
                    self.entries.get(self.entries.curselection()), from_l,
                    to_l
                )
            ), state=tk.DISABLED
        )
        self.edit_entry_button.pack()

        separate(self.minor_panel)

        # Create a button for deleting entry.
        self.delete_entry_button: tk.Button = tk.Button(
            self.minor_panel, text="Delete", width=10, font=("Ubuntu", 20),
            command=lambda: self.delete_entry(from_l, to_l), state=tk.DISABLED
        )
        self.delete_entry_button.pack()

        # Creates the new entry button.
        self.back_button: tk.Button = tk.Button(
            self.widget.top, text="Back", width=10, font=("Ubuntu", 20),
            command=lambda: self.go_to(EditEntriesInterface)
        )
        self.back_button.place(relx=0.01, rely=0.99, anchor=tk.SW)

        self.bind_escape(
            (
                self.search, self.entries, self.create_entry_button,
                self.edit_entry_button, self.delete_entry_button,
                self.back_button
            ), lambda: self.go_to(EditEntriesInterface)
        )

    def delete_entry(self, from_l: str, to_l: str) -> None:
        """
        Deletes the selected entry.
        :param from_l: str
            The name of the language being translated from.
        :param to_l: str
            The name of the language being translated to.
        :return: None
        """
        current = self.entries.curselection()[0]
        question = self.entries.get(current)
        self.handler.delete_entry(question, from_l, to_l)
        self.entries.delete(current)

        no_remaining = len(self.entries.get(first=0, last=tk.END))
        if no_remaining == current and no_remaining >= 1:
            self.entries.selection_set(current - 1)
        elif no_remaining > current:
            self.entries.selection_set(current)
        else:
            self.edit_entry_button.config(state=tk.DISABLED)
            self.delete_entry_button.config(state=tk.DISABLED)
            self.create_entry_button.focus()

    def check_selected(self, *_) -> None:
        """
        Makes sure that the edit and delete buttons are either disabled
        or normal as required.
        :return: None
        """
        current_selection = self.entries.curselection()
        if (
                current_selection != ()
                and self.edit_entry_button['state'] == 'disabled'
        ):
            self.edit_entry_button.config(state=tk.NORMAL)
            self.delete_entry_button.config(state=tk.NORMAL)
        elif (
                current_selection == ()
                and self.edit_entry_button['state'] == 'normal'
        ):
            self.edit_entry_button.config(state=tk.DISABLED)
            self.delete_entry_button.config(state=tk.DISABLED)

    def search_entries(self, from_l: str, to_l: str) -> None:
        """
        Searches for all related entries.
        :return: None
        """
        idx = self.entries.curselection()
        current = self.entries.get(idx) if idx != () else None
        results = self.handler.search_entries(
            self.string_var.get(), from_l, to_l
        )
        self.entries.delete(0, tk.END)
        for (_, question) in results:
            self.entries.insert(tk.END, question)
            if question == current:
                self.entries.select_set(tk.END)

        self.check_selected()

    def destroy(self) -> None:
        """
        Destroys the interface.
        :return: None
        """
        self.panel.destroy()
        self.back_button.destroy()
        super().destroy()


class CreateEntryInterface(BaseInterface):
    """
    This is the entry-creation interface.
    """
    def __init__(
            self, main_widget: MainWidget, handler: SQLHandler, from_l: str,
            to_l: str
    ) -> None:
        """
        Creates the entry-creation interface.
        :param MainWidget main_widget: The widget on which to create the
            sheet-creation interface.
        :param SQLHandler handler: The handler for the SQLite database.
        :param str from_l: The name of the language being translated.
        :param str to_l: The name of the language to which it is being
            translated.
        :return: None
        """
        # Initializes the general aspects of the interface.
        super().__init__(main_widget, handler)

        # Creates the notebook, providing tabs
        self.notebook: ttk.Notebook = ttk.Notebook(self.widget.top)
        self.notebook.pack(expand=1, fill=tk.BOTH)

        # Creates the central panel for naming the sheet.
        self.q_panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.q_panel.pack(expand=1, fill=tk.Y)
        self.notebook.add(self.q_panel, text="Question")
        self.q_sub_panel: tk.PanedWindow = tk.PanedWindow(self.q_panel)
        self.q_sub_panel.place(anchor=tk.CENTER, relx=0.5, rely=0.45)

        # Creates the label for the question.
        self.q_label: tk.Label = tk.Label(
            self.q_sub_panel, text="Question:", font=("Ubuntu", 20)
        )
        self.q_label.pack()

        separate(self.q_sub_panel)

        # Creates the question entry.
        self.question_sv: tk.StringVar = tk.StringVar()
        self.question_sv.trace_add(
            "write", lambda _, __, ___: self.check_entry(from_l, to_l)
        )
        self.question: tk.Entry = tk.Entry(
            self.q_sub_panel, width=25, textvariable=self.question_sv,
            font=("Ubuntu", 20)
        )
        self.question.focus()
        self.question.pack()

        separate(self.q_sub_panel)

        # Creates the label for the answer.
        self.a_label: tk.Label = tk.Label(
            self.q_sub_panel, text="Top answer:", font=("Ubuntu", 20)
        )
        self.a_label.pack()

        separate(self.q_sub_panel)

        # Creates the answer entry.
        self.answer_sv: tk.StringVar = tk.StringVar()
        self.answer_sv.trace_add(
            "write", lambda _, __, ___: self.check_entry(from_l, to_l)
        )
        self.answer: tk.Entry = tk.Entry(
            self.q_sub_panel, width=25, textvariable=self.answer_sv,
            font=("Ubuntu", 20)
        )
        self.answer.bind("<FocusOut>", lambda _: self.lose_focus_on_answer())
        self.answer.pack()

        # Creates the central panel for writing answers.
        self.a_panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.a_panel.pack(expand=1, fill=tk.Y)
        self.notebook.add(self.a_panel, text="Answers")
        self.a_sub_panel: tk.PanedWindow = tk.PanedWindow(self.a_panel)
        self.a_sub_panel.place(anchor=tk.CENTER, relx=0.5, rely=0.42)

        # Creates a label for the question
        self.a_static_label: tk.Label = tk.Label(
            self.a_sub_panel, text="", font=("Ubuntu", 20)
        )
        self.a_static_label.grid(row=0, column=0, columnspan=3)

        # Creates the answer entry
        self.new_answer_sv: tk.StringVar = tk.StringVar()
        self.new_answer_sv.trace_add(
            "write", lambda _, __, ___: self.check_answers()
        )

        self.answer_entry: tk.Entry = tk.Entry(
            self.a_sub_panel, font=("Ubuntu", 20), width=15,
            textvariable=self.new_answer_sv
        )
        self.answer_entry.grid(row=1, column=0)

        h_separate(self.a_sub_panel, row=1, col=1)

        # Creates a button for the answer entry
        self.add_button: tk.Button = tk.Button(
            self.a_sub_panel, text="Add", font=("Ubuntu", 20), width=10,
            command=self.add_answer, state=tk.DISABLED
        )
        self.add_button.grid(row=1, column=2)

        separate(self.a_sub_panel, 2)

        # Adds the listbox containing all answers
        self.answers: tk.Listbox = tk.Listbox(
            self.a_sub_panel, width=15, height=7, font=("Ubuntu", 20),
            exportselection=False
        )
        self.answers.insert(tk.END, "")
        self.answers.grid(row=3, column=0, columnspan=2)

        # Adds the deletion button
        self.delete_button: tk.Button = tk.Button(
            self.a_sub_panel, text="Delete", font=("Ubuntu", 20), width=10,
            command=self.delete_answer, state=tk.DISABLED
        )
        self.delete_button.grid(row=3, column=2, sticky=tk.N)

        self.answers.bind(
            "<<ListboxSelect>>",
            lambda _: self.check_selection()
        )

        # Creates the central panel for naming the sheet.
        self.e_panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.e_panel.pack(expand=1, fill=tk.Y)
        self.notebook.add(self.e_panel, text="Sheets")
        self.e_sub_panel: tk.PanedWindow = tk.PanedWindow(self.e_panel)
        self.e_sub_panel.place(anchor=tk.CENTER, relx=0.5, rely=0.4)

        # Creates a label with the question displayed
        self.e_label: tk.Label = tk.Label(
            self.e_sub_panel, text="", font=("Ubuntu", 20)
        )
        self.e_label.pack()

        # Creates the sheets list
        self.sheets: tk.Listbox = tk.Listbox(
            self.e_sub_panel, selectmode=tk.MULTIPLE, width=25, height=8,
            exportselection=False, font=("Ubuntu", 20)
        )
        for sheet in self.handler.get_all_sheets(from_l, to_l):
            self.sheets.insert(tk.END, sheet)
        self.sheets.pack()

        # Creates the language name entry.
        self.back_button: tk.Button = tk.Button(
            self.widget.top, text="Back", width=10, font=("Ubuntu", 20),
            command=lambda: self.go_to(
                EditTranslatorEntriesInterface, from_l, to_l
            )
        )
        self.back_button.place(relx=0.01, rely=0.99, anchor=tk.SW)

        # Creates the button to progress.
        self.save_button: tk.Button = tk.Button(
            self.widget.top, text="Save", width=10, font=("Ubuntu", 20),
            state=tk.DISABLED, command=lambda: self.save_entry(from_l, to_l)
        )
        self.save_button.place(anchor=tk.SE, relx=0.99, rely=0.99)

        self.bind_escape(
            (
                self.notebook, self.question, self.answer, self.answer_entry,
                self.answers, self.add_button, self.delete_button, self.sheets,
                self.back_button, self.save_button
            ), lambda: self.go_to(EditTranslatorEntriesInterface, from_l, to_l)
        )

    def lose_focus_on_answer(self) -> None:
        """
        Updates the corresponding list of answers.
        :return: None
        """
        self.answers.delete(0)
        to_add = self.answer_sv.get()
        all_answers = list(self.answers.get(0, tk.END))
        if to_add in all_answers:
            self.answers.delete(all_answers.index(to_add))
        self.answers.insert(0, self.answer_sv.get())

    def check_entry(self, from_l: str, to_l: str) -> bool:
        """
        Checks if the entry is valid for creation.
        :return: bool
            Whether the sheet can be saved or not.
        """
        question = self.question_sv.get().strip()
        answer = self.answer_sv.get().strip()

        # Adjusts the labels
        self.a_static_label.config(text=question)
        if self.answers.get(0, tk.END) == ('',):
            self.delete_button.config(state=tk.DISABLED)
        self.e_label.config(text=question)

        correct_lengths = 1 <= len(question) <= 80 and 1 <= len(answer) <= 80
        if (
                question == ''
                or self.handler.get_entry(question, from_l, to_l)
                or not correct_lengths
        ):
            if self.save_button["state"] == "normal":
                self.save_button.config(state=tk.DISABLED)
            return False

        if self.save_button["state"] == "disabled":
            self.save_button.config(state=tk.NORMAL)
        return True

    def check_answers(self) -> None:
        """
        Checks if the answer can be added to the existing list.
        :return: None
        """
        existing = self.answers.get(0, tk.END)
        to_add = self.new_answer_sv.get()
        correct_lengths = 1 <= len(to_add) <= 80

        if to_add in existing or not correct_lengths:
            self.add_button.config(state=tk.DISABLED)
        else:
            self.add_button.config(state=tk.NORMAL)

    def add_answer(self) -> None:
        """
        Adds an answer to the list of answers.
        :return: None
        """
        to_add = self.new_answer_sv.get()
        self.new_answer_sv.set("")
        self.answers.insert(tk.END, to_add)
        if self.answers.get(0) == "":
            self.answers.delete(0)
            self.answer_sv.set(to_add)
        self.answer_entry.focus()

    def check_selection(self) -> None:
        """
        Checks the selected answer and activates buttons accordingly.
        :return: None
        """
        if self.answers.get(0, tk.END)[0]:
            self.delete_button.config(state=tk.NORMAL)

    def delete_answer(self) -> None:
        """
        Deletes an answer from the answers list
        :return: None
        """
        pos = self.answers.curselection()[0]
        all_answers = self.answers.get(0, tk.END)
        self.answers.delete(pos)
        if len(all_answers) == 1:
            self.answers.insert(tk.END, "")
            self.delete_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.DISABLED)
            self.answer_entry.focus()
        if pos == 0:
            self.answer_sv.set(self.answers.get(0))

        # Selects another entry if possible
        if pos == len(all_answers) - 1:
            self.answers.selection_set(pos - 1)
        else:
            self.answers.selection_set(pos)

    def save_entry(
            self, from_l: str, to_l: str
    ) -> None:
        """
        Saves the entry.
        :param from_l: str
            The name of the language being translated.
        :param to_l: str
            The name of the language to which it is being translated.
        :return: None
        """
        self.lose_focus_on_answer()
        self.handler.add_entry(
            from_l, to_l, self.question_sv.get(), self.answers.get(0, tk.END),
            list(map(self.sheets.get, self.sheets.curselection()))
        )
        self.go_to(EditTranslatorEntriesInterface, from_l, to_l)

    def destroy(self) -> None:
        """
        Destroys the interface.
        :return: None
        """
        self.notebook.destroy()
        self.back_button.destroy()
        self.save_button.destroy()
        super().destroy()


class EditEntryInterfaceNew(BaseInterface):
    """
    This is the entry-editing interface.
    """
    def __init__(
            self, main_widget: MainWidget, handler: SQLHandler, entry: int
    ) -> None:
        """
        Creates the entry-editing interface.
        :param main_widget: MainWidget
            The widget on which to create the sheet-creation interface.
        :param handler: SQLHandler
            The handler for the SQLite database.
        :param entry: int
            The serial number of the entry being edited.
        :return: None
        """
        # Initializes the general aspects of the interface.
        super().__init__(main_widget, handler)

        from_l, to_l = self.handler.get_language_names_from_entry(entry)
        question, answer = self.handler.get_entry_question_and_answer(entry)

        # Creates the notebook, providing tabs
        self.notebook: ttk.Notebook = ttk.Notebook(self.widget.top)
        self.notebook.pack(expand=1, fill=tk.BOTH)

        # Creates the central panel for naming the sheet.
        self.q_panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.q_panel.pack(expand=1, fill=tk.Y)
        self.notebook.add(self.q_panel, text="Question")
        self.q_sub_panel: tk.PanedWindow = tk.PanedWindow(self.q_panel)
        self.q_sub_panel.place(anchor=tk.CENTER, relx=0.5, rely=0.45)

        # Creates the label for the question.
        self.q_label: tk.Label = tk.Label(
            self.q_sub_panel, text="Question:", font=("Ubuntu", 20)
        )
        self.q_label.pack()

        separate(self.q_sub_panel)

        # Creates the question entry.
        self.question_sv: tk.StringVar = tk.StringVar()
        self.question_sv.trace_add(
            "write", lambda _, __, ___: self.check_entry(entry)
        )
        self.question: tk.Entry = tk.Entry(
            self.q_sub_panel, width=25, textvariable=self.question_sv,
            font=("Ubuntu", 20)
        )
        self.question.focus()
        self.question.pack()

        separate(self.q_sub_panel)

        # Creates the label for the answer.
        self.a_label: tk.Label = tk.Label(
            self.q_sub_panel, text="Top answer:", font=("Ubuntu", 20)
        )
        self.a_label.pack()

        separate(self.q_sub_panel)

        # Creates the answer entry.
        self.answer_sv: tk.StringVar = tk.StringVar()
        self.answer_sv.trace_add(
            "write", lambda _, __, ___: self.check_entry(entry)
        )
        self.answer: tk.Entry = tk.Entry(
            self.q_sub_panel, width=25, textvariable=self.answer_sv,
            font=("Ubuntu", 20)
        )
        self.answer.bind("<FocusOut>", lambda _: self.lose_focus_on_answer())
        self.answer.pack()

        # Creates the central panel for writing answers.
        self.a_panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.a_panel.pack(expand=1, fill=tk.Y)
        self.notebook.add(self.a_panel, text="Answers")
        self.a_sub_panel: tk.PanedWindow = tk.PanedWindow(self.a_panel)
        self.a_sub_panel.place(anchor=tk.CENTER, relx=0.5, rely=0.42)

        # Creates a label for the question
        self.a_static_label: tk.Label = tk.Label(
            self.a_sub_panel, text="", font=("Ubuntu", 20)
        )
        self.a_static_label.grid(row=0, column=0, columnspan=3)

        # Creates the answer entry
        self.new_answer_sv: tk.StringVar = tk.StringVar()
        self.new_answer_sv.trace_add(
            "write", lambda _, __, ___: self.check_answers()
        )

        self.answer_entry: tk.Entry = tk.Entry(
            self.a_sub_panel, font=("Ubuntu", 20), width=15,
            textvariable=self.new_answer_sv
        )
        self.answer_entry.grid(row=1, column=0)

        h_separate(self.a_sub_panel, row=1, col=1)

        # Creates a button for the answer entry
        self.add_button: tk.Button = tk.Button(
            self.a_sub_panel, text="Add", font=("Ubuntu", 20), width=10,
            command=self.add_answer, state=tk.DISABLED
        )
        self.add_button.grid(row=1, column=2)

        separate(self.a_sub_panel, 2)

        # Adds the listbox containing all answers
        self.answers: tk.Listbox = tk.Listbox(
            self.a_sub_panel, width=15, height=7, font=("Ubuntu", 20),
            exportselection=False
        )
        for possible_answer in self.handler.get_answers_for_entry(entry):
            self.answers.insert(tk.END, possible_answer)
        self.answers.grid(row=3, column=0, columnspan=2)

        # Adds the deletion button
        self.delete_button: tk.Button = tk.Button(
            self.a_sub_panel, text="Delete", font=("Ubuntu", 20), width=10,
            command=self.delete_answer, state=tk.DISABLED
        )
        self.delete_button.grid(row=3, column=2, sticky=tk.N)

        self.answers.bind(
            "<<ListboxSelect>>",
            lambda _: self.check_selection()
        )

        # Creates the central panel for naming the sheet.
        self.e_panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.e_panel.pack(expand=1, fill=tk.Y)
        self.notebook.add(self.e_panel, text="Sheets")
        self.e_sub_panel: tk.PanedWindow = tk.PanedWindow(self.e_panel)
        self.e_sub_panel.place(anchor=tk.CENTER, relx=0.5, rely=0.4)

        # Creates a label with the question displayed
        self.e_label: tk.Label = tk.Label(
            self.e_sub_panel, text="", font=("Ubuntu", 20)
        )
        self.e_label.pack()

        # Creates the sheets list
        self.sheets: tk.Listbox = tk.Listbox(
            self.e_sub_panel, selectmode=tk.MULTIPLE, width=25, height=8,
            exportselection=False, font=("Ubuntu", 20)
        )
        current_sheets = list(self.handler.get_entry_sheets(entry))
        for sheet in self.handler.get_all_sheets(from_l, to_l):
            self.sheets.insert(tk.END, sheet)
            if sheet in current_sheets:
                self.sheets.selection_set(tk.END)
        self.sheets.pack()

        # Creates the language name entry.
        self.back_button: tk.Button = tk.Button(
            self.widget.top, text="Back", width=10, font=("Ubuntu", 20),
            command=lambda: self.go_to(
                EditTranslatorEntriesInterface, from_l, to_l
            )
        )
        self.back_button.place(relx=0.01, rely=0.99, anchor=tk.SW)

        # Creates the button to progress.
        self.save_button: tk.Button = tk.Button(
            self.widget.top, text="Save", width=10, font=("Ubuntu", 20),
            state=tk.DISABLED, command=lambda: self.save_entry(entry)
        )
        self.save_button.place(anchor=tk.SE, relx=0.99, rely=0.99)

        self.question_sv.set(question)
        self.answer_sv.set(answer)

        self.bind_escape(
            (
                self.notebook, self.question, self.answer, self.answer_entry,
                self.answers, self.add_button, self.delete_button, self.sheets,
                self.back_button, self.save_button
            ), lambda: self.go_to(EditTranslatorEntriesInterface, from_l, to_l)
        )

    def lose_focus_on_answer(self) -> None:
        """
        Updates the corresponding list of answers.
        :return: None
        """
        self.answers.delete(0)
        to_add = self.answer_sv.get()
        all_answers = list(self.answers.get(0, tk.END))
        if to_add in all_answers:
            self.answers.delete(all_answers.index(to_add))
        self.answers.insert(0, self.answer_sv.get())

    def check_entry(self, old_entry: int) -> bool:
        """
        Checks if the entry is valid for creation.
        :param old_entry: int
            The entry serial number.
        :return: bool
            Whether the sheet can be saved or not.
        """
        question = self.question_sv.get().strip()
        answer = self.answer_sv.get().strip()

        # Adjusts the labels
        self.a_static_label.config(text=question)
        if self.answers.get(0, tk.END) == ('',):
            self.delete_button.config(state=tk.DISABLED)
        self.e_label.config(text=question)

        correct_lengths = 1 <= len(question) <= 80 and 1 <= len(answer) <= 80
        search = self.handler.get_entry(
            question, *self.handler.get_language_names_from_entry(old_entry)
        )
        if (
                question == ''
                or (search and search != old_entry)
                or not correct_lengths
        ):
            if self.save_button["state"] == "normal":
                self.save_button.config(state=tk.DISABLED)
            return False

        if self.save_button["state"] == "disabled":
            self.save_button.config(state=tk.NORMAL)
        return True

    def check_answers(self) -> None:
        """
        Checks if the answer can be added to the existing list.
        :return: None
        """
        existing = self.answers.get(0, tk.END)
        to_add = self.new_answer_sv.get()
        correct_lengths = 1 <= len(to_add) <= 80

        if to_add in existing or not correct_lengths:
            self.add_button.config(state=tk.DISABLED)
        else:
            self.add_button.config(state=tk.NORMAL)

    def add_answer(self) -> None:
        """
        Adds an answer to the list of answers.
        :return: None
        """
        to_add = self.new_answer_sv.get()
        self.new_answer_sv.set("")
        self.answers.insert(tk.END, to_add)
        if self.answers.get(0) == "":
            self.answers.delete(0)
            self.answer_sv.set(to_add)
        self.answer_entry.focus()

    def check_selection(self) -> None:
        """
        Checks the selected answer and activates buttons accordingly.
        :return: None
        """
        if self.answers.get(0, tk.END)[0]:
            self.delete_button.config(state=tk.NORMAL)

    def delete_answer(self) -> None:
        """
        Deletes an answer from the answers list
        :return: None
        """
        pos = self.answers.curselection()[0]
        all_answers = self.answers.get(0, tk.END)
        self.answers.delete(pos)
        if len(all_answers) == 1:
            self.answers.insert(tk.END, "")
            self.delete_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.DISABLED)
            self.answer_entry.focus()
        if pos == 0:
            self.answer_sv.set(self.answers.get(0))

        # Selects another entry if possible
        if pos == len(all_answers) - 1:
            self.answers.selection_set(pos - 1)
        else:
            self.answers.selection_set(pos)

    def save_entry(
            self, entry: int
    ) -> None:
        """
        Saves the entry.
        :param entry: int
            The serial number of the entry.
        :return: None
        """
        self.lose_focus_on_answer()
        self.handler.edit_entry(
            entry, self.question_sv.get(), self.answers.get(0, tk.END),
            list(map(self.sheets.get, self.sheets.curselection()))
        )
        self.go_to(
            EditTranslatorEntriesInterface,
            *self.handler.get_language_names_from_entry(entry)
        )

    def destroy(self) -> None:
        """
        Destroys the interface.
        :return: None
        """
        self.notebook.destroy()
        self.back_button.destroy()
        self.save_button.destroy()
        super().destroy()


class TranslatorInterface(BaseInterface):
    """
    This is the translator interface.
    """
    def __init__(self, main_widget: MainWidget, handler: SQLHandler) -> None:
        """
        Creates the test interface.
        :param main_widget: MainWidget
            The widget on which to create the test interface.
        :return: None
        """
        # Initializes the general aspects of the interface.
        super().__init__(main_widget, handler)

        # Creates the central panel.
        self.panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.panel.pack()

        # Creates the first language label.
        self.from_label: tk.Label = tk.Label(
            self.panel, text="From:", font=("Ubuntu", 20)
        )
        self.from_label.grid(row=0, column=0, sticky=tk.W)

        # Creates the first second label.
        self.to_label: tk.Label = tk.Label(
            self.panel, text="To:", font=("Ubuntu", 20)
        )
        self.to_label.grid(row=0, column=1, sticky=tk.W)

        # Creates the first list of languages.
        self.listbox_1: tk.Listbox = tk.Listbox(
            self.panel, width=15, height=9, exportselection=False,
            font=("Ubuntu", 20)
        )
        for language in self.handler.get_languages():
            self.listbox_1.insert(tk.END, language)
        self.listbox_1.focus()
        self.listbox_1.bind("<<ListboxSelect>>", self.check_both_clicked)
        self.listbox_1.grid(row=1, column=0)

        # Creates the second list of languages.
        self.listbox_2: tk.Listbox = tk.Listbox(
            self.panel, width=15, height=9, exportselection=False,
            font=("Ubuntu", 20)
        )
        for language in self.handler.get_languages():
            self.listbox_2.insert(tk.END, language)
        self.listbox_2.bind("<<ListboxSelect>>", self.check_both_clicked)
        self.listbox_2.grid(row=1, column=1)

        # Creates the new entry button.
        self.back_button: tk.Button = tk.Button(
            self.widget.top, text="Back",
            command=lambda: self.go_to(MenuInterface), width=10,
            font=("Ubuntu", 20)
        )
        self.back_button.place(relx=0.01, rely=0.99, anchor=tk.SW)

        # Creates the button to progress.
        self.advance_button: tk.Button = tk.Button(
            self.widget.top, text="Advance", command=self.advance_click,
            width=10, font=("Ubuntu", 20)
        )
        self.advance_button.config(state=tk.DISABLED)
        self.advance_button.place(anchor=tk.SE, relx=0.99, rely=0.99)

        self.bind_escape(
            (
                self.listbox_1, self.listbox_2, self.back_button,
                self.advance_button
            ),
            lambda: self.go_to(MenuInterface)
        )

    def check_both_clicked(self, _) -> None:
        """
        Activates the advance button if appropriate.
        :param _: tk.Event
            The event triggering the function.
        :return: None
        """
        if (
            self.listbox_1.curselection()
            and self.listbox_2.curselection()
            and self.listbox_1.curselection() != self.listbox_2.curselection()
            and self.advance_button["state"] == "disabled"
        ):
            self.advance_button.config(state=tk.NORMAL)
        elif (
            self.advance_button["state"] == "normal"
            and self.listbox_1.curselection() == self.listbox_2.curselection()
        ):
            self.advance_button.config(state=tk.DISABLED)

    def advance_click(self) -> None:
        """
        Advances to the test.
        :return: None
        """
        # Raises an error if the button ought to be disabled.
        if (
                not self.listbox_1.curselection()
                or not self.listbox_2.curselection()
                or self.listbox_1.curselection()
                == self.listbox_2.curselection()
                or self.advance_button["state"] == "disabled"
        ):
            raise UserWarning("Advance button triggered when ineligible.")

        self.go_to(
            PickSheetInterface,
            self.listbox_1.get(self.listbox_1.curselection()),
            self.listbox_2.get(self.listbox_2.curselection())
        )

    def destroy(self) -> None:
        """
        Destroys the interface.
        :return: None
        """
        self.panel.destroy()
        self.back_button.destroy()
        self.advance_button.destroy()
        super().destroy()


class PickSheetInterface(BaseInterface):
    """
    This is the sheet-picking interface.
    """
    def __init__(
            self, main_widget: MainWidget, handler: SQLHandler, from_l: str,
            to_l: str
    ) -> None:
        """
        Creates the sheet-picking interface.
        :param main_widget: MainWidget
            The widget on which to create the test interface.
        :return: None
        """
        # Initializes the general aspects of the interface.
        super().__init__(main_widget, handler)

        # Creates the central panel.
        self.panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.panel.pack()

        # Creates the label for sheet selection.
        self.label: tk.Label = tk.Label(
            self.panel, text="Pick a sheet:", font=("Ubuntu", 20)
        )
        self.label.pack()

        # Creates the first list of languages.
        self.listbox: tk.Listbox = tk.Listbox(
            self.panel, width=30, height=9, exportselection=False,
            font=("Ubuntu", 20)
        )
        for sheet in self.handler.get_all_sheets(from_l, to_l, sort=True):
            self.listbox.insert(tk.END, sheet)
            if self.handler.get_sheet_complete(from_l, to_l, sheet):
                self.listbox.itemconfig(tk.END, fg="green")
        self.listbox.bind("<<ListboxSelect>>", lambda _: self.select_sheet(
            from_l, to_l
        ))
        self.listbox.focus()
        self.listbox.pack()

        # Creates the new entry button.
        self.back_button: tk.Button = tk.Button(
            self.widget.top, text="Back",
            command=lambda: self.go_to(TranslatorInterface), width=10,
            font=("Ubuntu", 20)
        )
        self.back_button.place(relx=0.01, rely=0.99, anchor=tk.SW)

        # Creates the button to progress.
        self.advance_button: tk.Button = tk.Button(
            self.widget.top, text="Advance", command=lambda: self.go_to(
                TestInterface, self.handler.get_sheet(
                    self.listbox.get(self.listbox.curselection()), from_l, to_l
                )
            ),
            width=10, font=("Ubuntu", 20)
        )
        self.advance_button.config(state=tk.DISABLED)
        self.advance_button.place(anchor=tk.SE, relx=0.99, rely=0.99)

        self.bind_escape(
            (self.listbox, self.back_button, self.advance_button),
            lambda: self.go_to(TranslatorInterface)
        )

    def select_sheet(self, from_l: str, to_l: str) -> None:
        """
        Allows the user to advance.
        :return: None
        """
        selection = self.listbox.curselection()

        if selection and self.handler.get_entries_from_sheet(
            self.listbox.get(self.listbox.curselection()), from_l, to_l

        ):
            self.advance_button.config(state=tk.NORMAL)
        else:
            self.advance_button.config(state=tk.DISABLED)

    def destroy(self) -> None:
        """
        Destroys the interface.
        :return: None
        """
        self.panel.destroy()
        self.back_button.destroy()
        self.advance_button.destroy()
        super().destroy()


class TestInterface(BaseInterface):
    """This is the test interface."""
    def __init__(
            self, main_widget: MainWidget, handler: SQLHandler, sheet_id: int
    ) -> None:
        """Creates the test interface.
        :param MainWidget main_widget:
            The widget on which to create the test interface.
        :return: None
        """

        # Initializes the general aspects of the interface.
        super().__init__(main_widget, handler)

        # Remembers what animation iteration the test widget is on.
        self.i: int = 0
        self.waiting: bool = False

        # Refreshes all the entries
        self.handler.refresh_entries()

        # Creates the central panel.
        self.panel: tk.PanedWindow = tk.PanedWindow(self.widget.top)
        self.panel.place(anchor=tk.CENTER, relx=0.5, rely=0.5)

        # Creates a progress bar on the right-hand side of the window.
        self.fake_panel: tk.Canvas = tk.Canvas(self.panel)
        self.fake_panel.grid(
            row=0, column=0
        )

        self.panel.grid_columnconfigure(1, weight=0)
        self.panel.grid_columnconfigure(0, weight=1)

        # Creates a progress bar on the right-hand side of the window.
        self.progress_bar: tk.Canvas = tk.Canvas(
            self.panel, width=20, bd=1, highlightbackground="black"
        )
        self.progress_bar.config(bg='white')
        self.progress_bar.grid(
            row=0, column=1
        )

        self.panel.bind("<Configure>", self.resize_window)

        # Places an image at the bottom of the window.
        self.star_img: tk.PhotoImage = tk.PhotoImage(file=path.join(
            path.dirname(path.realpath(__file__)), "images", "star.png"
        ))
        self.blank_img: tk.PhotoImage = tk.PhotoImage(file=path.join(
            path.dirname(path.realpath(__file__)), "images", "blank.png"
        ))

        self.response: tk.Label = tk.Label(
            self.widget.top, text="", font=("Ubuntu", 20)
        )
        self.response.place(
            anchor=tk.CENTER, relx=0.5, rely=0.5, y=75
        )

        # Creates a minor panel for the buttons.
        self.minor_panel: tk.PanedWindow = tk.PanedWindow(self.panel)
        self.minor_panel.place(anchor=tk.CENTER, relx=0.5, rely=0.5)

        # Records which words have been tested recently.
        self.recent: Deque[int] = deque(maxlen=3)

        # Remembers the current word being tested.
        self.entry: int
        self.question: str
        self.points: int
        self.needed: int
        self.so_far: int
        self.entry, self.question, self.points, self.needed, self.so_far = (
            self.pick_word(sheet_id)
        )

        self.reattempt: bool = False

        # Creates the hint at the top of the screen.
        self.label: tk.Label = tk.Label(
            self.minor_panel, text=self.question, font=("Ubuntu", 20)
        )
        self.label.pack()

        # Creates an entry for the user to type into.
        self.string_var: tk.StringVar = tk.StringVar()
        self.e1: tk.Entry = tk.Entry(
            self.minor_panel, bd=1, textvariable=self.string_var,
            font=("Ubuntu", 20)
        )
        self.e1.focus()
        self.e1.bind("<Return>", lambda event: self.accept_answer(sheet_id))
        self.e1.bind("<Escape>", lambda event: self.go_to(
            PickSheetInterface, *self.handler.get_language_names_from_entry(
                self.entry
            )
        ))
        self.e1.pack()

        # Creates a small cluster of stars at the bottom-left of the
        # screen.
        self.stars: tk.Canvas = tk.Canvas(self.panel, width=180, height=40)
        self.stars.place(anchor=tk.SW, relx=0, rely=1)
        self.draw_stars()

    def resize_window(self, _) -> None:
        """
        Adapts the progress bar appropriately.
        :return: None
        """
        screen_width = self.widget.top.winfo_width()
        screen_height = self.widget.top.winfo_height()
        self.fake_panel.config(
            width=screen_width - 20, height=screen_height + 1
        )
        self.progress_bar.config(height=screen_height + 1)
        self.refresh_bar()

    def animate_bar(self, sheet_id: int, so_far: int) -> None:
        """
        Animates the progress bar.
        :return: None
        """
        self.i += 1
        if self.i < 500:
            self.e1.after(1, lambda: self.animate_bar(sheet_id, so_far))
            self.refresh_bar(so_far)
        elif so_far >= -self.needed:
            self.e1.after(200, lambda: self.new_entry(sheet_id))
        else:
            self.waiting = True

    def refresh_bar(self, so_far: Optional[int] = None) -> None:
        """
        Updates the progress bar.
        :return: None
        """
        screen_height = self.widget.top.winfo_height()
        self.progress_bar.delete(tk.ALL)

        lines = linspace(1, screen_height + 2, self.needed + 1, rounded=True)

        if self.so_far == 1:
            if so_far is None:
                self.progress_bar.create_rectangle(
                    0, lines[1] + 2, 20, lines[-1] - 1,
                    fill='green', outline=""
                )
            elif so_far == 2:
                self.progress_bar.create_rectangle(
                    0, (lines[1] + 2) + ((lines[0] + 2) - (lines[1] + 2))
                    * self.i / 500, 20, lines[-1] - 1, fill='green',
                    outline=""
                )
            elif so_far == -3:
                green = '#%02x%02x%02x' % (
                    round(255 * self.i / 500),
                    round(128 + 127 * self.i / 500),
                    round(255 * self.i / 500)
                )
                red = '#%02x%02x%02x' % (
                    255,
                    round(255 - 255 * self.i / 500),
                    round(255 - 255 * self.i / 500)
                )
                self.progress_bar.create_rectangle(
                    0, lines[1] + 2 + ((lines[2] - 1) - (lines[1] + 2))
                    * self.i / 500, 20, lines[-1] - 1,
                    fill=green, outline=""
                )
                self.progress_bar.create_rectangle(
                    0, lines[0] + 2, 20,
                    lines[1] + 2 + ((lines[-1] - 1) - (lines[1] + 2))
                    * self.i / 500 - 3,
                    fill=red, outline=""
                )
        elif self.so_far == 2:
            if so_far is None or so_far == 2:
                self.progress_bar.create_rectangle(
                    0, lines[0] + 2, 20, lines[-1] - 1, fill='green',
                    outline=""
                )
            else:
                green = '#%02x%02x%02x' % (
                    round(255 * self.i / 500),
                    round(128 - 128 * self.i / 500),
                    0
                )
                self.progress_bar.create_rectangle(
                    0, lines[0] + 2, 20, lines[-1] - 1, fill=green,
                    outline=""
                )
        elif self.so_far < 0:
            if so_far is None or so_far == self.so_far - 1:
                self.progress_bar.create_rectangle(
                    0, lines[0] + 2, 20, lines[-self.so_far] - 1,
                    fill='red', outline=""
                )
                if self.so_far + self.needed > 0:
                    self.progress_bar.create_rectangle(
                        0, lines[-self.so_far] + 2, 20, screen_height + 1,
                        fill='orange', outline=""
                    )
            elif so_far > self.so_far:
                top = (
                    lines[0] + 2 if so_far >= 0
                    else lines[-1 - self.so_far] - 1
                )
                self.progress_bar.create_rectangle(
                    0, lines[0] + 2, 20,
                    lines[-self.so_far] - 1 +
                    (
                            top - (lines[-self.so_far] - 1)
                    ) * self.i / 500,
                    fill='red', outline=""
                )
                self.progress_bar.create_rectangle(
                    0,
                    lines[-self.so_far] + 2 +
                    (
                            (lines[-1 - self.so_far] + 2)
                            - (lines[-self.so_far] + 2)
                    ) * self.i / 500, 20, screen_height + 1,
                    fill='orange', outline=""
                )
            elif so_far < self.so_far:
                self.progress_bar.create_rectangle(
                    0, lines[0] + 2, 20,
                    lines[-self.so_far] - 1 +
                    (
                            (lines[-1] - 1)
                            - (lines[-self.so_far] - 1)
                    ) * self.i / 500,
                    fill='red', outline=""
                )
                self.progress_bar.create_rectangle(
                    0,
                    lines[-self.so_far] + 2 +
                    (
                            (lines[-1] - 1)
                            - (lines[-self.so_far] + 2)
                    ) * self.i / 500, 20, lines[-1] - 1,
                    fill='orange', outline=""
                )
        elif self.needed > 2:
            if so_far is None or so_far > 2:
                self.progress_bar.create_rectangle(
                    0, lines[0] + 2, 20, lines[-1] - 1, fill='orange',
                    outline=""
                )
            elif so_far == 2:
                orange = '#%02x%02x%02x' % (
                    round(255 - 255 * self.i / 500),
                    round(165 - 37 * self.i / 500),
                    0
                )
                self.progress_bar.create_rectangle(
                    0, lines[0] + 2, 20, lines[-1] - 1, fill=orange, outline=""
                )
            elif so_far < 0:
                self.progress_bar.create_rectangle(
                    0, lines[0] + 2, 20,
                    lines[0] + 2 +
                    ((lines[-1] - 1) - (lines[0] + 2)) * self.i / 500,
                    fill='red', outline=""
                )
                self.progress_bar.create_rectangle(
                    0,
                    lines[0] + 2 +
                    (
                            (lines[-1] - 1)
                            - (lines[0] + 2)
                    ) * self.i / 500, 20, lines[-1] - 1,
                    fill='orange', outline=""
                )
        elif so_far == 1:
            self.progress_bar.create_rectangle(
                0, lines[-1] - 1 + ((lines[1] + 2) - (lines[-1] - 1))
                * self.i / 500, 20, screen_height + 1, fill='green',
                outline=""
            )
        elif so_far == -3:
            red = '#%02x%02x%02x' % (
                255,
                round(255 - 255 * self.i / 500),
                round(255 - 255 * self.i / 500)
            )
            self.progress_bar.create_rectangle(
                0, lines[0] + 2, 20, lines[-1] - 1, fill=red, outline=""
            )

        # Draws the different lines for the bar.
        for line in lines[1:-1]:
            self.progress_bar.create_line(0, line, 20, line)

    @staticmethod
    def is_close(str_1: str, str_2: str) -> bool:
        """
        Figures out whether or not the two strings are very similar.
        :param str_1: str
            The first string.
        :param str_2: str
            The second string.
        :return: bool
            Whether they close or not.
        """
        return SequenceMatcher(None, str_1, str_2).ratio() >= 0.9

    def accept_answer(self, sheet_id: int) -> None:
        """
        Clears the entry made by the user.
        :return: None
        """
        # Does stuff if necessary
        if self.i == 500 and self.waiting:
            self.i = 0
            self.waiting = False
            self.new_entry(sheet_id)
            return
        # Ignores if animating
        elif self.i != 0:
            return

        attempt = self.e1.get().strip()
        match = 0
        for possible_answer in self.handler.get_answers_for_entry(self.entry):
            if attempt == possible_answer:
                match = 2
                break
            elif (
                    not self.reattempt and not match
                    and self.is_close(attempt, possible_answer)
            ):
                match = 1

        if match == 0:
            show = self.handler.get_entry_question_and_answer(self.entry)[1]
            self.response.config(text=f"Wrong:\n{show}")
        elif match == 1:
            self.response.config(text="Check your spelling!")
            self.reattempt = True
            return
        elif match == 2:
            self.response.config(text="Correct!")

        self.reattempt = False

        so_far = self.handler.update_entry(self.entry, match == 2)[2]
        self.draw_stars(so_far)

        self.e1.config(state=tk.DISABLED)
        self.e1.after(1, lambda: self.animate_bar(sheet_id, so_far))

    def new_entry(self, sheet_id: int) -> None:
        """
        Updates a new entry.
        :param sheet_id: int
            The id for the vocab sheet.
        :return: None
        """
        self.e1.config(state=tk.NORMAL)
        self.response.config(text="")
        self.e1.delete(0, tk.END)
        self.entry, self.question, self.points, self.needed, self.so_far = (
            self.pick_word(sheet_id, self.entry)
        )
        self.i = 0
        self.refresh_bar()

        # Updates the text displayed for the question.
        self.label['text'] = self.question

        self.draw_stars()

    def draw_stars(self, so_far: Optional[int] = None) -> None:
        """
        Draws the stars in the bottom-right of the screen.
        :param so_far: Optional[int]
            The updated so_far value.
        :return: None
        """
        self.stars.delete(tk.ALL)
        no_stars = self.points + (
            1 if (self.so_far if so_far is None else so_far) == 2 else 0
        )
        for star in range(self.points + 1):
            img = self.star_img if star < no_stars else self.blank_img
            self.stars.create_image(
                5 + 35 * star, 5, anchor=tk.NW, image=img
            )

    def pick_word(
            self, sheet_id: int, current: Optional[int] = None
    ) -> Tuple[int, str, int, int, int]:
        """
        Picks a word to do next.
        :param sheet_id: int
            The sheet being used.
        :param current: Optional[str]
            If given, current represents the word that was last tested.
        :return: str
            The new word to choose.
        """
        # Remembers previous word.
        if current is not None:
            self.recent.append(current)

        # Gets the entry to be performed
        return self.handler.get_next_entry(sheet_id, self.recent)

    def destroy(self) -> None:
        """
        Destroys the interface.
        :return: None
        """
        self.panel.destroy()
        self.response.destroy()
