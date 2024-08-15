from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import io
import MySQLdb
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
import jinja2

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages and sessions

app.config['MYSQL_HOST'] = 'mysql-scms-6-rvce.d.aivencloud.com'
app.config['MYSQL_USER'] = 'avnadmin'
app.config['MYSQL_PASSWORD'] = 'AVNS_E5Yqhjdd1PI5lmsl31P'
app.config['MYSQL_DB'] = 'scms'
app.config['MYSQL_PORT'] = 10363
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


mysql = MySQL(app)

#--------So that the points(which has to appear in new lines) don't become paragraphs in announcements-------
@app.template_filter('nl2br')
def nl2br(value):
    """Converts newlines in text to HTML line breaks."""
    return value.replace('\n', '<br>\n')

@app.route('/select_user', methods=['GET', 'POST'])
def select_user():
    return render_template("user_selection.html")
    
#---------------------------------------student-----------------------------------------------------
@app.route("/student")
def student_login():
    return render_template("student_login_page.html")

@app.route('/student/login', methods=['GET', 'POST'])
def register_login_student():
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        
        if form_type == 'login':
            usn = request.form['usn']
            password = request.form['password']
            
            # Perform your login validation logic here
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM student WHERE usn = %s AND password = %s', (usn, password))
            user = cursor.fetchone()
            cursor.close()
            
            if user:
                session['logged_in'] = True
                session['usn'] = usn
                return redirect(url_for('student_dashboard'))
            else:
                flash('Invalid credentials')
        
        elif form_type == 'register':
            name = request.form['name']
            usn = request.form['usn']
            phone = request.form['phone']
            email = request.form['email']
            parent_phone = request.form['parent_phone']
            parent_email = request.form['parent_email']
            password = request.form['password']
            cpassword = request.form['cpassword']
            
            # Perform your registration validation logic here
            if password == cpassword:
                cursor = mysql.connection.cursor()
                cursor.execute('INSERT INTO student (name, usn, phone_no, email_id, password) VALUES (%s, %s, %s, %s, %s)', (name, usn, phone, email, password))
                mysql.connection.commit()
               
                cursor.execute('INSERT INTO parents (usn, parent_phone, parent_email_id) VALUES (%s, %s, %s)', (usn, parent_phone, parent_email))
                mysql.connection.commit()
                cursor.close()
                
                session['logged_in'] = True
                session['usn'] = usn
                return redirect(url_for('student_dashboard'))
            else:
                flash('Passwords do not match')
    
    return render_template('student_login_page.html')


@app.route('/student/dashboard')
def student_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('register_login_student'))
    return render_template('student_dashboard.html')

