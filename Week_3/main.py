from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
import psycopg2
import re
# Local module
from SET_SETTINGS import *


class SetPopup(Popup):

    def set_values(self):
        set_values_list = {
            "Author": self.ids.author.text,
            "Genre": self.ids.genre.text,
            "Year_from": self.ids.year_from.text,
            "Year_to": self.ids.year_to.text,
        }

        return set_values_list

    def reset_quiry(self):
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
                SELECT books.label, books.title, books.year, aditional_information.pages
                FROM books
                LEFT JOIN aditional_information ON books.book_id = aditional_information.book_id
                WHERE books.author = '{books_settings["Author"]}'
                      AND books.label = '{books_settings["Genre"]}' 
                      AND books.year > {books_settings["Year_from"]} 
                      AND books.year < {books_settings["Year_to"]};
                """
        query_author_all = f"""
                SELECT books.label, books.title, books.year, aditional_information.pages
                FROM books
                LEFT JOIN aditional_information ON books.book_id = aditional_information.book_id
                WHERE books.label = '{books_settings["Genre"]}' 
                      AND books.year > {books_settings["Year_from"]} 
                      AND books.year < {books_settings["Year_to"]};
        """

        query_genre_all = f"""
                SELECT books.label, books.title, books.year, aditional_information.pages
                FROM books
                LEFT JOIN aditional_information ON books.book_id = aditional_information.book_id
                WHERE books.author = '{books_settings["Author"]}' 
                      AND books.year > {books_settings["Year_from"]} 
                      AND books.year < {books_settings["Year_to"]};
        """

        query_all = """
        SELECT books.label, books.title, books.year, aditional_information.pages
        FROM books
        LEFT JOIN aditional_information ON books.book_id = aditional_information.book_id;
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
            titles = [f"[{genre}]| {title}  {year}y.  {pages}p." for genre, title, year, pages in self.show]
        else:
            titles = [f"[{genre}]| {title}  {year}y.  {pages}p." for genre, title, year, pages in self.current_books]
        self.ids.scroll.text = "\n\n".join(titles[:275]) if titles != [] else "Not Found"

    def handle_search_results(self, books):
        quiry = self.ids.search_quiry.text.lower()
        pattern = r".*" + quiry + ".*"

        self.current_books = [[genre, title, year, pages] for genre, title, year, pages in books if re.match(pattern, title.lower())]
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
    pass


class SettingsScreen(Screen):
    pass


class LibraryApp(App):
    def build(self):
        return Builder.load_file("style.kv")


if __name__ == "__main__":
    LibraryApp().run()
