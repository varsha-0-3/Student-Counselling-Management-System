from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session, make_response
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import io
import MySQLdb
from datetime import datetime
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages and sessions

app.config['MYSQL_HOST'] = 'mysql-scms-6-rvce.d.aivencloud.com'
app.config['MYSQL_USER'] = 'avnadmin'
app.config['MYSQL_PASSWORD'] = 'AVNS_E5Yqhjdd1PI5lmsl31P'
app.config['MYSQL_DB'] = 'scms'
app.config['MYSQL_PORT'] = 10363
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Initialize Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Add your SMTP server details
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'scmsrvce24@gmail.com'  # Add your email username
app.config['MAIL_PASSWORD'] = 'wulr rrdk onxi cmfa'  # Add your email password
mail=Mail(app)

#--------So that the points(which has to appear in new lines) don't become paragraphs in announcements-------
@app.template_filter('nl2br')
def nl2br(value):
    """Converts newlines in text to HTML line breaks."""
    return value.replace('\n', '<br>\n')

@app.route('/select_user', methods=['GET', 'POST'])
def select_user():
    response = make_response(render_template("user_selection.html"))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response
    
#---------------------------------------student-----------------------------------------------------
# @app.route("/student")
# def student_login():
#     return render_template("student_login_page.html")

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
                return redirect(url_for('register_login_student') + '#')
        
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

    response = make_response(render_template('student_dashboard.html'))
    response.headers['Cache-Control'] = 'no-store'
    return response



@app.route('/student/dashboard/profile')
def view_profile_student():
    if not session.get('logged_in'):
        return redirect(url_for('student_login'))  # Redirect to login if not logged in

    usn = session.get('usn')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch the student's profile data
    query = """
    SELECT 
        student.*,
        counsellor.batch_no,
        counsellor.c_name, 
        counsellor.c_email, 
        counsellor.c_contact,
        activity_points.points, 
        parents.parent_email_id, 
        parents.parent_phone 
    FROM student
    LEFT JOIN counsellor_student ON student.usn = counsellor_student.usn
    LEFT JOIN counsellor ON counsellor_student.c_id = counsellor.c_id
    LEFT JOIN activity_points ON student.usn = activity_points.usn
    LEFT JOIN parents ON student.usn = parents.usn
    WHERE student.usn = %s
    """
    
    cursor.execute(query, (usn,))
    student = cursor.fetchone()
    cursor.close()

    if not student:
        return "Student not found", 404

    return render_template('student_profile.html', student=student)


@app.route('/student/dashboard/update_profile', methods=['POST'])
def update_profile():
    if not session.get('logged_in'):
        return redirect(url_for('student_login'))
    usn = session.get('usn')
    email_id = request.form.get('email_id', '')
    phone_no = request.form.get('phone_no', '')
    parent_email_id = request.form.get('parent_email_id', '')
    parent_phone = request.form.get('parent_phone', '')
    accommodation_type= request.form.get('accommodation_type', '')
    address= request.form.get('address', '')
    profile_pic = request.form.get('profile_pic', '')  # New field
    if 'drive.google.com' in profile_pic and 'view?usp=sharing' in profile_pic:
        profile_pic = profile_pic.replace('/view?usp=sharing', '/preview')
    cursor = mysql.connection.cursor()

    # Update student profile
    update_query = """
    UPDATE student 
    SET email_id = %s, phone_no = %s, accommodation_type=%s,address=%s,profile_pic=%s
    WHERE usn = %s
    """
    cursor.execute(update_query, ( email_id, phone_no,accommodation_type,address,profile_pic,usn))

    # Update parent details
    update_parent_query = """
    UPDATE parents
    SET parent_email_id = %s, parent_phone = %s
    WHERE usn = %s
    """
    cursor.execute(update_parent_query, (parent_email_id, parent_phone, usn))

    mysql.connection.commit()
    cursor.close()
   

    return redirect(url_for('view_profile_student'))



ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_data = file.read()
            usn = request.form['usn']
            document_type_id = int(request.form['document_type_id'])
            semester = int(request.form['semester'])
            upload_date = datetime.now()

            cursor = mysql.connection.cursor()
            cursor.execute(
                'INSERT INTO student_documents (usn, document_type_id, document_name, file_data, folder_url, semester, upload_date) '
                'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (usn, document_type_id, filename, file_data, None, semester, upload_date)
            )
            mysql.connection.commit()
            cursor.close()

            flash('File successfully uploaded')
            return redirect(url_for('upload_file'))
    
    # Fetch document types to display in the form
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT document_type_id, document_type_name FROM document_types')
    document_types = cursor.fetchall()
    cursor.close()

    return render_template('student_uploads.html', document_types=document_types)



