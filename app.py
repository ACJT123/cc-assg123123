from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = mysql.connector.connect(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb
)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.tarc.edu.my')



@app.route("/supervisorLoginPage")
def supervisorLoginPage(msg=""):
    return render_template('supervisorLogin.html', msg=msg)

@app.route("/supervisorLogin" , methods=['GET'])
def supervisorLogin():
    id = request.args.get('id')
    password = request.args.get('password')

    print("id",id)
    print("pw",password)

    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM supervisor WHERE id = %s', (id,))
    account = cursor.fetchone()

    if account:
        if password == account[1]:
            return redirect(url_for('supervisorMain', id=account[0]))
        else:
            msg = 'Account exists but password incorrect'
            return redirect(url_for('supervisorLogin', msg=msg))
    else:
        msg = 'Account does not exist'
        return redirect(url_for('supervisorLogin', msg=msg))

    
@app.route("/supervisorMain/<id>")
def supervisorMain(id):
    print("id",id)
    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM student WHERE supervisor_id = %s', (id,))
    students = cursor.fetchall()

    cursor.execute('SELECT * FROM supervisor WHERE id = %s', (id,))
    account = cursor.fetchone()
    print("account",account)
    print("students",students)
    return render_template('supervisorMain.html', students=students, supervisor=account)


@app.route("/evaluatePage/<id>")
def evaluatePage(id):
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM student WHERE id = %s", (id,))
    students = cursor.fetchall()
    return render_template('supervisorEvaluate.html' , students=students)


@app.route("/submit_evaluation", methods=['POST'])
def submitEvaluation():
    student_id = request.form['student_id']
    supervisor_id = request.form['supervisor_id']
    communication_skills = request.form['communication_skills']
    technical_skills = request.form['technical_skills']
    problem_solving = request.form['problem_solving']
    comments = request.form['comments']

    insert_sql = "INSERT INTO evaluation VALUES (%s, %s, %s, %s, %s)"

    # update the isEvaluated field in student table
    update_sql = "UPDATE student SET isEvaluated = 1 WHERE id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (student_id, communication_skills, technical_skills, problem_solving, comments))
        cursor.execute(update_sql, (student_id,))
        db_conn.commit()
    finally:
        cursor.close()

    print("supervisor_id",supervisor_id)
    print("student_id",student_id)
    print("communication_skills",communication_skills)
    print("technical_skills",technical_skills)
    print("problem_solving",problem_solving)
    print("comments",comments)
    return redirect(url_for('supervisorMain', id=supervisor_id))


# Route to admin profile page
@app.route("/supervisorProfile/<supervisor_id>")
def supervisorProfile(supervisor_id):
    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        # Get admin data from database
        cursor.execute('SELECT * FROM supervisor WHERE id = %s', (supervisor_id,))
        account = cursor.fetchone() # If account not exists, account = None
    finally:
        cursor.close()

    print(account[0])
    return render_template('supervisorProfile.html', supervisor_id=supervisor_id, supervisor=account)


@app.route("/editSupervisorProfile/<supervisor_id>")
def editSupervisorProfile(supervisor_id):
    print(supervisor_id)

    # Get user input name, email and phone number from HTML form
    name = request.args.get('name')
    email = request.args.get('email')
    phone = request.args.get('phone')

    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        # Update admin data in database
        cursor.execute('UPDATE supervisor SET name = %s, email = %s, phone_number = %s WHERE id = %s', (name, email, phone, supervisor_id))
        db_conn.commit()

        # Get admin data from database
        cursor.execute('SELECT * FROM supervisor WHERE id = %s', (supervisor_id,))
        account = cursor.fetchone() # If account not exists, account = None
    finally:
        cursor.close()

    return redirect(url_for('supervisorProfile', supervisor_id=supervisor_id, supervisor=account))


# Admin logout function
@app.route("/supervisorLogout")
def supervisorLogout():
    return redirect(url_for('supervisorLoginPage'))





@app.route("/studentLoginPage")
def studentLoginPage(msg=""):
    return render_template('studentLogin.html', msg=msg)

@app.route("/studentLogin", methods=['GET'])
def studentLogin():
    id = request.args.get('id')
    password = request.args.get('password')

    print("id",id)
    print("pw",password)

    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM student WHERE id = %s', (id,))
    account = cursor.fetchone()

    if account:
        if password == account[3]:
            return redirect(url_for('student', id=id))
        else:
            msg = 'Account exists but password incorrect'
            return redirect(url_for('studentLogin', msg=msg))
    else:
        msg = 'Account does not exist'
        return redirect(url_for('studentLogin', msg=msg))
    
@app.route("/student/<id>", methods=['GET'])
def student(id):
    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM student WHERE id = %s', (id,))
    account = cursor.fetchone()
    cursor.execute('SELECT * FROM supervisor')
    supervisor = cursor.fetchall()

    return render_template('student.html', account=account, supervisors=supervisor)


@app.route("/adminLogin")
def adminLogin(msg=""):
    return render_template('admin-login.html', msg=msg)


@app.route("/login", methods=['GET'])
def login():
    # Get user input email and password from HTML form
    email = request.args.get('email')
    password = request.args.get('password')

    # Console log for debugging
    print(email)
    print(password)

    # Check if email exists in accounts table in out database
    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM admin WHERE email = %s', (email,))
    account = cursor.fetchone()

    # Console log for debugging
    print(account)  # If account not exists, account = None

    # If account exists in accounts table in out database
    if account:
        # Check if password correct
        if password == account[2]:
            # If password correct, redirect to admin page
            return redirect(url_for('admin'))
        else:
            # If password incorrect, redirect to admin login page with error message
            msg = 'Account exists but password incorrect'
            return redirect(url_for('adminLogin', msg=msg))
    # If account not exists in accounts table in out database
    else:
        msg = 'Account does not exists'
        return redirect(url_for('adminLogin', msg=msg))


@app.route("/xy")
def xyPortfolio():
    return render_template('xy-portfolio.html')


@app.route("/kelvin")
def kelvinPortfolio():
    return render_template('kelvin-portfolio.html')


@app.route("/kh")
def khPortfolio():
    return render_template('kh-portfolio.html')


@app.route("/jt")
def jtPortfolio():
    return render_template('jt-portfolio.html')


@app.route("/yk")
def ykPortfolio():
    return render_template('yk-portfolio.html')


# @app.route("/addemp", methods=['POST'])
# def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name,
                       last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        # emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        # s3 = boto3.resource('s3')

        # try:
        #     print("Data inserted in MySQL RDS... uploading image to S3...")
        #     s3.Bucket(custombucket).put_object(
        #         Key=emp_image_file_name_in_s3, Body=emp_image_file)
        #     bucket_location = boto3.client(
        #         's3').get_bucket_location(Bucket=custombucket)
        #     s3_location = (bucket_location['LocationConstraint'])

        #     if s3_location is None:
        #         s3_location = ''
        #     else:
        #         s3_location = '-' + s3_location

        #     object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
        #         s3_location,
        #         custombucket,
        #         emp_image_file_name_in_s3)

        # except Exception as e:
        #     return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
