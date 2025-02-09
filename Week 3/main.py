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
    def search_book(self):
        popup = SetPopup()
        popup.open()
        popup.bind(on_dismiss=lambda instance: self.handle_search_results(self.search_books(popup.set_values())))


    def search_books(self, books_settings):
        conn = psycopg2.connect(
            database="Technical_Literature",
            user="postgres",
            host='127.0.0.1',
            password="25072004",
            port=5432
        )
        cur = conn.cursor()

        query_not_all = f"""
                SELECT title, year 
                FROM books
                WHERE books.author = '{books_settings["Author"]}'
                      AND books.label = '{books_settings["Genre"]}' 
                      AND books.year > {books_settings["Year_from"]} 
                      AND books.year < {books_settings["Year_to"]};
                """
        query_author_all = f"""
                SELECT title, year 
                FROM books
                WHERE books.label = '{books_settings["Genre"]}' 
                      AND books.year > {books_settings["Year_from"]} 
                      AND books.year < {books_settings["Year_to"]};
        """

        query_genre_all = f"""
                SELECT title, year 
                FROM books
                WHERE books.author = '{books_settings["Author"]}' 
                      AND books.year > {books_settings["Year_from"]} 
                      AND books.year < {books_settings["Year_to"]};
        """

        query_all = """
        SELECT title, year
        FROM books;
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

    def handle_search_results(self, books):
        quiry = self.ids.search_quiry.text
        pattern = r".*" + quiry + ".*"

        current_books = [title for title, year in books if re.match(pattern, title)]

        self.ids.scroll.text = "\n\n".join(current_books[:300])


class AddScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class LibraryApp(App):
    def build(self):
        return Builder.load_file("style.kv")


if __name__ == "__main__":
    LibraryApp().run()