@app.route('/student/documents/view_all/<string:usn>')
def view_all_documents(usn):
    if not session.get('logged_in'):
        return redirect(url_for('register_login_student'))

    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT sd.id, sd.document_name, dt.document_type_name, sd.semester, sd.upload_date 
        FROM student_documents sd
        JOIN document_types dt ON sd.document_type_id = dt.document_type_id
        WHERE sd.usn = %s
    ''', (usn,))
    documents = cursor.fetchall()
    cursor.close()

    if documents:
        return render_template('view_documents.html', usn=usn, documents=documents)
    else:
        flash('No documents found for this student.')
        return redirect(url_for('upload_file'))

@app.route('/student/documents/view_document/<int:document_id>')
def view_document(document_id):
    

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT document_name, file_data FROM student_documents WHERE id = %s', (document_id,))
    document = cursor.fetchone()
    cursor.close()

    if document:
        file_data = document['file_data']
        document_name = document['document_name']
        
        return send_file(io.BytesIO(file_data), download_name=document_name, as_attachment=False)
    else:
        flash('File not found')
        return redirect(url_for('view_all_documents', usn=session.get('usn')))


@app.route('/student/logout')
def student_logout():
    session.clear()
    return redirect(url_for('select_user'))
#------------------------------------------------------------

#counsellor----------------------------------------------------------------------
# @app.route("/counsellor")
# def counsellor_login():
#     return render_template("counsellor_login_page.html")


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
            session['c_logged_in'] = True
            session['name'] = c_name
            session['counsellor_id'] = user['c_id']
            return redirect(url_for('counsellor_dashboard'))
        else:
            flash('Invalid credentials')
    
    return render_template('counsellor_login_page.html')

@app.route('/counsellor/dashboard')
def counsellor_dashboard():
    if not session.get('c_logged_in'):
        return redirect(url_for('register_login_counsellor'))

    response = make_response(render_template('counsellor_dashboard.html'))
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.route('/counsellor/view_all_student_documents', methods=['GET', 'POST'])
def students_documents():
    if not session.get('c_logged_in'):
        return redirect(url_for('register_login_counsellor'))

    usn = None
    documents = []


    if request.method == 'POST':
        usn = request.form['usn']

        if usn:
            cursor = mysql.connection.cursor()
            cursor.execute('''
                SELECT sd.id, sd.document_name, dt.document_type_name, sd.semester, sd.upload_date 
                FROM student_documents sd
                JOIN document_types dt ON sd.document_type_id = dt.document_type_id
                WHERE sd.usn = %s
            ''', (usn,))
            documents = cursor.fetchall()
            cursor.close()

            if not documents:
                flash('No documents found for this USN.')

    return render_template('view_student_documents.html', usn=usn, documents=documents)

@app.route('/counsellor/batch_students')
def view_batch_students():
    if not session.get('c_logged_in'):
        return redirect(url_for('register_login_counsellor'))

    c_id = session.get('counsellor_id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    query = """
    SELECT student.* FROM student
    INNER JOIN counsellor_student ON student.usn = counsellor_student.usn
    WHERE counsellor_student.c_id = %s
    """
    cursor.execute(query, (c_id,))
    students = cursor.fetchall()
    cursor.close()
    return render_template('view_batch_students.html', students=students)

# ------------------------------------------------------
@app.route('/counsellor/dashboard/academic_profile', methods=['GET'])
def student_academic_profile():
    # Check if the counsellor is logged in
    if not session.get('c_logged_in'):
        return redirect(url_for('register_login_counsellor'))

    # Fetch counsellor ID from session
    counsellor_id = session.get('counsellor_id')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # 1. Fetch subjects
    cursor.execute("SELECT * FROM admin_addsubject")
    subjects = cursor.fetchall()

    # 2. Fetch all students (USNs) under this counsellor along with CGPA and SGPA
    cursor.execute('''
        SELECT 
            s.usn, 
            s.name, 
            cgpa.cgpa, 
            cgpa.sgpa 
        FROM 
            counsellor_student cs
        JOIN 
            student s ON cs.usn = s.usn
        LEFT JOIN 
            admin_addcgpa cgpa ON s.usn = cgpa.usn
        WHERE 
            cs.c_id = %s
        ORDER BY 
            s.usn
    ''', (counsellor_id,))
    cgpa_records = cursor.fetchall()

    # 3. Fetch all students under this counsellor for attendance
    cursor.execute('''
        SELECT s.usn, s.name
        FROM counsellor_student cs
        JOIN student s ON cs.usn = s.usn
        WHERE cs.c_id = %s
        ORDER BY s.usn
    ''', (counsellor_id,))
    students = cursor.fetchall()

    # Create a dictionary to store the attendance data for each student per subject
    attendance_data = {student['usn']: {'name': student['name'], 'attendance': {}} for student in students}

    # Fetch attendance data for each student and subject
    cursor.execute('''
        SELECT usn, subject_id, attendance
        FROM admin_addattendance
        WHERE usn IN %s
    ''', (tuple([student['usn'] for student in students]),))
    attendance_records = cursor.fetchall()

    # Map attendance data to the respective student and subject
    for record in attendance_records:
        usn = record['usn']
        subject_id = record['subject_id']
        attendance_percentage = record['attendance']

        # Find the subject name for the given subject_id
        subject_name = next((sub['subject_name'] for sub in subjects if sub['subject_id'] == subject_id), None)
        if subject_name:
            attendance_data[usn]['attendance'][subject_name] = attendance_percentage

    cursor.close()

    # Render the dashboard with the combined data
    return render_template(
        'view_batch_academic_profile.html', 
        subjects=subjects,                # For subject scores
        cgpa_records=cgpa_records,        # For CGPA/SGPA view
        students=students,                # For attendance view
        attendance_data=attendance_data    # For attendance mapping
    )


# --------------------------------------------------------------------------
# @app.route('/counsellor/view_batch_attendance', methods=['GET'])
# def view_batch_attendance():
#     # Check if the counsellor is logged in
#     if not session.get('c_logged_in'):
#         return redirect(url_for('register_login_counsellor'))

#     # Fetch counsellor ID from session
#     counsellor_id = session.get('counsellor_id')

#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

#     # Fetch all students under this counsellor
#     cursor.execute('''
#         SELECT s.usn, s.name
#         FROM counsellor_student cs
#         JOIN student s ON cs.usn = s.usn
#         WHERE cs.c_id = %s
#         ORDER BY s.usn
#     ''', (counsellor_id,))
#     students = cursor.fetchall()

