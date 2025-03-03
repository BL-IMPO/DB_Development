import psycopg2


def create_database():
    terms = []
    definitions = []

    with open("raw_sorted_data.txt", "r") as file:
        lines = [line for line in file.readlines()]

        for line in lines:
            term, definition = line.split(" - ")
            terms.append(term[2:])
            definitions.append(definition[:-3])

    return terms, definitions


def main():
    conn = psycopg2.connect(database="DB_GLOSSARY",
                            user="postgres",
                            host="127.0.0.1",
                            password="25072004",
                            port=5432)

    cur = conn.cursor()

    quiry = """
            CREATE TABLE glossary(
                term VARCHAR (50),
                definition VARCHAR (400));
            """

    cur.execute(quiry)
    conn.commit()

    terms, definitions = create_database()

    for term, definition in zip(terms, definitions):
        cur.execute(
            f"""
            INSERT INTO glossary (term, definition) VALUES ('{term}', '{definition}');
            """
        )

        conn.commit()

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
