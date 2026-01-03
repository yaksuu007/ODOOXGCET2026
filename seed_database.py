"""
Database Seeding Script
Adds default employees, attendance records, and other data to the database
"""
from app import app, db, User, Attendance, LeaveRequest
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta
import random
import os

# Sample data for employees
EMPLOYEES_DATA = [
    {
        "employee_id": "EMP001",
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith@dayflow.com",
        "password": "password123",
        "role": "Employee",
        "department": "IT",
        "position": "Senior Software Engineer",
        "phone": "+1-555-0101",
        "address": "123 Main St, New York, NY 10001",
        "salary": 95000.00,
        "hire_date": date(2022, 1, 15)
    },
    {
        "employee_id": "EMP002",
        "first_name": "Sarah",
        "last_name": "Johnson",
        "email": "sarah.johnson@dayflow.com",
        "password": "password123",
        "role": "Employee",
        "department": "Marketing",
        "position": "Marketing Manager",
        "phone": "+1-555-0102",
        "address": "456 Oak Ave, Los Angeles, CA 90001",
        "salary": 85000.00,
        "hire_date": date(2022, 3, 20)
    },
    {
        "employee_id": "EMP003",
        "first_name": "Michael",
        "last_name": "Brown",
        "email": "michael.brown@dayflow.com",
        "password": "password123",
        "role": "Employee",
        "department": "Finance",
        "position": "Financial Analyst",
        "phone": "+1-555-0103",
        "address": "789 Pine Rd, Chicago, IL 60601",
        "salary": 75000.00,
        "hire_date": date(2022, 5, 10)
    },
    {
        "employee_id": "EMP004",
        "first_name": "Emily",
        "last_name": "Davis",
        "email": "emily.davis@dayflow.com",
        "password": "password123",
        "role": "Employee",
        "department": "HR",
        "position": "HR Specialist",
        "phone": "+1-555-0104",
        "address": "321 Elm St, Houston, TX 77001",
        "salary": 70000.00,
        "hire_date": date(2022, 7, 5)
    },
    {
        "employee_id": "EMP005",
        "first_name": "David",
        "last_name": "Wilson",
        "email": "david.wilson@dayflow.com",
        "password": "password123",
        "role": "Employee",
        "department": "Sales",
        "position": "Sales Representative",
        "phone": "+1-555-0105",
        "address": "654 Maple Dr, Phoenix, AZ 85001",
        "salary": 65000.00,
        "hire_date": date(2022, 9, 12)
    },
    {
        "employee_id": "EMP006",
        "first_name": "Jessica",
        "last_name": "Martinez",
        "email": "jessica.martinez@dayflow.com",
        "password": "password123",
        "role": "Employee",
        "department": "Engineering",
        "position": "DevOps Engineer",
        "phone": "+1-555-0106",
        "address": "987 Cedar Ln, Philadelphia, PA 19101",
        "salary": 90000.00,
        "hire_date": date(2023, 1, 8)
    },
    {
        "employee_id": "EMP007",
        "first_name": "Robert",
        "last_name": "Taylor",
        "email": "robert.taylor@dayflow.com",
        "password": "password123",
        "role": "Employee",
        "department": "Design",
        "position": "UI/UX Designer",
        "phone": "+1-555-0107",
        "address": "147 Birch St, San Antonio, TX 78201",
        "salary": 80000.00,
        "hire_date": date(2023, 2, 14)
    },
    {
        "employee_id": "EMP008",
        "first_name": "Amanda",
        "last_name": "Anderson",
        "email": "amanda.anderson@dayflow.com",
        "password": "password123",
        "role": "Employee",
        "department": "Operations",
        "position": "Operations Manager",
        "phone": "+1-555-0108",
        "address": "258 Spruce Ave, San Diego, CA 92101",
        "salary": 88000.00,
        "hire_date": date(2023, 4, 3)
    },
    {
        "employee_id": "HR001",
        "first_name": "Admin",
        "last_name": "User",
        "email": "admin@dayflow.com",
        "password": "admin123",
        "role": "HR",
        "department": "HR",
        "position": "HR Manager",
        "phone": "+1-555-0001",
        "address": "100 Admin Blvd, New York, NY 10001",
        "salary": 120000.00,
        "hire_date": date(2021, 1, 1)
    }
]

def generate_profile_image_url(first_name, last_name):
    """Generate a profile image URL using UI Avatars API"""
    initials = f"{first_name[0]}{last_name[0]}".upper()
    return f"https://ui-avatars.com/api/?name={first_name}+{last_name}&size=200&background=667eea&color=fff&bold=true"

