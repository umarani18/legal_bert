from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import pandas as pd
import numpy as np
from datetime import datetime
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import re
import random

app = Flask(__name__)
app.secret_key = 'legal_advisor_secret_key'  # Should be a secure key in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///legal_advisor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

db = SQLAlchemy(app)

# User database model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    cases = db.relationship('Case', backref='user', lazy=True)

# Case database model
class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    date_created = db.Column(db.DateTime, server_default=db.func.now())
    analysis_result = db.Column(db.Text)
    assignments = db.relationship('LawyerAssignment', backref='case', lazy=True)
    
# Lawyer Assignment model
class LawyerAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    lawyer_id = db.Column(db.Integer, nullable=False)
    lawyer_name = db.Column(db.String(100), nullable=False)
    case_type = db.Column(db.String(50), nullable=False)
    date_assigned = db.Column(db.DateTime, server_default=db.func.now())
    status = db.Column(db.String(50), default='Pending')
    client_name = db.Column(db.String(100), nullable=False)
    notes = db.relationship('LawyerNote', backref='assignment', lazy=True)

# Lawyer Note model for storing updates and notes
class LawyerNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('lawyer_assignment.id'), nullable=False)
    note_text = db.Column(db.Text, nullable=False)
    date_added = db.Column(db.DateTime, server_default=db.func.now())
    status_at_time = db.Column(db.String(50))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['name'] = user.name
            session['is_admin'] = user.is_admin
            
            flash('Login successful!', 'success')
            
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('login'))
        
        # Create new user with hashed password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, email=email, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    if session.get('is_admin', False):
        return redirect(url_for('admin_dashboard'))
    
    # Get user's recent cases
    recent_cases = Case.query.filter_by(user_id=session['user_id']).order_by(Case.date_created.desc()).limit(5).all()
    
    return render_template('user_dashboard.html', recent_cases=recent_cases)

