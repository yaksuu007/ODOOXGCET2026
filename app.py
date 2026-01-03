from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date, timedelta
import os
from functools import wraps

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hrms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'Employee' or 'HR'
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    department = db.Column(db.String(50))
    position = db.Column(db.String(50))
    hire_date = db.Column(db.Date)
    salary = db.Column(db.Float)
    profile_picture = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='user', lazy=True)
    leave_requests = db.relationship('LeaveRequest', backref='user', lazy=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.Time)
    check_out = db.Column(db.Time)
    status = db.Column(db.String(20), nullable=False)  # Present, Absent, Half-day, Leave
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='unique_user_date'),)

class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)  # Paid, Sick, Unpaid
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    remarks = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected
    admin_comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

# Decorator for login required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('signin'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator for admin required
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('signin'))
        user = User.query.get(session['user_id'])
        if user.role != 'HR':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('employee_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.role == 'HR':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('employee_dashboard'))
    return redirect(url_for('signin'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        
        # Validation
        if not all([employee_id, email, password, role]):
            flash('All fields are required.', 'danger')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('signup.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('signup.html')
        
        # Check if user exists
        if User.query.filter_by(employee_id=employee_id).first():
            flash('Employee ID already exists.', 'danger')
            return render_template('signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('signup.html')
        
        # Create user
        hashed_password = generate_password_hash(password)
        user = User(
            employee_id=employee_id,
            email=email,
            password=hashed_password,
            role=role
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('signin'))
    
    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash(f'Welcome back, {user.first_name or user.email}!', 'success')
            
            if user.role == 'HR':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('employee_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('signin.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('signin'))

@app.route('/employee/dashboard')
@login_required
def employee_dashboard():
    user = User.query.get(session['user_id'])
    if user.role == 'HR':
        return redirect(url_for('admin_dashboard'))
    
    # Get recent attendance
    recent_attendance = Attendance.query.filter_by(user_id=user.id).order_by(Attendance.date.desc()).limit(5).all()
    
    # Get pending leave requests
    pending_leaves = LeaveRequest.query.filter_by(user_id=user.id, status='Pending').count()
    
    return render_template('employee_dashboard.html', user=user, recent_attendance=recent_attendance, pending_leaves=pending_leaves)

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # Get all employees
    employees = User.query.filter_by(role='Employee').all()
    
    # Get recent attendance records
    recent_attendance = Attendance.query.order_by(Attendance.date.desc()).limit(10).all()
    
    # Get pending leave requests
    pending_leaves = LeaveRequest.query.filter_by(status='Pending').count()
    
    return render_template('admin_dashboard.html', employees=employees, recent_attendance=recent_attendance, pending_leaves=pending_leaves)

@app.route('/profile')
@login_required
def profile():
    user_id = request.args.get('user_id')
    current_user = User.query.get(session['user_id'])
    
    # Admin can view any employee profile, employees can only view their own
    if user_id and current_user.role == 'HR':
        user = User.query.get_or_404(user_id)
    else:
        user = current_user
    
    return render_template('profile.html', user=user, current_user=current_user)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user_id = request.args.get('user_id')
    current_user = User.query.get(session['user_id'])
    
    # Admin can edit any employee profile, employees can only edit their own
    if user_id and current_user.role == 'HR':
        user = User.query.get_or_404(user_id)
    else:
        user = current_user
    
    if request.method == 'POST':
        # Employees can edit limited fields
        if user.role == 'Employee' and user.id == session['user_id']:
            user.phone = request.form.get('phone')
            user.address = request.form.get('address')
        elif current_user.role == 'HR':
            # Admin can edit all fields
            user.first_name = request.form.get('first_name')
            user.last_name = request.form.get('last_name')
            user.phone = request.form.get('phone')
            user.address = request.form.get('address')
            user.department = request.form.get('department')
            user.position = request.form.get('position')
            if request.form.get('salary'):
                try:
                    user.salary = float(request.form.get('salary'))
                except ValueError:
                    pass
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                filename = secure_filename(f"{user.id}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.profile_picture = filename
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        if user_id and current_user.role == 'HR':
            return redirect(url_for('profile', user_id=user_id))
        return redirect(url_for('profile'))
    
    return render_template('edit_profile.html', user=user, current_user=current_user)

@app.route('/attendance')
@login_required
def attendance():
    user = User.query.get(session['user_id'])
    view_type = request.args.get('view', 'daily')
    
    if view_type == 'weekly':
        # Get current week's attendance
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        if user.role == 'HR':
            attendance_records = Attendance.query.filter(
                Attendance.date >= start_of_week,
                Attendance.date <= end_of_week
            ).order_by(Attendance.date.desc()).all()
        else:
            attendance_records = Attendance.query.filter_by(user_id=user.id).filter(
                Attendance.date >= start_of_week,
                Attendance.date <= end_of_week
            ).order_by(Attendance.date.desc()).all()
    else:
        # Daily view
        selected_date = request.args.get('date', date.today().isoformat())
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except:
            selected_date = date.today()
        
        if user.role == 'HR':
            attendance_records = Attendance.query.filter_by(date=selected_date).all()
        else:
            attendance_records = Attendance.query.filter_by(user_id=user.id, date=selected_date).all()
    
    return render_template('attendance.html', user=user, attendance_records=attendance_records, view_type=view_type)

@app.route('/attendance/checkin', methods=['POST'])
@login_required
def checkin():
    user = User.query.get(session['user_id'])
    if user.role == 'HR':
        flash('Admins cannot check in.', 'warning')
        return redirect(url_for('attendance'))
    
    today = date.today()
    attendance = Attendance.query.filter_by(user_id=user.id, date=today).first()
    
    if attendance:
        flash('You have already checked in today.', 'warning')
    else:
        attendance = Attendance(
            user_id=user.id,
            date=today,
            check_in=datetime.now().time(),
            status='Present'
        )
        db.session.add(attendance)
        db.session.commit()
        flash('Check-in successful!', 'success')
    
    return redirect(url_for('attendance'))

@app.route('/attendance/checkout', methods=['POST'])
@login_required
def checkout():
    user = User.query.get(session['user_id'])
    if user.role == 'HR':
        flash('Admins cannot check out.', 'warning')
        return redirect(url_for('attendance'))
    
    today = date.today()
    attendance = Attendance.query.filter_by(user_id=user.id, date=today).first()
    
    if attendance:
        if attendance.check_out:
            flash('You have already checked out today.', 'warning')
        else:
            attendance.check_out = datetime.now().time()
            db.session.commit()
            flash('Check-out successful!', 'success')
    else:
        flash('Please check in first.', 'warning')
    
    return redirect(url_for('attendance'))

@app.route('/leave')
@login_required
def leave():
    user = User.query.get(session['user_id'])
    
    if user.role == 'HR':
        # Admin view - all leave requests
        leave_requests = LeaveRequest.query.order_by(LeaveRequest.created_at.desc()).all()
    else:
        # Employee view - own leave requests
        leave_requests = LeaveRequest.query.filter_by(user_id=user.id).order_by(LeaveRequest.created_at.desc()).all()
    
    return render_template('leave.html', user=user, leave_requests=leave_requests)

@app.route('/leave/apply', methods=['GET', 'POST'])
@login_required
def apply_leave():
    user = User.query.get(session['user_id'])
    if user.role == 'HR':
        flash('Admins cannot apply for leave through this form.', 'warning')
        return redirect(url_for('leave'))
    
    if request.method == 'POST':
        leave_type = request.form.get('leave_type')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        remarks = request.form.get('remarks')
        
        if not all([leave_type, start_date, end_date]):
            flash('All required fields must be filled.', 'danger')
            return render_template('apply_leave.html', user=user)
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if end_date < start_date:
                flash('End date must be after start date.', 'danger')
                return render_template('apply_leave.html', user=user)
            
            leave_request = LeaveRequest(
                user_id=user.id,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                remarks=remarks,
                status='Pending'
            )
            db.session.add(leave_request)
            db.session.commit()
            
            flash('Leave request submitted successfully!', 'success')
            return redirect(url_for('leave'))
        except ValueError:
            flash('Invalid date format.', 'danger')
    
    return render_template('apply_leave.html', user=user)

@app.route('/leave/approve/<int:leave_id>', methods=['POST'])
@admin_required
def approve_leave(leave_id):
    leave_request = LeaveRequest.query.get_or_404(leave_id)
    action = request.form.get('action')
    comment = request.form.get('comment', '')
    
    if action == 'approve':
        leave_request.status = 'Approved'
        leave_request.admin_comment = comment
        
        # Update attendance records for leave period
        current_date = leave_request.start_date
        while current_date <= leave_request.end_date:
            attendance = Attendance.query.filter_by(
                user_id=leave_request.user_id,
                date=current_date
            ).first()
            
            if not attendance:
                attendance = Attendance(
                    user_id=leave_request.user_id,
                    date=current_date,
                    status='Leave'
                )
                db.session.add(attendance)
            
            current_date += timedelta(days=1)
        
        flash('Leave request approved!', 'success')
    elif action == 'reject':
        leave_request.status = 'Rejected'
        leave_request.admin_comment = comment
        flash('Leave request rejected.', 'info')
    
    db.session.commit()
    return redirect(url_for('leave'))

@app.route('/payroll')
@login_required
def payroll():
    user = User.query.get(session['user_id'])
    
    if user.role == 'HR':
        # Admin view - all employees' payroll
        employees = User.query.filter_by(role='Employee').all()
        return render_template('payroll.html', user=user, employees=employees, is_admin=True)
    else:
        # Employee view - own payroll (read-only)
        return render_template('payroll.html', user=user, employees=[user], is_admin=False)

@app.route('/payroll/update/<int:employee_id>', methods=['POST'])
@admin_required
def update_payroll(employee_id):
    employee = User.query.get_or_404(employee_id)
    new_salary = request.form.get('salary')
    
    try:
        employee.salary = float(new_salary)
        db.session.commit()
        flash(f'Salary updated for {employee.first_name or employee.employee_id}', 'success')
    except ValueError:
        flash('Invalid salary amount.', 'danger')
    
    return redirect(url_for('payroll'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