def create_attendance_records(user, start_date, end_date):
    """Create attendance records for a user between start_date and end_date"""
    current_date = start_date
    attendance_records = []
    
    while current_date <= end_date:
        # Skip weekends (Saturday=5, Sunday=6)
        if current_date.weekday() < 5:  # Monday to Friday
            # Randomly decide if employee is present (90% chance)
            if random.random() < 0.9:
                # Generate check-in time between 8:00 AM and 9:30 AM
                check_in_hour = random.randint(8, 9)
                check_in_minute = random.choice([0, 15, 30, 45]) if check_in_hour == 8 else random.choice([0, 15, 30])
                check_in = datetime.combine(current_date, datetime.min.time().replace(hour=check_in_hour, minute=check_in_minute))
                
                # Generate check-out time between 5:00 PM and 6:30 PM
                check_out_hour = random.randint(17, 18)
                check_out_minute = random.choice([0, 15, 30, 45]) if check_out_hour == 17 else random.choice([0, 15, 30])
                check_out = datetime.combine(current_date, datetime.min.time().replace(hour=check_out_hour, minute=check_out_minute))
                
                status = "Present"
            else:
                # 10% chance of being absent or on leave
                if random.random() < 0.5:
                    status = "Absent"
                    check_in = None
                    check_out = None
                else:
                    status = "Leave"
                    check_in = None
                    check_out = None
            
            attendance = Attendance(
                user_id=user.id,
                date=current_date,
                check_in=check_in.time() if check_in else None,
                check_out=check_out.time() if check_out else None,
                status=status
            )
            attendance_records.append(attendance)
        
        current_date += timedelta(days=1)
    
    return attendance_records

def create_leave_requests(user):
    """Create some sample leave requests for a user"""
    leave_requests = []
    
    # Create 2-3 random leave requests in the past 6 months
    for _ in range(random.randint(2, 3)):
        # Random start date in the past 6 months
        days_ago = random.randint(30, 180)
        start_date = date.today() - timedelta(days=days_ago)
        
        # Leave duration: 1-5 days
        duration = random.randint(1, 5)
        end_date = start_date + timedelta(days=duration - 1)
        
        leave_type = random.choice(["Paid", "Sick", "Unpaid"])
        status = random.choice(["Approved", "Pending", "Rejected"])
        
        leave_request = LeaveRequest(
            user_id=user.id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            remarks=f"Leave request for {leave_type.lower()} leave",
            status=status,
            admin_comment="Approved by HR" if status == "Approved" else None
        )
        leave_requests.append(leave_request)
    
    return leave_requests

def seed_database():
    """Main function to seed the database"""
    with app.app_context():
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("Clearing existing data...")
        db.session.query(LeaveRequest).delete()
        db.session.query(Attendance).delete()
        db.session.query(User).delete()
        db.session.commit()
        
        print("Creating employees...")
        users = []
        
        for emp_data in EMPLOYEES_DATA:
            # Check if user already exists
            existing_user = User.query.filter_by(employee_id=emp_data["employee_id"]).first()
            if existing_user:
                print(f"Employee {emp_data['employee_id']} already exists, skipping...")
                users.append(existing_user)
                continue
            
            # Create user
            # Generate profile image URL
            profile_image_url = generate_profile_image_url(emp_data["first_name"], emp_data["last_name"])
            
            user = User(
                employee_id=emp_data["employee_id"],
                email=emp_data["email"],
                password=generate_password_hash(emp_data["password"]),
                role=emp_data["role"],
                first_name=emp_data["first_name"],
                last_name=emp_data["last_name"],
                phone=emp_data["phone"],
                address=emp_data["address"],
                department=emp_data["department"],
                position=emp_data["position"],
                salary=emp_data["salary"],
                hire_date=emp_data["hire_date"],
                profile_picture=profile_image_url  # Store URL for placeholder image
            )
            
            db.session.add(user)
            db.session.flush()  # Get the user ID
            
            users.append(user)
            print(f"Created employee: {emp_data['first_name']} {emp_data['last_name']} ({emp_data['employee_id']})")
        
        db.session.commit()
        print(f"\nCreated {len(users)} employees")
        
        # Create attendance records
        print("\nCreating attendance records...")
        today = date.today()
        
        # Create monthly attendance (last 3 months)
        for user in users:
            if user.role == "Employee":  # Only create attendance for employees
                # Last 3 months
                for month_offset in range(3):
                    month_start = date(today.year, today.month, 1) - timedelta(days=30 * month_offset)
                    if month_start.month == today.month:
                        month_start = date(today.year, today.month, 1)
                    else:
                        month_start = date(month_start.year, month_start.month, 1)
                    
                    # Get last day of month
                    if month_start.month == 12:
                        month_end = date(month_start.year + 1, 1, 1) - timedelta(days=1)
                    else:
                        month_end = date(month_start.year, month_start.month + 1, 1) - timedelta(days=1)
                    
                    # Limit to today if it's current month
                    if month_end > today:
                        month_end = today
                    
                    attendance_records = create_attendance_records(user, month_start, month_end)
                    db.session.add_all(attendance_records)
                    print(f"  Created {len(attendance_records)} attendance records for {user.first_name} {user.last_name} ({month_start.strftime('%B %Y')})")
        
        db.session.commit()
        print("Attendance records created")
        
        # Create leave requests
        print("\nCreating leave requests...")
        for user in users:
            if user.role == "Employee":
                leave_requests = create_leave_requests(user)
                db.session.add_all(leave_requests)
                print(f"  Created {len(leave_requests)} leave requests for {user.first_name} {user.last_name}")
        
        db.session.commit()
        print("Leave requests created")
        
        print("\n" + "="*50)
        print("Database seeding completed successfully!")
        print("="*50)
        print("\nDefault Login Credentials:")
        print("-" * 50)
        for emp_data in EMPLOYEES_DATA:
            print(f"Email: {emp_data['email']}")
            print(f"Password: {emp_data['password']}")
            print(f"Role: {emp_data['role']}")
            print("-" * 50)

if __name__ == "__main__":
    seed_database()

