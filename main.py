# CREATE TABLE documents (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     student_name VARCHAR(255),
#     filename VARCHAR(255),
#     file_data LONGBLOB
# );

from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Query@1811'
app.config['MYSQL_DB'] = 'counsellor_database'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
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

if __name__ == '__main__':
    app.run(debug=True)

