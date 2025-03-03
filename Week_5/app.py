from flask import Flask, render_template, request, redirect, url_for
import csv
import psycopg2
from collections import defaultdict

app = Flask(__name__)


# Load glossary data from CSV or PostgreSQL
def load_glossary():
    glossary = defaultdict(list)

    # Try loading from PostgreSQL first
    try:
        conn = psycopg2.connect(
            database="DB_GLOSSARY",
            host="127.0.0.1",
            user="postgres",
            password="password",
            port=5432
        )
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

    except Exception as e:
        print(f"Error loading from PostgreSQL: {e}. Falling back to CSV.")

        # Fallback to CSV if PostgreSQL fails
        with open('Sorted_Data.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                term = row['Terms']
                definition = row['Definitions']
                first_letter = term[0].upper()  # Get the first letter of the term
                glossary[first_letter].append((term, definition))

    # Sort the glossary by letter
    sorted_glossary = dict(sorted(glossary.items()))
    return sorted_glossary


# Save glossary data to CSV
def save_glossary(glossary):
    with open('Sorted_Data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Terms', 'Definitions', 'Section']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for section, terms in glossary.items():
            for term, definition in terms:
                writer.writerow({'Terms': term, 'Definitions': definition, 'Section': section})


# Main page
@app.route('/')
def index():
    glossary = load_glossary()
    sort_order = request.args.get('sort', 'asc')  # Default sort order is A-Z
    sorted_glossary = sort_glossary(glossary, sort_order)
    return render_template('index.html', glossary=sorted_glossary, selected_letter=None, sort_order=sort_order)


# Filter terms by letter
@app.route('/letter/<letter>')
def filter_by_letter(letter):
    glossary = load_glossary()
    selected_letter = letter.upper()
    sort_order = request.args.get('sort', 'asc')  # Default sort order is A-Z

    if selected_letter == "ALL":
        # Show all terms
        filtered_terms = []
        for terms in glossary.values():
            filtered_terms.extend(terms)
    else:
        # Show terms for the selected letter
        filtered_terms = glossary.get(selected_letter, [])

    # Sort the filtered terms
    filtered_terms = sorted(filtered_terms, key=lambda x: x[0], reverse=(sort_order == 'desc'))
    return render_template('index.html', glossary=glossary, selected_letter=selected_letter,
                           filtered_terms=filtered_terms, sort_order=sort_order)


# Search page
@app.route('/search', methods=['GET', 'POST'])
def search():
    glossary = load_glossary()
    search_query = request.form.get('search_query', '').strip().lower()
    results = []

    if search_query:
        for section, terms in glossary.items():
            for term, definition in terms:
                if search_query in term.lower() or search_query in definition.lower():
                    results.append((term, definition, section))

    return render_template('search.html', glossary=glossary, search_query=search_query, results=results)


# Data management page
@app.route('/data', methods=['GET', 'POST'])
def data():
    glossary = load_glossary()

    if request.method == 'POST':
        action = request.form.get('action')
        term = request.form.get('term')
        definition = request.form.get('definition')
        section = request.form.get('section')

        if action == 'add':
            glossary[section].append((term, definition))
        elif action == 'delete':
            section_to_delete = request.form.get('section_to_delete')
            term_to_delete = request.form.get('term_to_delete')
            glossary[section_to_delete] = [(t, d) for t, d in glossary[section_to_delete] if t != term_to_delete]
        elif action == 'update':
            old_term = request.form.get('old_term')
            new_term = request.form.get('new_term')
            new_definition = request.form.get('new_definition')
            section_to_update = request.form.get('section_to_update')
            glossary[section_to_update] = [(new_term if t == old_term else t, new_definition if t == old_term else d)
                                           for t, d in glossary[section_to_update]]

        save_glossary(glossary)
        return redirect(url_for('data'))

    return render_template('data.html', glossary=glossary)


# Sections page
@app.route('/sections')
def sections():
    glossary = load_glossary()
    return render_template('sections.html', glossary={'Database': []})


# Section terms page
@app.route('/section/<section>')
def section_terms(section):
    glossary = load_glossary()
    return render_template('section_terms.html', section=section, glossary=glossary, )


# Helper function to sort glossary
def sort_glossary(glossary, sort_order):
    sorted_glossary = {}
    for letter, terms in glossary.items():
        sorted_terms = sorted(terms, key=lambda x: x[0], reverse=(sort_order == 'desc'))
        sorted_glossary[letter] = sorted_terms
    return sorted_glossary


if __name__ == '__main__':
    app.run(debug=True)