# Function to analyze case using BERT model
def analyze_case_with_bert(text):
    model_path = "/home/umarani/project/legal_advisor/Main_app/model/legal_bert_model"
    tokenizer = BertTokenizer.from_pretrained(model_path)
    model = BertForSequenceClassification.from_pretrained(model_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    if tokenizer is None or model is None:
        return "Unable to load the legal analysis model. Please try again later."
    
    # Preprocess the text
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    predicted_label = torch.argmax(outputs.logits, dim=1).item()
    category_mapping = {0: "Criminal", 1: "Civil", 2: "Invalid Case"}
    print(category_mapping[predicted_label])
    return category_mapping[predicted_label]

@app.route('/case_analysis', methods=['GET', 'POST'])
def case_analysis():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    analysis_result=None
    if request.method == 'POST':
        description = request.form['description']
        
        # Create a new case
        new_case = Case(
            user_id=session['user_id'],
            description=description,
            status='Analyzing',
            date_created=datetime.now()
        )
        
        db.session.add(new_case)
        db.session.commit()
        # Analyze the case
        try:
            analysis_result = analyze_case_with_bert(description)
        except Exception as e:
            print(f"Analysis failed: {e}")
            analysis_result = "We encountered an issue during analysis. "
        
        # Update the case with analysis results
        new_case.analysis_result = analysis_result
        new_case.status = 'Analyzed'
        db.session.commit()
        
        flash('Case submitted and analyzed successfully!', 'success')
        return redirect(url_for('view_case', case_id=new_case.id))
    
    return render_template('case_analysis.html', analysis_result=analysis_result)

@app.route('/view_case/<int:case_id>')
def view_case(case_id):
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    case = Case.query.get_or_404(case_id)
    
    # Ensure the user can only view their own cases unless they're an admin
    if case.user_id != session['user_id'] and not session.get('is_admin', False):
        flash('You do not have permission to view this case', 'danger')
        return redirect(url_for('user_dashboard'))
    
    # Get lawyer assignment and notes if the case is assigned to a lawyer
    lawyer_assignment = LawyerAssignment.query.filter_by(case_id=case.id).first()
    lawyer_notes = []
    
    if lawyer_assignment:
        # Get all notes for this case, ordered by most recent first
        lawyer_notes = LawyerNote.query.filter_by(assignment_id=lawyer_assignment.id).order_by(LawyerNote.date_added.desc()).all()
    
    return render_template('view_case.html', 
                          case=case, 
                          lawyer_assignment=lawyer_assignment,
                          lawyer_notes=lawyer_notes)

@app.route('/my_cases')
def my_cases():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    cases = Case.query.filter_by(user_id=session['user_id']).order_by(Case.date_created.desc()).all()
    return render_template('my_cases.html', cases=cases)


@app.route('/find_lawyers', methods=['GET', 'POST'])
def find_lawyers_route():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    categories = ["Criminal", "Civil"]
    lawyers = []
    search_performed = False
    
    # Get user's cases for the dropdown
    user_cases = Case.query.filter_by(user_id=session['user_id']).all()

    if request.method == 'POST':
        district = request.form.get('district')
        case_type = request.form.get('case_type')
        
        if district and case_type:
            # Get lawyers using the CSV file
            lawyer_df = pd.read_csv("/home/umarani/project/legal_advisor/Main_app/data/LawyerDataFinal (1).csv")
            
            # Clean and filter the data
            lawyer_df['district'] = lawyer_df['district'].str.lower().str.strip()
            lawyer_df['Category'] = lawyer_df['Category'].str.lower().str.strip()
            district = district.strip().lower()
            case_type = case_type.lower()
            
            # Filter lawyers by district and case type
            filtered_df = lawyer_df[(lawyer_df['district'] == district) & (lawyer_df['Category'] == case_type)]
            
            if not filtered_df.empty:
                lawyers_list = filtered_df.to_dict('records')
                lawyers = random.sample(lawyers_list, min(2, len(lawyers_list)))
                search_performed = True
            else:
                flash(f'No lawyers found for {district} district with expertise in {case_type} cases.', 'warning')
                search_performed = True
    
    return render_template('find_lawyers.html', 
                          lawyers=lawyers, 
                          categories=categories, 
                          search_performed=search_performed,
                          user_cases=user_cases)

@app.route('/request_lawyer', methods=['POST'])
def request_lawyer():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    lawyer_id = request.form.get('lawyer_id')
    lawyer_name = request.form.get('lawyer_name')
    case_id = request.form.get('case_id')
    case_type = request.form.get('case_type')
    
    # Validate the data
    if not all([lawyer_id, lawyer_name, case_id, case_type]):
        flash('Missing required information', 'danger')
        return redirect(url_for('find_lawyers_route'))
    
    # Get the case and verify it belongs to the current user
    case = Case.query.get_or_404(case_id)
    if case.user_id != session['user_id']:
        flash('You do not have permission to assign this case', 'danger')
        return redirect(url_for('find_lawyers_route'))
    
    # Check if this case is already assigned to a lawyer
    existing_assignment = LawyerAssignment.query.filter_by(case_id=case_id).first()
    if existing_assignment:
        flash('This case is already assigned to a lawyer', 'warning')
        return redirect(url_for('my_cases'))
    
    # Create the lawyer assignment
    assignment = LawyerAssignment(
        case_id=case_id,
        lawyer_id=lawyer_id,
        lawyer_name=lawyer_name,
        case_type=case_type,
        status='Pending',
        client_name=session['name']
    )
    
    # Update the case status
    case.status = 'Assigned to Lawyer'
    
    db.session.add(assignment)
    db.session.commit()
    
    flash(f'Case #{case_id} assigned to {lawyer_name}', 'success')
    return redirect(url_for('my_cases'))

import csv
import pandas as pd

# Existing imports...

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        lawyer_id = request.form['lawyer_id']
        phone_number = request.form['phone_number']
        
        # Load lawyer data from CSV
        csv_path = "/home/umarani/project/legal_advisor/Main_app/data/LawyerDataFinal (1).csv"
        lawyers_df = pd.read_csv(csv_path)
        
        # Convert lawyer_id to integer for comparison
        try:
            lawyer_id = str(lawyer_id)
            phone_number = str(phone_number)
        except ValueError:
            flash('Invalid Lawyer ID format', 'danger')
            return render_template('admin_login.html')
        print(lawyer_id)
        # Find lawyer in DataFrame
        lawyer_row = lawyers_df.loc[lawyers_df['lawyer_id'] == lawyer_id]
        print(lawyer_row)
        if not lawyer_row.empty:
            # Check if phone number matches
            
            if str(int(lawyer_row['phone_number'].values[0])) == phone_number:
                session['user_id'] = f"lawyer_{lawyer_id}"  # Prefix to distinguish from regular users
                session['name'] = lawyer_row['lawyer_name'].values[0]
                session['is_admin'] = True
                session['lawyer_id'] = lawyer_id
                session['district'] = lawyer_row['district'].values[0]
                session['category'] = lawyer_row['Category'].values[0]
                
                flash('Login successful!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid phone number', 'danger')
        else:
            flash('Lawyer ID not found', 'danger')
    
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin', False):
        flash('Please login with admin credentials', 'warning')
        return redirect(url_for('admin_login'))
    
    # Get current date for display
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Get lawyer ID from session
    lawyer_id = session.get('lawyer_id')
    
    # Get assigned cases for this lawyer
    assigned_cases = LawyerAssignment.query.filter_by(lawyer_id=lawyer_id).all()
    
    # Count pending and resolved cases
    pending_cases = sum(1 for case in assigned_cases if case.status == 'Pending')
    resolved_cases = sum(1 for case in assigned_cases if case.status == 'Resolved')
    
    # Format case data for display in the table
    recent_cases = []
    for assignment in assigned_cases:
        case = Case.query.get(assignment.case_id)
        if case:
            recent_cases.append({
                'id': case.id,
                'client_name': assignment.client_name,
                'case_type': assignment.case_type,
                'date_assigned': assignment.date_assigned.strftime('%d %b %Y'),
                'status': assignment.status
            })
    
    return render_template('admin_dashboard.html', 
                          current_date=current_date,
                          pending_cases=pending_cases,
                          resolved_cases=resolved_cases,
                          upcoming_appointments=len(assigned_cases),
                          rating=4.8,  # Placeholder value
                          recent_cases=recent_cases)

@app.route('/lawyer_view_case/<int:case_id>')
def lawyer_view_case(case_id):
    if 'user_id' not in session or not session.get('is_admin', False):
        flash('Please login with lawyer credentials', 'warning')
        return redirect(url_for('admin_login'))
    
    # Get lawyer ID from session
    lawyer_id = session.get('lawyer_id')
    
    # Get the assignment for this case
    assignment = LawyerAssignment.query.filter_by(case_id=case_id, lawyer_id=lawyer_id).first()
    
    if not assignment:
        flash('You do not have permission to view this case', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    # Get the case details
    case = Case.query.get_or_404(case_id)
    
    # Get the client details
    client = User.query.get(case.user_id)
    
    return render_template('lawyer_view_case.html', 
                          case=case, 
                          assignment=assignment, 
                          client=client)

@app.route('/update_case_status/<int:case_id>', methods=['POST'])
def update_case_status(case_id):
    if 'user_id' not in session or not session.get('is_admin', False):
        flash('Please login with lawyer credentials', 'warning')
        return redirect(url_for('admin_login'))
    
    # Get lawyer ID from session
    lawyer_id = session.get('lawyer_id')
    
    # Get the assignment for this case
    assignment = LawyerAssignment.query.filter_by(case_id=case_id, lawyer_id=lawyer_id).first()
    
    if not assignment:
        flash('You do not have permission to update this case', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    # Update the status
    new_status = request.form.get('status')
    notes = request.form.get('notes')
    
    if new_status:
        old_status = assignment.status  # Save previous status for reference
        assignment.status = new_status
        
        # Also update the case status if needed
        case = Case.query.get(case_id)
        if case:
            if new_status == 'Resolved':
                case.status = 'Resolved'
            else:
                case.status = f'Lawyer: {new_status}'
        
        # Save notes if provided
        if notes and notes.strip():
            lawyer_note = LawyerNote(
                assignment_id=assignment.id,
                note_text=notes,
                status_at_time=new_status,
                date_added=datetime.now()
            )
            db.session.add(lawyer_note)
        
        db.session.commit()
        flash(f'Case status updated to {new_status}', 'success')
    else:
        flash('Invalid status', 'danger')
    
    return redirect(url_for('lawyer_view_case', case_id=case_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True)