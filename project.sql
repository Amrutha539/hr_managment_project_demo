-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- Employee Position Table
CREATE TABLE IF NOT EXISTS employee_position (
    emp_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    position TEXT NOT NULL,
    description TEXT
);

-- Department Table (removed department_id)
CREATE TABLE IF NOT EXISTS department (
    department_name TEXT PRIMARY KEY
);

-- Employee Table (renamed employee_id to emp_id, removed department_id and position_id)
CREATE TABLE IF NOT EXISTS employee (
    emp_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    dob DATE,
    position TEXT,
    department_name TEXT,
    FOREIGN KEY (position) REFERENCES employee_position(position) ON DELETE SET NULL,
    FOREIGN KEY (department_name) REFERENCES department(department_name) ON DELETE SET NULL
);

-- Salary Table (removed salary_id)
CREATE TABLE IF NOT EXISTS salary (
    emp_id TEXT,
    amount INTEGER NOT NULL,
    payment_date DATE NOT NULL,
    FOREIGN KEY (emp_id) REFERENCES employee(emp_id) ON DELETE CASCADE
);

-- Attendance Table (removed attendance_id)
CREATE TABLE IF NOT EXISTS attendance (
    emp_id TEXT,
    date DATE NOT NULL,
    status TEXT CHECK(status IN ('Present', 'Absent')),
    FOREIGN KEY (emp_id) REFERENCES employee(emp_id) ON DELETE CASCADE
);

-- Leave Table (removed leave_id)
CREATE TABLE IF NOT EXISTS leave_record (
    emp_id TEXT,
    leave_type TEXT,
    start_date DATE,
    end_date DATE,
    status TEXT,
    FOREIGN KEY (emp_id) REFERENCES employee(emp_id) ON DELETE CASCADE
);

-- Training Table (removed training_id and department_id)
CREATE TABLE IF NOT EXISTS training (
    topic TEXT NOT NULL,
    date DATE NOT NULL,
    department_name TEXT,
    FOREIGN KEY (department_name) REFERENCES department(department_name) ON DELETE SET NULL
);
