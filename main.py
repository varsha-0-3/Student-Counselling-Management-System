# CREATE TABLE documents (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     student_name VARCHAR(255),
#     filename VARCHAR(255),
#     file_data LONGBLOB
# );


from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_mysqldb import MySQL
import os

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'your_username'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'your_database'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'}

# Function to check if a filename has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to handle file upload
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Validate filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash('Invalid file type')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            file_data = file.read()  # Read file data as bytes
            
            # Save filename and file_data into MySQL database along with student details
            student_name = request.form['student_name']  # Example: Getting student_name from form
            
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO documents (student_name, filename, file_data) VALUES (%s, %s, %s)',
                           (student_name, filename, file_data))
            mysql.connection.commit()
            cursor.close()
            
            return redirect(url_for('upload_file'))
    
    return render_template('upload.html')


@app.route('/view_document/<int:document_id>')
def view_document(document_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT filename, file_data FROM documents WHERE id = %s', (document_id,))
    document = cursor.fetchone()
    cursor.close()
    
    if document:
        file_data = document['file_data']
        filename = document['filename']
        
        # Serve file to user's browser
        return send_file(io.BytesIO(file_data), attachment_filename=filename, as_attachment=True)
    else:
        return 'File not found'

if __name__ == '__main__':
    app.run(debug=True)