#     # Fetch all subjects
#     cursor.execute('SELECT subject_id, subject_name FROM admin_addsubject ORDER BY subject_name')
#     subjects = cursor.fetchall()

#     # Create a dictionary to store the attendance data for each student per subject
#     attendance_data = {student['usn']: {'name': student['name'], 'attendance': {}} for student in students}

#     # Fetch attendance data for each student and subject
#     cursor.execute('''
#         SELECT usn, subject_id, attendance
#         FROM admin_addattendance
#         WHERE usn IN %s
#     ''', (tuple([student['usn'] for student in students]),))
#     attendance_records = cursor.fetchall()

#     # Map attendance data to the respective student and subject
#     for record in attendance_records:
#         usn = record['usn']
#         subject_id = record['subject_id']
#         attendance_percentage = record['attendance']

#         # Find the subject name for the given subject_id
#         subject_name = next((sub['subject_name'] for sub in subjects if sub['subject_id'] == subject_id), None)
#         if subject_name:
#             attendance_data[usn]['attendance'][subject_name] = attendance_percentage

#     cursor.close()

#     # Pass data to the template
#     return render_template('batch_attendance.html', 
#                            students=students, 
#                            subjects=subjects, 
#                            attendance_data=attendance_data)




@app.route('/view_student_profile/<usn>')
def view_student_profile(usn):
    if not session.get('c_logged_in'):
        return redirect(url_for('register_login_counsellor'))
    
    c_id = session.get('counsellor_id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    query = """
            SELECT 
                student.*,
                counsellor.batch_no,
                counsellor.c_name, 
                counsellor.c_email, 
                counsellor.c_contact,
                activity_points.points, 
                parents.parent_email_id, 
                parents.parent_phone,
                admin_addcgpa.cgpa 
            FROM student
            LEFT JOIN admin_addcgpa ON student.usn = admin_addcgpa.usn
            LEFT JOIN counsellor_student ON student.usn = counsellor_student.usn
            LEFT JOIN counsellor ON counsellor_student.c_id = counsellor.c_id
            LEFT JOIN activity_points ON student.usn = activity_points.usn
            LEFT JOIN parents ON student.usn = parents.usn
            WHERE student.usn = %s
    """
    cursor.execute(query, (usn,))
    result = cursor.fetchone()
    cursor.close()

    if result is None:
        print("No student found with USN:", usn)
    else:
        print("Result:", result)  # This will show all the fetched student data

    # Render the profile page with the student data
    return render_template('view_student_profile.html', student=result)

# @app.route('/counsellor/view_student_cgpa', methods=['GET'])
# def view_student_cgpa():
#     # Check if the counsellor is logged in
#     if not session.get('c_logged_in'):
#         return redirect(url_for('register_login_counsellor'))

#     # Fetch counsellor ID from session
#     counsellor_id = session.get('counsellor_id')

#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

#     # Fetch all students (USNs) under this counsellor along with CGPA and SGPA
#     cursor.execute('''
#         SELECT 
#             s.usn, 
#             s.name, 
#             cgpa.cgpa, 
#             cgpa.sgpa 
#         FROM 
#             counsellor_student cs
#         JOIN 
#             student s ON cs.usn = s.usn
#         LEFT JOIN 
#             admin_addcgpa cgpa ON s.usn = cgpa.usn
#         WHERE 
#             cs.c_id = %s
#         ORDER BY 
#             s.usn
#     ''', (counsellor_id,))

#     cgpa_records = cursor.fetchall()
#     cursor.close()

#     # Render the profile page with the CGPA and SGPA data
#     return render_template('view_student_cgpa.html', cgpa_records=cgpa_records)



@app.route('/counsellor/logout')
def counsellor_logout():
    session.clear()
    return redirect(url_for('select_user'))
#------------------------------------------------------------------------------------------



#admin----------------------------------------------------------------------
# @app.route("/admin")
# def admin_login():
#     return render_template("admin_login_page.html")


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
            session['a_logged_in'] = True
            session['email'] = admin_email
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials')
    
    return render_template('admin_login_page.html')


@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('a_logged_in'):
        return redirect(url_for('register_login_admin'))

    # Fetch students and subjects for dropdowns
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT usn FROM student')
    students = cursor.fetchall()
    
    cursor.execute('SELECT subject_id, subject_name FROM admin_addsubject')
    subjects = cursor.fetchall()
    cursor.execute('SELECT usn, cgpa, sgpa FROM admin_addcgpa')
    cgpa_records = cursor.fetchall()

    if request.method == 'POST':
        action = request.form.get('action')

        # Handle adding subject
        if action == 'add_subject':
            subject_name = request.form['subject_name']
            course_code = request.form['course_code']
            sem_number = request.form['sem_number']
            
            cursor = mysql.connection.cursor()
            cursor.execute(
                'INSERT INTO admin_addsubject (subject_name, course_code, sem_number) VALUES (%s, %s, %s)', 
                (subject_name, course_code, sem_number)
            )
            mysql.connection.commit()
            cursor.close()
            flash('Subject added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))

        # Handle adding test and quiz scores
        elif action == 'add_scores':
            usn = request.form['usn']
            subject_id = request.form['subject_id']
            test_number = request.form['test_number']
            test_score = request.form['test_score']
            quiz_score = request.form['quiz_score']
            
            cursor = mysql.connection.cursor()
            cursor.execute(
                'INSERT INTO admin_addscores (usn, subject_id, test_number, test_score, quiz_score) VALUES (%s, %s, %s, %s, %s)', 
                (usn, subject_id, test_number, test_score, quiz_score)
            )
            mysql.connection.commit()
            cursor.close()
            flash('Test and quiz scores added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        

   

    if request.method == 'POST':
        action = request.form.get('action')

        # Handle adding/updating CGPA and SGPA
        if action == 'add_update_cgpa':
            usn = request.form['usn']
            cgpa = request.form['cgpa']
            sgpa = request.form['sgpa']

            cursor.execute(
                'INSERT INTO admin_addcgpa (usn, cgpa, sgpa) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE cgpa = %s, sgpa = %s', 
                (usn, cgpa, sgpa, cgpa, sgpa)
            )
            mysql.connection.commit()
            flash('CGPA and SGPA updated successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        

        elif action == 'update_cgpa':
            usn = request.form['usn']  # This gets the USN of the record being updated
            cgpa = request.form.get(f'cgpa_{usn}')
            sgpa = request.form.get(f'sgpa_{usn}')

            if cgpa is not None and sgpa is not None:
                cursor.execute(
                    'UPDATE admin_addcgpa SET cgpa = %s, sgpa = %s WHERE usn = %s',
                    (cgpa, sgpa, usn)
                )
                mysql.connection.commit()
                flash('CGPA and SGPA updated successfully!', 'success')
                return redirect(url_for('admin_dashboard'))
            
        elif action == 'add_attendance':
            usn = request.form['usn']
            subject_id = request.form['subject_id']
            attendance_percentage = request.form['attendance_percentage']

            cursor.execute(
                'INSERT INTO admin_addattendance (usn, subject_id, attendance) VALUES (%s, %s, %s)',
                (usn, subject_id, attendance_percentage)
            )
            mysql.connection.commit()
            flash('Attendance added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))

    return render_template('admin_dashboard.html', students=students, subjects=subjects, cgpa_records=cgpa_records)







@app.route('/admin/logout')
def admin_logout():
    session['a_logged_in']=False
    return redirect(url_for('register_login_admin'))
#------------------------------------------------------------------------------------------

@app.route("/")
@app.route("/home")
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM announcements ORDER BY date DESC LIMIT 3")
    latest_announcements = cursor.fetchall()
    cursor.close()
    return render_template('home.html', announcements=latest_announcements)




#-----------Announcements-----Start------------------------

# route for Announcements page - For Faculty view
@app.route('/announcements')
def announcements():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Retrieve announcements where author matches the session's name
    query = 'SELECT * FROM announcements WHERE author = %s ORDER BY date DESC'
    cursor.execute(query, (session['name'],))
    announcements = cursor.fetchall()
    cursor.close()
    return render_template('announcements.html', announcements=announcements)

# route for Announcements page - For Student view
@app.route('/student_announcements')
def student_announcements():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Get the student's USN from the session
    usn = session['usn']
    
    # Find the counsellor assigned to the student
    query = '''
        SELECT c.c_name
        FROM counsellor_student cs
        JOIN counsellor c ON cs.c_id = c.c_id
        WHERE cs.usn = %s
    '''
    cursor.execute(query, (usn,))
    counsellor = cursor.fetchone()
    
    if counsellor:
        counsellor_name = counsellor['c_name']
        
        # Retrieve announcements made by the counsellor
        query = '''
            SELECT * 
            FROM announcements
            WHERE author = %s
            ORDER BY date DESC
        '''
        cursor.execute(query, (counsellor_name,))
        announcements = cursor.fetchall()
    else:
        announcements = []
    
    cursor.close()
    return render_template('student_announcements.html', announcements=announcements)



# route for create-Announcements page
@app.route('/create-announcement')
def create_announcements():
    return render_template('create-announcement.html')

# After submitting the create announcement form
@app.route('/submit-announcement', methods=['POST'])
def submit_announcement():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        link = request.form.get('link')
        author = session.get('name')
        date = datetime.now().strftime('%Y-%m-%d %H:%M')
        c_id = session.get('counsellor_id')
        
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO announcements (title, content, link, author, date) VALUES (%s, %s, %s, %s, %s)', (title, content, link, author, date))
        mysql.connection.commit()

        # ----Fetch the students who belong to the counsellor's batch----#
        cursor.execute('''
            SELECT DISTINCT s.email_id 
            FROM student s
            JOIN counsellor_student cs ON s.usn = cs.usn
            WHERE cs.c_id = %s
        ''', (c_id,))
        student_emails = cursor.fetchall()
        cursor.close()

        #----send mail----#
        with mail.connect() as conn:
            for email in student_emails:
                msg = Message('New Announcement', 
                              sender='scmsrvce24@gmail.com', 
                              recipients=[email['email_id']])
                msg.body = f"Hello, there is a new announcement titled '{title}'.\n\n{content}\n\nLink: {link if link else ''}\n\nBest regards,\n{author}"
                conn.send(msg)

        flash('Announcement created successfully!')
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

#-----------Announcements-----End------------------------

#-----------Activity-points-----Start------------------------

@app.route('/counsellor/view-activity-points')
def view_activity_points():
    print(f"Session data: {session}")  # Debugging line, To be removed
    if not session.get('c_logged_in'):
        return redirect(url_for('register_login_counsellor'))
     
    c_id = session.get('counsellor_id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
     
    query = """
    SELECT student.*, activity_points.*
    FROM student
    INNER JOIN counsellor_student ON student.usn = counsellor_student.usn
    LEFT JOIN activity_points ON student.usn = activity_points.usn
    WHERE counsellor_student.c_id = %s
    """
    cursor.execute(query, (c_id,))
    students = cursor.fetchall()
    cursor.close()
    for student in students:
        print(f"Student points: {student}")
    return render_template('view_activity_points.html', students=students)

@app.route('/student/update-activity-points', methods=['GET', 'POST'])
def update_activity_points():
    if not session.get('logged_in'):
        return redirect(url_for('student_login'))  # Redirect to login if not logged in

    usn = session.get('usn')  # Assuming the user's USN is stored in the session
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Retrieve existing data for the student
    query = """
    SELECT points, drive_link FROM activity_points WHERE usn = %s
    """
    cursor.execute(query, (usn,))
    data = cursor.fetchone()  # Fetch the existing data
    cursor.close()

    # Set default values if data is None (i.e., no entry found)
    points = data['points'] if data else ''
    drive_link = data['drive_link'] if data else ''

    if request.method == 'POST':
        points = request.form['points']
        drive_link = request.form['drive_link']

        # Update the activity_points table in the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = """
        INSERT INTO activity_points (usn, points, drive_link)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
        points = VALUES(points),
        drive_link = VALUES(drive_link)
        """
        cursor.execute(query, (usn, points, drive_link))
        mysql.connection.commit()
        cursor.close()

        flash('Activity points updated successfully!')
        return redirect(url_for('student_dashboard'))  # Redirect to the student dashboard or another page

    return render_template('update_activity_points.html', points=points, drive_link=drive_link)

#-----------Activity-points-----End------------------------

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

# schedule meetings html page will be rendered.
@app.route('/schedule_meetings')
def schedule_meetings():
    return render_template('schedule_meetings.html')

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



@app.route('/counsellor/dashboard/academic_profile/view_test_scores/<subject_id>', methods=['GET'])
def view_test_scores(subject_id):
    if not session.get('c_logged_in'):
        return redirect(url_for('register_login_counsellor'))
    
    c_id = session.get('counsellor_id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch students assigned to the counsellor
    cursor.execute("SELECT usn FROM counsellor_student WHERE c_id = %s", (c_id,))
    students = cursor.fetchall()

    # Initialize scores data
    scores_data = {}

    # Prepare a list of USNs to fetch names for
    usn_list = [student['usn'] for student in students]

    # Fetch names for all students in one query
    cursor.execute("SELECT usn, name FROM student WHERE usn IN %s", (tuple(usn_list),))
    student_names = {row['usn']: row['name'] for row in cursor.fetchall()}

    # Fetch scores for the selected subject
    for student in students:
        usn = student['usn']
        
        # Fetch scores and join with the name already obtained
        cursor.execute("""
            SELECT 
                admin_addscores.test_number,
                admin_addscores.test_score,
                admin_addscores.quiz_score
            FROM 
                admin_addscores 
            WHERE 
                admin_addscores.subject_id = %s AND admin_addscores.usn = %s
        """, (subject_id, usn))
        score_result = cursor.fetchall()

        # Initialize the scores_data entry for the student
        scores_data[usn] = {
            'name': student_names.get(usn, ''),  # Get name from the dictionary
            'scores': {}
        }

        # Populate the scores
        for score in score_result:
            test_num = score['test_number']
            scores_data[usn]['scores'][test_num] = {
                'test_score': score['test_score'] if score['test_score'] is not None else 'N/A',
                'quiz_score': score['quiz_score'] if score['quiz_score'] is not None else 'N/A'
            }

    cursor.close()
    return render_template('view_test_scores.html', scores_data=scores_data, subject_id=subject_id)


# @app.route('/view_subject_scores')
# def view_subject_scores():
#     if not session.get('c_logged_in'):
#         return redirect(url_for('register_login_counsellor'))

#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute("SELECT * FROM admin_addsubject")
#     subjects = cursor.fetchall()
#     cursor.close()

#     return render_template('select_subjects.html', subjects=subjects)

if __name__ == '__main__':
    app.run(debug=True)
