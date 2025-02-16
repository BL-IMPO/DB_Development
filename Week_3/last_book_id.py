import pickle


def book_id_save(book_id: int):
    """
    Parameters
    ----------
    book_id
    Book id to save for future using.
    """
    f = open("last_book_id.dat", "wb")
    pickle.dump(book_id, f)
    f.close()


def book_id_get():
    """
    Returns
    -------
    Returns last book id from table books.
    """
    f = open("last_book_id.dat", "rb")
    book_id = pickle.load(f)
    f.close()

    return book_id


if __name__ == "__main__":
    print(book_id_save(book_id_get() - 1))
    print(book_id_get())
    print(book_id_save(book_id_get() + 1))
    print(book_id_get())
