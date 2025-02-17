from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
import psycopg2
import re
# Local module
from SET_SETTINGS import *
import last_book_id


class SetPopup(Popup):

    def set_values(self):
        set_values_list = {
            "Author": self.ids.author.text,
            "Genre": self.ids.genre.text,
            "Year_from": self.ids.year_from.text,
            "Year_to": self.ids.year_to.text,
        }

        return set_values_list

    def reset_query(self):
        self.ids.author.text = DEFAULT_AUTHOR
        self.ids.genre.text = DEFAULT_GENRE
        self.ids.year_from.text = YEAR_FROM
        self.ids.year_to.text = YEAR_TO


class LibraryScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        self.current_books = []
        self.show = []

    def search_book(self):
        popup = SetPopup()
        popup.open()
        popup.bind(on_dismiss=lambda instance: self.handle_search_results(self.search_books(popup.set_values())))

    @staticmethod
    def search_books(books_settings):
        conn = psycopg2.connect(
            database="Technical_Literature",
            user="postgres",
            host='127.0.0.1',
            password="25072004",
            port=5432
        )
        cur = conn.cursor()

        query_not_all = f"""
                SELECT books.book_id, books.label, books.title, books.year, aditional_information.pages
                FROM books
                LEFT JOIN aditional_information ON books.book_id = aditional_information.book_id
                WHERE books.author = '{books_settings["Author"]}'
                      AND books.label = '{books_settings["Genre"]}' 
                      AND books.year > {books_settings["Year_from"]} 
                      AND books.year < {books_settings["Year_to"]};
                """
        query_author_all = f"""
                SELECT books.book_id, books.label, books.title, books.year, aditional_information.pages
                FROM books
                LEFT JOIN aditional_information ON books.book_id = aditional_information.book_id
                WHERE books.label = '{books_settings["Genre"]}' 
                      AND books.year > {books_settings["Year_from"]} 
                      AND books.year < {books_settings["Year_to"]};
        """

        query_genre_all = f"""
                SELECT books.book_id, books.label, books.title, books.year, aditional_information.pages
                FROM books
                LEFT JOIN aditional_information ON books.book_id = aditional_information.book_id
                WHERE books.author = '{books_settings["Author"]}' 
                      AND books.year > {books_settings["Year_from"]} 
                      AND books.year < {books_settings["Year_to"]};
        """

        query_all = f"""
        SELECT books.book_id, books.label, books.title, books.year, aditional_information.pages
        FROM books
        LEFT JOIN aditional_information ON books.book_id = aditional_information.book_id
        WHERE  books.year > {books_settings["Year_from"]} 
               AND books.year < {books_settings["Year_to"]};
        """

        if books_settings["Author"] == "ALL" and books_settings["Genre"] == "ALL":
            cur.execute(query_all)
        elif books_settings["Author"] == "ALL":
            cur.execute(query_author_all)
        elif books_settings["Genre"] == "ALL":
            cur.execute(query_genre_all)
        else:
            cur.execute(query_not_all)

        books = cur.fetchall()

        cur.close()
        conn.close()

        return books

    def show_books(self):
        if self.show:
            titles = [f"<{book_id}> [{genre}]| {title}  {year}y.  {pages}p."
                      for book_id, genre, title, year, pages in self.show]
        else:
            titles = [f"<{book_id}> [{genre}]| {title}  {year}y.  {pages}p."
                      for book_id, genre, title, year, pages in self.current_books]
        self.ids.scroll.text = "\n\n".join(titles[:250]) if titles != [] else "Not Found"

    def handle_search_results(self, books):
        query = self.ids.search_quiry.text.lower()
        pattern = r".*" + query + ".*"

        self.current_books = [[book_id, genre, title, year, pages] for book_id, genre, title, year, pages in books if
                              re.match(pattern, title.lower())]
        self.show_books()

    def sort_by(self):
        mode = self.ids.sort_by.text

        if "None" in mode:
            self.ids.sort_by.text = "Sort by: Year"
            self.show = sorted(self.current_books, key=lambda year: year[1])
        elif "Year" in mode:
            self.ids.sort_by.text = "Sort by: Title"
            self.show = sorted(self.current_books, key=lambda title: title[0])
        elif "Title" in mode:
            self.ids.sort_by.text = "Sort by: None"
            self.show = self.current_books
        else:
            print("Can't sort!")

        self.show_books()


class AddScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.book_id = last_book_id.book_id_get() + 1
        self.label = "Engineering"

    def on_spinner_select(self, spinner, text):
        self.label = text

    def insert_book(self):
        conn = psycopg2.connect(
            database="Technical_Literature",
            user="postgres",
            host='127.0.0.1',
            password="25072004",
            port=5432
        )
        cur = conn.cursor()

        query_books = f"""INSERT INTO books (label, book_id, title, year, author) 
                    VALUES ('{self.label}',
                            {self.book_id} , 
                            '{self.ids.book_title.text}', 
                            {self.ids.book_year.text}, 
                            '{self.ids.book_author.text}');"""

        query_additional = f"""UPDATE aditional_information 
                               SET pages = {self.ids.book_pages.text},
                               description = '{self.ids.book_description.text}'
                               WHERE book_id = {self.book_id};
                               """
        cur.execute(query_books)
        conn.commit()
        cur.execute(query_additional)
        conn.commit()

        # updating book_id
        last_book_id.book_id_save(self.book_id + 1)
        print("Current last book_id: ", self.book_id)

        cur.close()
        conn.close()


class DeleteScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.book_id = 0
        self.mode = 0

    def check_book_existence(self):
        self.book_id = self.ids.book_delete_id.text

        conn = psycopg2.connect(
            database="Technical_Literature",
            user="postgres",
            host='127.0.0.1',
            password="25072004",
            port=5432
        )
        cur = conn.cursor()

        query_all = f"""SELECT EXISTS(SELECT 1 FROM books WHERE book_id = {self.book_id});"""

        cur.execute(query_all)
        check = cur.fetchall()

        return check[0][0]

    def change_labels(self, current_books):
        self.ids.book_delete_author.text = \
            str(current_books[0][1])[:28] + "...." if len(str(current_books[0][1])) > 28 else str(current_books[0][1])
        self.ids.book_delete_genre.text = str(current_books[0][2])
        self.ids.book_delete_year.text = str(current_books[0][4])
        self.ids.book_delete_pages.text = str(current_books[0][5])
        self.ids.book_delete_title.text = \
            str(current_books[0][3])[:28] + "...." if len(str(current_books[0][3])) > 28 else str(current_books[0][3])

    def check_book(self):
        conn = psycopg2.connect(
            database="Technical_Literature",
            user="postgres",
            host='127.0.0.1',
            password="25072004",
            port=5432
        )
        cur = conn.cursor()

        if self.check_book_existence():
            query_all = f"""
                    SELECT books.book_id, books.author, books.label, books.title, books.year, aditional_information.pages
                    FROM books
                    LEFT JOIN aditional_information ON books.book_id = aditional_information.book_id
                    WHERE  books.book_id = {self.book_id};
                    """

            cur.execute(query_all)
            books = cur.fetchall()

            current_books = [[book_id, author, genre, title, year, pages] for book_id, author, genre, title, year, pages in books]
            self.change_labels(current_books)

            # changing mode
            self.mode = 1

        else:
            current_books = [["Not exist", "Not exist", "Not exist", "Not exist", "Not exist", "Not exist"]]
            self.change_labels(current_books)
            print("Doesn't exist!")

        cur.close()
        conn.close()

    def delete_book(self):
        conn = psycopg2.connect(
            database="Technical_Literature",
            user="postgres",
            host='127.0.0.1',
            password="25072004",
            port=5432
        )
        cur = conn.cursor()

        if self.mode == 1:
            query_books = f"""DELETE FROM books WHERE book_id = {self.book_id};"""
            cur.execute(query_books)
            conn.commit()

            self.mode = 0
        else:
            print("Wrong mode!")

        cur.close()
        conn.close()


class SettingsScreen(Screen):
    pass


class LibraryApp(App):
    def build(self):
        return Builder.load_file("style.kv")


if __name__ == "__main__":
    LibraryApp().run()
