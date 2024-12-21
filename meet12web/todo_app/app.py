from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change to a random secret key

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Replace with your MySQL username
        password="",  # Replace with your MySQL password
        database="todo_db"
    )

@app.route('/')
def index():
    db = get_db_connection()
    cursor = db.cursor()
    
    # Load tasks from the database
    cursor.execute("""
        SELECT t.id, t.task_name, t.deadline, p.priority_name, s.subject_name, st.status_name
        FROM tasks t
        JOIN priorities p ON t.priority_id = p.id
        JOIN subjects s ON t.subject_id = s.id
        JOIN statuses st ON t.status_id = st.id
    """)
    
    tasks = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    task_name = request.form['task_name']
    task_deadline = request.form['task_deadline']
    task_priority = request.form['task_priority']
    task_subject = request.form['task_subject']

    if task_name and task_priority and task_deadline and task_subject:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("INSERT IGNORE INTO subjects (subject_name) VALUES (%s)", (task_subject,))
        cursor.execute("SELECT id FROM subjects WHERE subject_name = %s", (task_subject,))
        subject_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM priorities WHERE priority_name = %s", (task_priority,))
        priority_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM statuses WHERE status_name = 'Belum Selesai'")
        status_id = cursor.fetchone()[0]

        cursor.execute(
            "INSERT INTO tasks (task_name, deadline, priority_id, subject_id, status_id) VALUES (%s, %s, %s, %s, %s)",
            (task_name, task_deadline, priority_id, subject_id, status_id)
        )
        db.commit()
        cursor.close()
        db.close()
        flash('Task added successfully!')
    else:
        flash('All fields are required!')

    return redirect(url_for('index'))

@app.route('/delete-selected', methods=['POST'])
def delete_selected_tasks():
    task_ids = request.form.getlist('task_ids')
    if task_ids:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM tasks WHERE id IN (%s)" % ','.join(task_ids))
        db.commit()
        cursor.close()
        db.close()
        flash('Selected tasks deleted successfully!')
    else:
        flash('No tasks selected to delete.')
    return redirect(url_for('index'))

@app.route('/delete-all', methods=['POST'])
def delete_all_tasks():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM tasks")
    db.commit()
    cursor.close()
    db.close()
    flash('All tasks deleted successfully!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)