-- 1. Create Extensions & Enums
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE user_role AS ENUM ('Employee', 'HR_Admin');
CREATE TYPE leave_status AS ENUM ('Pending', 'Approved', 'Rejected');
CREATE TYPE attendance_status AS ENUM ('Present', 'Absent', 'Half-day', 'Leave');

-- 2. Employee Directory & Auth
-- Combined for simplicity, but password is kept in this protected table.
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR(100) NOT NULL,
    work_email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL, -- Never store plain text!
    department VARCHAR(50),
    job_title VARCHAR(50),
    role user_role DEFAULT 'Employee',
    profile_pic_url TEXT,
    account_status VARCHAR(20) DEFAULT 'Active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Attendance Logs
CREATE TABLE attendance (
    log_id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    work_date DATE NOT NULL DEFAULT CURRENT_DATE,
    clock_in TIMESTAMP WITH TIME ZONE,
    clock_out TIMESTAMP WITH TIME ZONE,
    status attendance_status DEFAULT 'Present',
    -- Total hours can be a generated column or calculated via View
    total_hours NUMERIC(4,2),
    UNIQUE(user_id, work_date) -- Prevents duplicate check-ins for the same day
);

-- 4. Leave Requests
CREATE TABLE leave_requests (
    request_id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    leave_type VARCHAR(50) NOT NULL, -- e.g., 'Sick', 'Paid'
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT,
    approval_status leave_status DEFAULT 'Pending',
    admin_comments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Payroll Records (Strictly Private)
CREATE TABLE payroll (
    payroll_id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    base_salary DECIMAL(12, 2) NOT NULL,
    allowances DECIMAL(12, 2) DEFAULT 0.00,
    deductions DECIMAL(12, 2) DEFAULT 0.00,
    net_payable DECIMAL(12, 2) GENERATED ALWAYS AS (base_salary + allowances - deductions) STORED,
    payment_cycle VARCHAR(20) NOT NULL, -- e.g., 'January 2026'
    is_paid BOOLEAN DEFAULT FALSE
);

-- 6. Notifications
CREATE TABLE notifications (
    notification_id SERIAL PRIMARY KEY,
    target_user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);