# itertools is needed for the repeating function
from itertools import chain, repeat

# Path is needed to find the home folder
from pathlib import Path

# sqlite3 is needed to interact with the database.
import sqlite3 as sql

# typing is needed for the type annotation.
from typing import Deque, Iterable, List, Tuple, Union, Set


class SQLHandler:
    """
    This enables the application to retrieve data from and write to the
    database.
    """
    def __init__(self) -> None:
        """
        Connects to the SQLite database.
        """
        home = Path.home()
        path = Path(home, ".prosakart")
        if len(list(home.glob(".prosakart"))) == 0:
            path.mkdir(parents=True, exist_ok=True)
        db_file = str(Path(path, "vocab.db"))
        self.conn = sql.connect(db_file)
        self.cur = self.conn.cursor()
        self.create_db(db_file)

    def create_db(self, file) -> None:
        """
        Structures the database.
        :return: None
        """
        # Allows foreign keys to be used.
        self.conn.execute("PRAGMA foreign_keys = ON;")

        # Creates the languages table.
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS languages (
                language INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR (40) NOT NULL,
                CONSTRAINT one_name UNIQUE (name)
            );
            """
        )

        # Creates the translators table.
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS translators (
                translator INTEGER PRIMARY KEY AUTOINCREMENT,
                from_l INTEGER NOT NULL
                    REFERENCES languages (language)
                        ON DELETE CASCADE,
                to_l INTEGER NOT NULL
                    REFERENCES languages (language)
                        ON DELETE CASCADE,
                CONSTRAINT one_translation UNIQUE (from_l, to_l)
            );
            """
        )

        # Creates the sheets table.
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sheets (
                sheet INTEGER PRIMARY KEY AUTOINCREMENT,
                translator INTEGER
                    REFERENCES translators(translator)
                        ON DELETE CASCADE,
                name VARCHAR (80),
                CONSTRAINT name UNIQUE (translator, name)
            );
            """
        )

        # Creates the entries table.
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                entry INTEGER PRIMARY KEY AUTOINCREMENT,
                translator INTEGER
                    REFERENCES translators(translator)
                        ON DELETE CASCADE,
                question VARCHAR (80),
                points TINYINT DEFAULT 0,
                needed TINYINT DEFAULT 2,
                so_far TINYINT DEFAULT 0,
                completed CHAR (23),
                CONSTRAINT one_question_per_entry UNIQUE
                    (translator, question)
            );
            """
        )

        # Creates the solutions table.
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS solutions (
                solution INTEGER PRIMARY KEY AUTOINCREMENT,
                entry INTEGER REFERENCES entries(entry)
                    ON DELETE CASCADE,
                text VARCHAR (80),
                displayed BOOL,
                CONSTRAINT one_answer_per_question UNIQUE
                    (entry, text)
            );
            """
        )

        # Creates the mentions table.
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mentions (
                mention INTEGER PRIMARY KEY AUTOINCREMENT,
                sheet INTEGER REFERENCES sheets(sheet)
                    ON DELETE CASCADE,
                entry INTEGER REFERENCES entries(entry)
                    ON DELETE CASCADE,
                CONSTRAINT name UNIQUE (sheet, entry)
            );
            """
        )
        # Refreshes the connection. This prevents certain errors.
        self.conn.commit()
        self.conn.close()
        self.conn = sql.connect(file)
        self.cur = self.conn.cursor()
        self.conn.execute("PRAGMA foreign_keys = ON;")

    def close(self) -> None:
        """
        Saves the database.
        :return: None
        """
        self.conn.commit()
        self.conn.close()

    def get_languages(self, *, sort: bool = True) -> Iterable[str]:
        """
        Yields the languages.
        :param sort: bool
            Whether to sort the results or not.
        :return: None
        """
        self.cur.execute("SELECT name FROM languages;")
        results = map(lambda x: x[0], self.cur.fetchall())
        return sorted(
            results, key=lambda x: x.lower()
        ) if sort else results

    def get_language(
            self, name: str, *, r_none: bool = False
    ) -> Union[int, None]:
        """
        Finds the serial number for the given language.
        :param name: str
            The name of the language
        :param r_none: bool
            Whether to return None if no value is found. If set to
            False and no row is found, raises an error.
        :return: int
            The serial number of the language.
        """
        self.cur.execute(
            """
            SELECT language FROM languages
            WHERE name = ?;
            """, (name,)
        )
        row = self.cur.fetchone()
        if row is None:
            if r_none:
                return None
            else:
                raise ValueError(
                    f"There is no language with name {name}."
                )
        return row[0]

    def add_language(self, name: str) -> None:
        """
        Adds a language to the list.
        :param name: The name of the language to be added.
        :return: None
        """
        self.conn.execute("INSERT INTO languages (name) VALUES (?);", (name,))

    def change_language(self, old_name: str, new_name) -> None:
        """
        Changes a language from the list.
        :param old_name: str
            The name of the language to be changed.
        :param new_name: str
            The new name of the language.
        :return: None
        """
        self.conn.execute(
            "UPDATE languages SET name = ? WHERE name = ?;",
            (new_name, old_name)
        )

    def delete_language(self, name: str) -> None:
        """
        Changes a language from the list.
        :param name: str
            The name of the language to be deleted.
        :return: None
        """
        self.conn.execute(
            "DELETE FROM languages WHERE name = ?;", (name,)
        )

    def get_translator(
            self, from_serial: int, to_serial: int, create: bool = True
    ) -> int:
        """
        Finds the serial number for the translator corresponding to the
        two provided languages.
        :param from_serial: int
            The serial number for the language being translated.
        :param to_serial: int
            The serial number for the language of translation.
        :param create: bool
            If the translator does not exist for that combination of
            languages and create is set to True, then the translator is
            created. If create is set to False in that circumstance,
            an error is raised.
        :return: int
            The serial number for the translator.
        """
        # Write command for finding translator.
        fetch_command = """
        SELECT translator FROM translators
        WHERE from_l = ?
            AND to_l = ?;
        """
        # Attempt to find translator.
        self.cur.execute(fetch_command, (from_serial, to_serial))
        row = self.cur.fetchone()

        # If there is no such translator in the database.
        if row is None:
            # Creates the translator and finds the serial number.
            if create:
                self.cur.execute("SELECT * FROM languages;")
                self.conn.execute(
                    """
                    INSERT INTO translators (from_l, to_l) VALUES
                        (?, ?);
                    """, (from_serial, to_serial)
                )
                self.cur.execute(fetch_command, (from_serial, to_serial))
                row = self.cur.fetchone()

            # Raises an error.
            else:
                raise ValueError(
                    f"There is no translator with input serial {from_serial}"
                    + f"and output serial {to_serial}."
                )

        # Returns the serial number of the translator.
        return row[0]

    def get_translator_from_language_names(
            self, from_l: str, to_l: str
    ) -> int:
        """
        Returns the serial number of the translator given the languages
        of interest.
        :param from_l: str
            The name of the language that is being translated.
        :param to_l: str
            The name of the language of translation.
        :return: int
            The serial number of the translator.
        """
        query = """
            SELECT translator
            FROM translators
            INNER JOIN languages AS l1
                ON l1.language = from_l
            INNER JOIN languages AS l2
                ON l2.language = to_l
            WHERE l1.name = ?
                AND l2.name = ?;
            """
        self.cur.execute(query, (from_l, to_l))
        result = self.cur.fetchone()

        if result is None:
            self.cur.execute(
                """
                INSERT INTO translators (from_l, to_l) VALUES
                    (?, ?);
                """, (self.get_language(from_l), self.get_language(to_l))
            )

            self.cur.execute(
                query, (from_l, to_l)
            )
            result = self.cur.fetchone()

        return result[0]

    def get_language_names_from_entry(
            self, entry: int
    ) -> Tuple[str, str]:
        """
        Returns the serial number of the translator given the entry.
        :param entry: int
            The serial number of the entry.
        :return: Tuple[str, str]
            The names of the two languages.
        """
        self.cur.execute(
            """
            SELECT l1.name, l2.name
            FROM entries
            INNER JOIN translators
                ON entries.translator = translators.translator
            INNER JOIN languages AS l1
                ON l1.language = from_l
            INNER JOIN languages AS l2
                ON l2.language = to_l
            WHERE entry = ?;
            """, (entry,)
        )
        return self.cur.fetchone()

    def add_sheet(
            self, name: str, from_l: str, to_l: str, entries: Set[str]
    ) -> None:
        """
        Adds the sheet for the given translator.
        :return: None
        """
        trans_s = self.get_translator_from_language_names(from_l, to_l)
        self.conn.execute(
            """
            INSERT INTO sheets (translator, name) VALUES
                (?, ?);
            """, (trans_s, name)
        )
        sheet_s = self.get_sheet(name, from_l, to_l)

        # Adds entries if there are any to be added.
        if entries:
            self.cur.execute(
                f"""
                SELECT entry FROM entries WHERE translator = ?
                AND ({" OR ".join(["question = ?"] * len(entries))});
                """, (trans_s, *entries)
            )

            self.conn.execute(
                f"""
                INSERT INTO mentions (entry, sheet) VALUES
                    {", ".join(["(?, ?)"] * len(entries))};
                """, sum(zip(map(
                    lambda x: x[0], self.cur.fetchall()
                ), repeat(sheet_s)), ())
            )

    def get_all_sheets(
            self, from_l: str, to_l: str, *, sort: bool = True
    ) -> Iterable[str]:
        """
        Returns the sheets relevant to a translator.
        :param from_l: str
            The name of the language that is being translated.
        :param to_l: str
            The name of the language of translation.
        :param sort: bool
            Whether the list should be sorted or not.
        :return: None
        """
        self.cur.execute(
            """
            SELECT sheets.name FROM sheets
            INNER JOIN translators
                ON translators.translator = sheets.translator
            INNER JOIN languages AS l1
                ON translators.from_l = l1.language
            INNER JOIN languages AS l2
                ON translators.to_l = l2.language
            WHERE l1.name = ?
                AND l2.name = ?;
            """, (from_l, to_l)
        )
        results = map(lambda x: x[0], self.cur.fetchall())
        return sorted(
            results, key=lambda x: x.lower()
        ) if sort else results

    def get_sheets_for_entry(
            self, entry: int, *, sort: bool = True
    ) -> Iterable[str]:
        """
        Returns the sheets to which an entry can be added.
        :param entry: int
            The serial number of the entry.
        :param sort: bool
            Whether the list should be sorted or not.
        :return: None
        """
        self.cur.execute(
            """
            SELECT name
            FROM sheets
            INNER JOIN translators
                ON translators.translator = sheets.translator
            INNER JOIN entries
                ON entries.translator = translators.translator
            WHERE entry = ?;
            """, (entry,)
        )
        results = map(lambda x: x[0], self.cur.fetchall())
        return sorted(
            results, key=lambda x: x.lower()
        ) if sort else results

    def get_entry_sheets(
            self, entry: int, *, sort: bool = True
    ) -> Iterable[str]:
        """
        Returns the sheets in which an entry resides.
        :param entry: int
            The serial number of the entry.
        :param sort: bool
            Whether the list should be sorted or not.
        :return: None
        """
        self.cur.execute(
            """
            SELECT name FROM mentions
            INNER JOIN entries ON entries.entry = mentions.entry
            INNER JOIN sheets ON sheets.sheet = mentions.sheet
            WHERE entries.entry = ?;
            """, (entry,)
        )
        results = map(lambda x: x[0], self.cur.fetchall())
        return sorted(
            results, key=lambda x: x.lower()
        ) if sort else results

    def get_sheet(
            self, name: str, from_l: str, to_l: str, *, r_none: bool = False
    ) -> Union[int, None]:
        """
        Finds the serial number for the given sheet.
        :param name: str
            The name of the sheet.
        :param from_l: str
            The name of the language being translated from.
        :param to_l: str
            The name of the language being translated to.
        :param r_none: bool
            Whether to return None if no value is found. If set to
            False and no row is found, raises an error.
        :return: int
            The serial number of the sheet.
        """
        self.cur.execute(
            """
            SELECT sheet FROM sheets
            INNER JOIN translators
                ON translators.translator = sheets.translator
            INNER JOIN languages AS l1
                ON translators.from_l = l1.language
            INNER JOIN languages AS l2
                ON translators.to_l = l2.language
            WHERE l1.name = ?
                AND l2.name = ?
                AND sheets.name = ?;
            """, (from_l, to_l, name)
        )
        row = self.cur.fetchone()
        if row is None:
            if r_none:
                return None
            else:
                raise ValueError(
                    f"There is no relevant language with name {name}."
                )
        return row[0]

    def get_sheet_complete(self, from_l: str, to_l: str, sheet: str) -> bool:
        """
        Finds whether or not a sheet has been completed (cannot receive
        any more stars at the present moment).
        :param str from_l: The name of the language being translated
            from.
        :param str to_l: The name of the language being translated to.
        :param str sheet: The sheet's name.
        :rtype: bool
        :return: Whether it is complete or not.
        """
        self.cur.execute(
            f"""
            SELECT COUNT(so_far) FROM SHEETS
            INNER JOIN translators
                ON translators.translator = sheets.translator
            INNER JOIN languages AS l1
                ON translators.from_l = l1.language
            INNER JOIN languages AS l2
                ON translators.to_l = l2.language
            INNER JOIN entries
            INNER JOIN mentions
                ON mentions.entry = entries.entry
                AND sheets.sheet = mentions.sheet
            WHERE l1.name = ?
                AND l2.name = ?
                AND sheets.name = ?
                AND entries.so_far != 2;
            """, (from_l, to_l, sheet)
        )
        return not bool(self.cur.fetchone()[0])

    def get_sheets(
            self, names: List[str], from_l: str, to_l: str
    ) -> Iterable[int]:
        """
        Finds the serial number for the given sheet.
        :param names: List[str]
            The names of the sheets.
        :param from_l: str
            The name of the language being translated from.
        :param to_l: str
            The name of the language being translated to.
        :return: int
            The serial number of the sheet.
        """
        self.cur.execute(
            f"""
            SELECT sheet FROM sheets
            INNER JOIN translators
                ON translators.translator = sheets.translator
            INNER JOIN languages AS l1
                ON translators.from_l = l1.language
            INNER JOIN languages AS l2
                ON translators.to_l = l2.language
            WHERE l1.name = ?
                AND l2.name = ?
                AND ({" OR ".join(["sheets.name = ?"] * len(names))});
            """, (from_l, to_l, *names)
        )
        return map(lambda x: x[0], self.cur.fetchall())

    def change_sheet(
            self, old_name: str, new_name, from_l: str, to_l: str,
            entries: Set[str]
    ) -> None:
        """
        Changes a new language from the list.
        :param old_name: str
            The name of the language to be changed.
        :param new_name: str
            The new name of the language.
        :param from_l: str
            The name of the language from which to translate.
        :param to_l: str
            The name of the language to which to translate.
        :param entries: Set[str]
            The questions to be placed in the sheet.
        :return: None
        """
        trans_s = self.get_translator_from_language_names(from_l, to_l)
        sheet_s = self.get_sheet(old_name, from_l, to_l)
        self.conn.execute(
            """
            UPDATE sheets SET name = ?
            WHERE sheet = ?;
            """,
            (new_name, sheet_s)
        )

        # Finds all entries currently in the sheet
        self.cur.execute(
            """
            SELECT entry FROM mentions
            WHERE sheet = ?;
            """, (sheet_s,)
        )
        current = set(x[0] for x in self.cur.fetchall())

        # Finds all entries to be in the sheet
        if entries:
            self.cur.execute(
                f"""
                SELECT entry FROM entries
                WHERE translator = ?
                    AND ({" OR ".join(["question = ?"] * len(entries))});
                """, (trans_s, *entries)
            )
            entries_s = set(x[0] for x in self.cur.fetchall())
        else:
            entries_s = set()

        to_add = entries_s.difference(current)
        to_remove = current.difference(entries_s)

        if to_add:
            self.conn.execute(
                f"""
                INSERT INTO mentions (entry, sheet) VALUES
                    {", ".join(["(?, ?)"] * len(to_add))};
                """, sum(zip(to_add, repeat(sheet_s)), ())
            )

        if to_remove:
            self.conn.execute(
                f"""
                DELETE FROM mentions
                WHERE sheet = ?
                AND ({" OR ".join(["entry = ?"] * len(to_remove))});
                """, (sheet_s, *to_remove)
            )

    def delete_sheet(self, name: str, from_l: str, to_l: str) -> None:
        """
        Changes a language from the list.
        :param name: str
            The name of the language to be deleted.
        :param from_l: str
            The language from which to be translated.
        :param to_l: str
            The language to which to be translated.
        :return: None
        """
        trans_s = self.get_translator_from_language_names(from_l, to_l)
        self.conn.execute(
            """
            DELETE FROM sheets
            WHERE translator = ?
                AND name = ?;
            """, (trans_s, name)
        )

    def add_entry(
            self, from_l: str, to_l: str, question: str, answers: List[str],
            sheets: List[str]
    ) -> None:
        """
        Adds an entry to the database.
        :param from_l: str
            The name of the language being translated from.
        :param to_l: str
            The name of the language being translated to.
        :param question: str
            The text of the question.
        :param answers: str
            The text of the answers.
        :param sheets: List[str]
            The names of the sheets to which the entry is added.
        :return: None
        """
        trans_s = self.get_translator_from_language_names(from_l, to_l)

        # Adds the entry.
        self.conn.execute(
            """
            INSERT INTO entries (translator, question) VALUES
                (?, ?);
            """, (trans_s, question)
        )

        # Finds the entry's new serial number.
        self.cur.execute(
            """
            SELECT entry FROM entries
            WHERE translator = ? AND question = ?;
            """, (trans_s, question)
        )
        entry = self.cur.fetchone()[0]

        # Gives the entries its answers.
        solutions_query = f"""
        INSERT INTO solutions (entry, text, displayed) VALUES
            {", ".join(["(?, ?, ?)"] * len(answers))};
        """
        self.conn.execute(
            solutions_query, sum(zip(
                repeat(entry), answers, chain((True,), repeat(False))
            ), ())
        )

        if sheets:
            # Finds the serial number of each sheet
            sheet_serials = self.get_sheets(sheets, from_l, to_l)

            # Adds the entry to its respective sheets.
            mentions_query = f"""
            INSERT INTO mentions (entry, sheet) VALUES
                {", ".join(["(?, ?)"] * len(sheets))};
            """
            self.conn.execute(
                mentions_query, sum(zip(
                    repeat(entry), sheet_serials
                ), ())
            )

    def search_entries(
            self, text: str, from_l: str, to_l: str
    ) -> Union[List[Tuple[int, str]], None]:
        """
        Finds the serial number for the given entry.
        :param text: str
            The text in the search query.
        :param from_l: str
            The name of the language being translated from.
        :param to_l: str
            The name of the language being translated to.
        :return: Union[List[Tuple[int, str]], None]
            The serial number of the language.
        """
        self.cur.execute(
            """
            SELECT DISTINCT entries.entry, question FROM solutions
            INNER JOIN entries ON entries.entry = solutions.entry
            INNER JOIN translators
                ON translators.translator = entries.translator
            INNER JOIN languages AS l1
                ON translators.from_l = l1.language
            INNER JOIN languages AS l2
                ON translators.to_l = l2.language
            WHERE (INSTR(question, ?) OR INSTR(text, ?))
                AND l1.name = ?
                AND l2.name = ?;
            """, (text, text, from_l, to_l)
        )
        return sorted(self.cur.fetchall(), key=lambda x: x[1].lower())

    def get_entry(
            self, question: str, from_l: str, to_l: str
    ) -> Union[int, None]:
        """
        Finds the serial number for the given entry.
        :param question: str
            The text in the question.
        :param from_l: str
            The name of the language being translated from.
        :param to_l: str
            The name of the language being translated to.
        :return: int
            The serial number of the entry.
        """
        self.cur.execute(
            """
            SELECT entry from entries
            INNER JOIN translators
                ON entries.translator = translators.translator
            INNER JOIN languages AS l1 ON l1.language = from_l
            INNER JOIN languages AS l2 ON l2.language = to_l
            WHERE question = ?
                AND l1.name = ?
                AND l2.name = ?;
            """, (question, from_l, to_l)
        )
        result = self.cur.fetchone()
        return result if result is None else result[0]

    def get_entries_from_sheet(
            self, name: str, from_l: str, to_l: str
    ) -> List[Tuple[int, str]]:
        """
        Finds the serial number for the given entry.
        :param name: str
            The name of the sheet.
        :param from_l: str
            The name of the language being translated from.
        :param to_l: str
            The name of the language being translated to.
        :return: List[int]
            The serial number of the entry.
        """
        self.cur.execute(
            """
            SELECT entries.entry, entries.question from entries
            INNER JOIN translators
                ON entries.translator = translators.translator
            INNER JOIN languages AS l1 ON l1.language = from_l
            INNER JOIN languages AS l2 ON l2.language = to_l
            INNER JOIN sheets
                ON sheets.translator = translators.translator
            INNER JOIN mentions
                ON mentions.sheet = sheets.sheet
                    AND mentions.entry = entries.entry
            WHERE sheets.name = ?
                AND l1.name = ?
                AND l2.name = ?;
            """, (name, from_l, to_l)
        )
        return self.cur.fetchall()

    def get_entry_question_and_answer(
            self, serial: int
    ) -> Tuple[str, str]:
        """
        Finds the question and displayed answer for the given entry.
        :param serial: int
            The serial number of the entry.
        :return: Tuple[str, str]
            The strings for the question and displayed answer.
        """
        self.cur.execute(
            """
            SELECT question, text FROM entries
            INNER JOIN solutions ON solutions.entry = entries.entry
            WHERE entries.entry = ?
                AND solutions.displayed = 1;
            """, (serial,)
        )
        return self.cur.fetchone()

    def get_answers_for_entry(
            self, entry: int
    ) -> List[str]:
        """
        Finds the answers that are assigned to a particular entry.
        :param entry: int
            The serial number for the entry.
        :return: List[str]
            The answers.
        """
        self.cur.execute(
            """
            SELECT text FROM solutions
            INNER JOIN entries ON solutions.entry = entries.entry
            WHERE entries.entry = ?
            ORDER BY solutions.displayed DESC;
            """, (entry,)
        )
        return [x[0] for x in self.cur.fetchall()]

    def edit_entry(
            self, entry: int, question: str, answers: Tuple[str],
            sheets: List[str]
    ) -> None:
        """
        Modifies the entry of interest.
        :param entry: int
            The serial number for the entry being modified.
        :param question: str
            The name of the question to be saved.
        :param answers: Tuple[str]
            The answers to be saved.
        :param sheets: List[str]
            The sheets to which the entry must now belong.
        :return: None
        """
        self.conn.execute(
            """
            UPDATE entries SET question = ? WHERE entry = ?;
            """, (question, entry)
        )
        self.cur.execute(
            """
            SELECT * FROM solutions
            WHERE entry = ?
            ORDER BY displayed DESC;
            """, (entry,)
        )
        results = self.cur.fetchall()
        to_delete = []
        found_top = False
        displayed_answer, *other_answers = answers
        to_add = set(answers)

        # Checks each of the former answers.
        for i, result in enumerate(results):
            # If the formerly displayed answer is demoted
            if i == 0 and result[2] in other_answers:
                self.conn.execute(
                    """
                    UPDATE solutions
                    SET displayed = 0
                    WHERE solution = ?;
                    """, (result[0],)
                )

            # If a formerly non-displayed is promoted
            elif result[2] == displayed_answer:
                if i > 0:
                    self.conn.execute(
                        """
                        UPDATE solutions
                        SET displayed = 1
                        WHERE solution = ?;
                        """, (result[0],)
                    )
                found_top = True

            # If the former answer has been removed
            if result[2] not in answers:
                to_delete.append(result[0])
            else:
                to_add.remove(result[2])

        # Removes all answers that need to be deleted.
        if to_delete:
            delete_str = f"""
            DELETE FROM solutions WHERE {
            ' OR '.join(("solution = ?",) * len(to_delete))
            };
            """
            self.conn.execute(delete_str, list(to_delete))

        # Gives the entries its answers.
        if to_add:
            solutions_query = f"""
            INSERT INTO solutions (entry, text, displayed) VALUES
                {", ".join(["(?, ?, ?)"] * len(to_add))};
            """
            displayed = repeat(False) if found_top else chain(
                (True,), repeat(False)
            )
            self.cur.execute(
                solutions_query, sum(zip(
                    repeat(entry), to_add, displayed
                ), ())
            )

        # Updates the sheets
        set_sheets = set(sheets)
        current = set(self.get_entry_sheets(entry))

        to_add = set_sheets.difference(current)
        if to_add:
            self.cur.execute(
                f"""
                SELECT DISTINCT sheet FROM sheets
                INNER JOIN entries
                    ON entries.translator = sheets.translator
                WHERE entries.entry = ?
                    AND {" OR ".join(["name = ?"] * len(to_add))};
                """, (entry, *to_add)
            )
            to_add_ids = [x[0] for x in self.cur.fetchall()]
            self.conn.execute(
                f"""
                INSERT INTO mentions (sheet, entry) VALUES
                    {", ".join(["(?, ?)"] * len(to_add_ids))};
                """, sum(zip(to_add_ids, repeat(entry)), ())
            )

        to_remove = current.difference(set_sheets)
        if to_remove:
            self.cur.execute(
                f"""
                SELECT DISTINCT sheet FROM sheets
                INNER JOIN entries
                    ON entries.translator = sheets.translator
                WHERE {" OR ".join(["name = ?"] * len(to_remove))};
                """, tuple(to_remove)
            )
            to_remove_ids = [x[0] for x in self.cur.fetchall()]
            self.conn.execute(
                f"""
                DELETE FROM mentions
                WHERE entry = ?
                    AND ({" OR ".join(["sheet = ?"] * len(to_remove_ids))})
                """, (entry, *to_remove_ids)
            )

    def delete_entry(self, question: str, from_l: str, to_l: str) -> None:
        """Deletes the entry of interest.
        :param str question: The text in the question.
        :param str from_l: The name of the language being translated
            from.
        :param str to_l:The name of the language being translated to.
        :return: None
        """
        entry_no = self.get_entry(question, from_l, to_l)
        self.conn.execute(
            """
            DELETE FROM entries WHERE entry = ?;
            """, (entry_no,)
        )

    def get_next_entry(
            self, sheet_id: int, previous: Deque[int]
    ) -> Tuple[int, str, int, int, int]:
        """Finds the next entry for the user to do.
        :param int sheet_id:
            The id of the current sheet.
        :param Deque[int] previous:
            The previously performed questions.
        :rtype: Tuple[int, str, int, int, int]
        :return: The entry id to be taken next.
        """
        # Order by the following
        self.cur.execute(
            f"""
            SELECT entries.entry, question, points, needed, so_far
                FROM entries
            INNER JOIN mentions
                ON mentions.entry = entries.entry
            WHERE sheet = ?
            ORDER BY
            {
                "CASE " + " ".join(
                    f"WHEN entries.entry = ? THEN {i}" for i, _ in
                    enumerate(previous, 1)
                ) + " ELSE 0 END, "
                if previous else ""
            }
            CASE WHEN (so_far = 2) THEN 2 WHEN (so_far = 0) THEN 1
                ELSE 0 END,
            RANDOM()
            LIMIT 1;
            """, (sheet_id, *previous)
        )
        return self.cur.fetchone()

    def update_entry(
            self, entry: int, correct: bool
    ) -> Tuple[int, int, int]:
        """
        Finds the next entry for the user to do.
        :param entry: int
            The id of the entry.
        :param correct: bool
            Whether or not the entry was answered correctly.
        :return: Tuple[int, int, int]
            The points, needed and so_far values.
        """
        # Finds the entries previous details.
        self.cur.execute(
            f"""
            SELECT points, needed, so_far, completed
                FROM entries
            WHERE entry = ?;
            """, (entry,)
        )
        points, needed, so_far, completed = self.cur.fetchone()

        # Determines what the new result should be.
        if not correct:
            if needed < 10:
                needed += 1
            so_far = -needed
            completed = None
        else:
            if so_far < needed:
                so_far += 1
                if so_far == 0:
                    so_far = needed
            elif needed > 2:
                needed -= 1
                so_far -= 1
            if needed == so_far == 2 and not completed:
                self.cur.execute(
                    """
                    SELECT datetime('now');
                    """
                )
                completed = self.cur.fetchone()[0]

        # Update the new result
        self.conn.execute(
            f"""
            UPDATE entries
                SET points = ?, needed = ?, so_far = ?, completed = ?
            WHERE entry = ?;
            """, (points, needed, so_far, completed, entry)
        )

        return points, needed, so_far

    def refresh_entries(self) -> None:
        """
        Ensures that all entries gain points after a long enough period
        of time.
        :return: None
        """
        self.conn.execute(
            f"""
            UPDATE entries SET points = points + 1, completed = NULL,
                so_far = 0
            WHERE completed IS NOT NULL AND
                (datetime('now') > datetime(completed, '+1 day')
                    and points = 0)
                OR (datetime('now') > datetime(completed, '+7 day')
                    and points = 1)
                OR (datetime('now') > datetime(completed, '+1 month')
                    and points = 2)
                OR (datetime('now') > datetime(completed, '+3 month')
                    and points = 3)
            """
        )

    def get_points(self) -> int:
        """
        Returns the total number of points.
        :return: int
            The number of points held by the user.
        """
        self.cur.execute(
            f"""
            SELECT (
                (SELECT SUM(points) FROM entries) +
                (SELECT COUNT(entry) FROM entries WHERE so_far = 2)
            ) as total_points;
            """
        )
        return self.cur.fetchone()[0]