@app.route('/student/documents/upload', methods=['GET', 'POST'])
def upload_file():
    if not session.get('logged_in'):
        return redirect(url_for('register_login_student'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash('Invalid file type')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            file_data = file.read()
            student_name = request.form['student_name']
            
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO documents (student_name, filename, file_data) VALUES (%s, %s, %s)', (student_name, filename, file_data))
            mysql.connection.commit()
            cursor.close()
            
            flash('File successfully uploaded')
            return redirect(url_for('upload_file'))
    
    return render_template('student_uploads.html')

@app.route('/student/documents/view_document/<int:document_id>')
def view_document(document_id):
    if not session.get('logged_in'):
        return redirect(url_for('register_login_student'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT filename, file_data FROM documents WHERE id = %s', (document_id,))
    document = cursor.fetchone()
    cursor.close()
    
    if document:
        file_data = document['file_data']
        filename = document['filename']
        
        return send_file(io.BytesIO(file_data), download_name=filename, as_attachment=False)
    else:
        return 'File not found'
    

@app.route('/student/logout')
def student_logout():
    session.clear()
    return redirect(url_for('register_login_student'))
#------------------------------------------------------------

#counsellor----------------------------------------------------------------------
@app.route("/counsellor")
def counsellor_login():
    return render_template("counsellor_login_page.html")


@app.route('/counsellor/login', methods=['GET', 'POST'])
def register_login_counsellor():
    if request.method == 'POST':
        c_name = request.form['name']
        password = request.form['password']
        
        # Perform login validation
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM counsellor WHERE c_name = %s AND password = %s', (c_name, password))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            session['logged_in'] = True
            session['name'] = c_name
            session['counsellor_id'] = user['c_id']
            return redirect(url_for('counsellor_dashboard'))
        else:
            flash('Invalid credentials')
    
    return render_template('counsellor_login_page.html')

@app.route('/counsellor/dashboard')
def counsellor_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('register_login_counsellor'))
    return render_template('counsellor_dashboard.html')

@app.route('/counsellor/logout')
def counsellor_logout():
    session.clear()
    return redirect(url_for('register_login_counsellor'))
#------------------------------------------------------------------------------------------



#admin----------------------------------------------------------------------
@app.route("/admin")
def admin_login():
    return render_template("admin_login_page.html")


@app.route('/admin/login', methods=['GET', 'POST'])
def register_login_admin():
    if request.method == 'POST':
        admin_email = request.form['email']
        admin_password = request.form['password']
        
        # Perform login validation
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM admin WHERE admin_email = %s AND admin_password = %s', (admin_email, admin_password))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            session['logged_in'] = True
            session['email'] = admin_email
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials')
    
    return render_template('admin_login_page.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('register_login_admin'))
    return render_template('admin_dashboard.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('register_login_admin'))
#------------------------------------------------------------------------------------------



@app.route("/")
@app.route("/home")
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM announcements ORDER BY date DESC LIMIT 3")
    latest_announcements = cursor.fetchall()
    cursor.close()
    print(latest_announcements) 
    return render_template('home.html', announcements=latest_announcements)


ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# route for Annoucements page
@app.route('/announcements')
def announcements():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM announcements ORDER BY date DESC')
    announcements = cursor.fetchall()
    cursor.close()
    return render_template('announcements.html', announcements=announcements)


# route for creat-Annoucements page
@app.route('/create-announcement')
def create_announcements():
    return render_template('create-announcement.html')

# After submitting the create annoucement form
@app.route('/submit-announcement', methods=['POST'])
def submit_announcement():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        link = request.form.get('link')
        author = "BK Srinivas"
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO announcements (author, date, title, content, link) VALUES (%s, %s, %s, %s, %s)''', (author, date, title, content, link))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('announcements'))
    
@app.route('/edit-announcement/<int:id>', methods=['GET', 'POST'])
def edit_announcement(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        cursor.execute('UPDATE announcements SET title = %s, content = %s WHERE id = %s', (title, content, id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('announcements'))
    else:
        cursor.execute('SELECT * FROM announcements WHERE id = %s', (id,))
        announcement = cursor.fetchone()
        cursor.close()
        return render_template('edit-announcement.html', announcement=announcement)

# Route to delete an announcement
@app.route('/delete-announcement/<int:id>', methods=['GET'])
def delete_announcement(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM announcements WHERE id = %s', (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('announcements'))

# add the meeting to the database.
@app.route('/add_meeting', methods=['POST'])
def add_meeting():
    if request.method == 'POST':
        # Retrieve form data
        date = request.form['date']
        time_12hr = request.form['time']
        link = request.form['link']
        description = request.form.get('description', '')

        # Retrieve counsellor_id from session
        counsellor_id = session.get('counsellor_id')

        # Convert 12-hour time format with AM/PM to 24-hour format
        time_24hr = datetime.strptime(time_12hr, '%I:%M %p').strftime('%H:%M')

        # Ensure the selected time is greater than the current time if it's the same day
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M')

        if date == current_date and time_24hr <= current_time:
            flash('Error: The time must be greater than the current time for the same day.', 'danger')
            return redirect(url_for('schedule_meetings'))

        # Insert data into the 'meeting' table
        cursor = mysql.connection.cursor()
        try:
            cursor.execute('''INSERT INTO meeting (date, time, link, description, counsellorid) 
                              VALUES (%s, %s, %s, %s, %s)''',
                           (date, time_24hr, link, description, counsellor_id))
            mysql.connection.commit()
            flash('Meeting scheduled successfully!', 'success')
        except MySQLdb.Error as e:
            mysql.connection.rollback()
            flash(f'Error scheduling meeting: {e}', 'danger')
        finally:
            cursor.close()

        return render_template('counsellor_dashboard.html')

    return render_template('counsellor_dashboard.html')



@app.route('/view_meetings')
def view_meetings():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT date, time, link, description FROM meeting ORDER BY date, time ASC')
    meetings = cursor.fetchall()
    cursor.close()

    return render_template('view_meetings.html', meetings=meetings)

@app.route('/student/student_view_meetings')
def student_view_meetings():
    if not session.get('logged_in'):
        return redirect(url_for('register_login_student'))

    usn = session.get('usn')
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Query to join student and meeting tables and fetch relevant meetings
    query = '''
        SELECT m.date, m.time, m.link, m.description 
        FROM student s
        JOIN counsellor_student cs ON s.usn = cs.usn
        JOIN meeting m ON cs.c_id = m.counsellorid
        WHERE s.usn = %s
        ORDER BY m.date, m.time ASC
    '''
    
    cursor.execute(query, (usn,))
    meetings = cursor.fetchall()
    cursor.close()

    return render_template('view_meetings.html', meetings=meetings)

if __name__ == '__main__':
    app.run(debug=True)
