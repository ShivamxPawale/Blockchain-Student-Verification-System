from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from web3 import Web3
import hashlib

app = Flask(__name__)
app.secret_key = 'anything_but_an_error_will_make_me_triggered'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
db = SQLAlchemy(app)

# Connect to Ganache blockchain
web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
contract_address = '0x383d4fbC4F33f3Df61f40c08dF6fFe026DEB83FE'
contract_abi = [
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "string",
          "name": "uhi",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "name",
          "type": "string"
        }
      ],
      "name": "StudentRegistered",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "string",
          "name": "uhi",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "name",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "bool",
          "name": "isValid",
          "type": "bool"
        }
      ],
      "name": "StudentVerified",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_instituteCode",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_uhi",
          "type": "string"
        }
      ],
      "name": "registerStudent",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_uhi",
          "type": "string"
        }
      ],
      "name": "verifyStudent",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    }
  ]
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Database Models
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    institute_code = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    meeting_link = db.Column(db.String(255), nullable=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    institute_code = db.Column(db.String(50), nullable=False)
    uhi = db.Column(db.String(255), unique=True, nullable=False)

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Admin Registration
@app.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        name = request.form['name']
        institute_code = request.form['institute_code']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        admin = Admin(name=name, institute_code=institute_code, password=password)
        db.session.add(admin)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('register_admin.html')

# Admin Login
@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        name = request.form['name']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        admin = Admin.query.filter_by(name=name, password=password).first()
        if admin:
            session['admin_id'] = admin.id
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login_admin.html')

# Admin Dashboard
@app.route('/dashboard')
def dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('login_admin'))
    return render_template('dashboard.html')

# Update Meeting Link
@app.route('/update_meeting_link', methods=['GET', 'POST'])
def update_meeting_link():
    admin = Admin.query.first()  # Fetch the first admin (Modify based on your logic)

    if request.method == 'POST':
        if 'meeting_link' not in request.form:
            flash("Meeting link is missing in the form!", "danger")
            return redirect(url_for('update_meeting_link'))

        admin.meeting_link = request.form['meeting_link']
        db.session.commit()
        flash("Meeting link updated successfully!", "success")
        return redirect(url_for('dashboard'))  # Redirect to admin dashboard

    return render_template('update_meeting_link.html', admin=admin)

# Register Student
from flask import render_template, request, redirect, url_for, session, flash
import hashlib

@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if 'admin_id' not in session:
        flash("Unauthorized access! Please log in.", "danger")
        return redirect(url_for('admin_login'))  # Redirect to admin login page

    if request.method == 'POST':
        name = request.form.get('name')
        institute_code = request.form.get('institute_code')

        if not name or not institute_code:
            flash("All fields are required!", "danger")
            return redirect(url_for('register_student'))

        # Generate Unique Hash Identifier (UHI)
        uhi = institute_code + "-" + hashlib.sha256((name).encode()).hexdigest()

        # Store in SQL Database
        student = Student(name=name, institute_code=institute_code, uhi=uhi)
        db.session.add(student)
        db.session.commit()

        # Register Student in Blockchain
        tx_hash = contract.functions.registerStudent(name, institute_code, uhi).transact({'from': web3.eth.accounts[0]})
        web3.eth.wait_for_transaction_receipt(tx_hash)

        flash('Student registered successfully!', 'success')
        return redirect(url_for('dashboard'))  # Redirect to dashboard after success

    return render_template('register_student.html')  # Render student registration form on GET request


# Verify Student
@app.route('/verify_student', methods=['GET', 'POST'])
def verify_student():
    if request.method == 'POST':
        name = request.form['name']
        institute_code = request.form['institute_code']
        uhi = request.form['uhi']
        student = Student.query.filter_by(name=name, institute_code=institute_code, uhi=uhi).first()
        if student:
            is_valid = contract.functions.verifyStudent(name, uhi).call()
            if is_valid:
                admin = Admin.query.filter_by(institute_code=institute_code).first()
                return redirect(admin.meeting_link) if admin else 'No meeting link found'
        flash('Invalid student details!', 'danger')
    return render_template('verify_student.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)