# CREATE TABLE documents (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     student_name VARCHAR(255),
#     filename VARCHAR(255),
#     file_data LONGBLOB
# );

from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages and sessions

app.config['MYSQL_HOST'] = 'mysql-scms-6-rvce.d.aivencloud.com'
app.config['MYSQL_USER'] = 'avnadmin'
app.config['MYSQL_PASSWORD'] = 'AVNS_E5Yqhjdd1PI5lmsl31P'
app.config['MYSQL_DB'] = 'scms'
app.config['MYSQL_PORT'] = 10363
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        
        if form_type == 'login':
            usn = request.form['usn']
            password = request.form['password']
            # Perform your login validation logic here
            # Example check, replace with actual logic and database query
            if usn == 'test' and password == 'test':  
                session['logged_in'] = True
                session['usn'] = usn
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid credentials')
        
        elif form_type == 'register':
            name = request.form['name']
            usn = request.form['usn']
            phone = request.form['phone']
            email = request.form['email']
            password = request.form['password']
            cpassword = request.form['cpassword']
            # Perform your registration validation logic here
            if password == cpassword:  # Example check, replace with actual logic
                # Save registration details to the database
                cursor = mysql.connection.cursor()
                cursor.execute('INSERT INTO users (name, usn, phone, email, password) VALUES (%s, %s, %s, %s, %s)', (name, usn, phone, email, password))
                mysql.connection.commit()
                cursor.close()
                session['logged_in'] = True
                session['usn'] = usn
                return redirect(url_for('dashboard'))
            else:
                flash('Passwords do not match')
    
    return render_template('login_page.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('register'))
    return render_template('student_dashboard.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if not session.get('logged_in'):
        return redirect(url_for('register'))
    
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

@app.route('/view_document/<int:document_id>')
def view_document(document_id):
    if not session.get('logged_in'):
        return redirect(url_for('register'))
    
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('register'))

if __name__ == '__main__':
    app.run(debug=True)
