from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database Connection
def get_db_connection():

    conn = sqlite3.connect('notes.db')

    conn.row_factory = sqlite3.Row

    return conn

# Create Table
def create_table():

    conn = get_db_connection()

    conn.execute('''

        CREATE TABLE IF NOT EXISTS notes (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            content TEXT NOT NULL,

            important INTEGER DEFAULT 0,

            created_at TEXT NOT NULL
        )

    ''')

    conn.commit()

    conn.close()

create_table()

# Home Page
@app.route('/')
def home():

    return render_template('index.html')

# Add Note
@app.route('/add_note', methods=['POST'])
def add_note():

    data = request.get_json()

    title = data.get('title')

    content = data.get('content')

    created_at = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    conn = get_db_connection()

    conn.execute(

        '''

        INSERT INTO notes

        (title, content, created_at)

        VALUES (?, ?, ?)

        ''',

        (title, content, created_at)

    )

    conn.commit()

    conn.close()

    return jsonify({
        "message": "Note Added"
    })

# Get Notes
@app.route('/get_notes', methods=['GET'])
def get_notes():

    conn = get_db_connection()

    notes = conn.execute(

        '''

        SELECT * FROM notes

        ORDER BY important DESC, id DESC

        '''

    ).fetchall()

    conn.close()

    notes_list = []

    for note in notes:

        notes_list.append({

            "id": note["id"],

            "title": note["title"],

            "content": note["content"],

            "important": note["important"],

            "created_at": note["created_at"]

        })

    return jsonify(notes_list)

# Delete Note
@app.route('/delete_note/<int:id>', methods=['DELETE'])
def delete_note(id):

    conn = get_db_connection()

    conn.execute(

        'DELETE FROM notes WHERE id = ?',

        (id,)

    )

    conn.commit()

    conn.close()

    return jsonify({
        "message": "Deleted"
    })

# Edit Note
@app.route('/edit_note/<int:id>', methods=['PUT'])
def edit_note(id):

    data = request.get_json()

    title = data.get('title')

    content = data.get('content')

    conn = get_db_connection()

    conn.execute(

        '''

        UPDATE notes

        SET title = ?, content = ?

        WHERE id = ?

        ''',

        (title, content, id)

    )

    conn.commit()

    conn.close()

    return jsonify({
        "message": "Updated"
    })

# Highlight Important Note
@app.route('/highlight_note/<int:id>', methods=['PUT'])
def highlight_note(id):

    conn = get_db_connection()

    note = conn.execute(

        'SELECT important FROM notes WHERE id = ?',

        (id,)

    ).fetchone()

    new_value = 0 if note["important"] == 1 else 1

    conn.execute(

        '''

        UPDATE notes

        SET important = ?

        WHERE id = ?

        ''',

        (new_value, id)

    )

    conn.commit()

    conn.close()

    return jsonify({
        "message": "Highlight Updated"
    })

if __name__ == '__main__':

    app.run(debug=True)