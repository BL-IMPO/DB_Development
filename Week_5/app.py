from flask import Flask, render_template
import psycopg2
from collections import defaultdict

app = Flask(__name__)


def load_glossary():
    glossary = defaultdict(list)
    conn = psycopg2.connect(database="DB_GLOSSARY",
                            host="127.0.0.1",
                            user="postgres",
                            password="25072004",
                            port=5432)
    cur = conn.cursor()

    cur.execute("SELECT * FROM glossary;")
    reader = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()

    for row in reader:
        term = row[0]
        definition = row[1]
        first_letter = term[0].upper()  # Get the first letter of the term
        glossary[first_letter].append((term, definition))

    # Sort the glossary by letter
    sorted_glossary = dict(sorted(glossary.items()))

    return sorted_glossary


@app.route('/')
def index():
    glossary = load_glossary()
    return render_template('index.html', glossary=glossary, selected_letter=None, filtered_terms=None)


@app.route('/letter/<letter>')
def filter_by_letter(letter):
    glossary = load_glossary()
    selected_letter = letter.upper()

    if selected_letter == "ALL":
        # Show all terms
        filtered_terms = []
        for terms in glossary.values():
            filtered_terms.extend(terms)
    else:
        # Show terms for the selected letter
        filtered_terms = glossary.get(selected_letter, [])

    return render_template('index.html', glossary=glossary, selected_letter=selected_letter,
                           filtered_terms=filtered_terms)


if __name__ == '__main__':
    app.run(debug=True)