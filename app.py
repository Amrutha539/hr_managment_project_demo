import streamlit as st 
import sqlite3
import hashlib
import pandas as pd

# --- Password hashing ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()



# --- Password hashing ---
def initialize_database():
    conn = sqlite3.connect("hrm.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # DO NOT DROP TABLES
    # Tables are created only if they do not already exist

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS department (
            department_id TEXT PRIMARY KEY,
            department_name TEXT UNIQUE NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee (
            emp_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT,
            dob DATE,
            position TEXT,
            department_id TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS salary (
            emp_id TEXT,
            amount INTEGER NOT NULL,
            payment_date DATE NOT NULL,
            bank_details TEXT,
            total_monthly_stipend INTEGER,
            amount_deducted INTEGER,
            payment_method TEXT,
            FOREIGN KEY (emp_id) REFERENCES employee(emp_id) ON DELETE CASCADE,
            PRIMARY KEY (emp_id, payment_date)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            employee_id TEXT,
            date DATE NOT NULL,
            status TEXT CHECK(status IN ('Present', 'Absent')),
            FOREIGN KEY (employee_id) REFERENCES employee(emp_id) ON DELETE CASCADE,
            PRIMARY KEY (employee_id, date)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_record (
            emp_id TEXT,
            leave_type TEXT,
            start_date DATE,
            end_date DATE,
            status TEXT,
            FOREIGN KEY (emp_id) REFERENCES employee(emp_id) ON DELETE CASCADE,
            PRIMARY KEY (emp_id, start_date, end_date)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_title TEXT NOT NULL,
            rule_description TEXT NOT NULL
        );
    """)

    # Insert sample rules if empty
    cursor.execute("SELECT COUNT(*) FROM rules")
    if cursor.fetchone()[0] == 0:
        sample_rules = [
            ("Code of Conduct", "Employees must maintain professional behavior at all times. Harassment, discrimination, or unethical behavior is strictly prohibited."),
            ("Working Hours", "Standard working hours are 9:00 AM to 6:00 PM, Monday to Friday. Late arrivals must be reported to HR in advance."),
            ("Attendance Policy", "Minimum 90% monthly attendance is mandatory. Continuous absence of 3 days without notice may result in disciplinary action."),
            ("Leave Policy", "Leave requests must be submitted at least 3 days in advance. Emergency leave must be informed the same day."),
            ("Salary and Payroll", "Salaries are processed on the 1st of every month. Salary deductions apply for unapproved absences and late arrivals."),
            ("Dress Code", "Employees are expected to wear formal or business casual attire. Dress-down Fridays are permitted unless stated otherwise."),
            ("Data Security and Confidentiality", "Sharing of confidential company data without authorization is a serious offense. Employees must adhere to all IT and security policies."),
            ("Performance Evaluation", "Regular appraisals are conducted every 6 or 12 months. Promotions and bonuses are performance-based."),
            ("Grievance Redressal", "Employees may approach HR with any complaints or grievances. All issues will be addressed confidentially and fairly."),
            ("Exit Policy", "A minimum of 30 days’ notice is required for resignation. Exit interviews and handovers must be completed before departure.")
        ]
        cursor.executemany("INSERT INTO rules (rule_title, rule_description) VALUES (?, ?)", sample_rules)

    conn.commit()
    conn.close()

# --- Display table helper ---
def display_table_with_scroll(df):
    df_display = df.copy()
    df_display.columns = [col.replace('_', ' ').title() for col in df_display.columns]
    st.markdown("""
        <style>
        .table-container {
            overflow-x: auto;
            width: 100%;
            margin-bottom: 1rem;
        }
        table {
            width: 100% !important;
        }
        </style>
        """, unsafe_allow_html=True)
    st.markdown('<div class="table-container">', unsafe_allow_html=True)
    st.dataframe(df_display, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Delete functions ---
def delete_single_record(table, where_clause, params):
    conn = sqlite3.connect("hrm.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute(f"DELETE FROM {table} WHERE {where_clause}", params)
    conn.commit()
    conn.close()

def delete_all_records(table):
    conn = sqlite3.connect("hrm.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute(f"DELETE FROM {table}")
    conn.commit()
    conn.close()

# --- Session defaults ---
if "stored_username" not in st.session_state:
    st.session_state.stored_username = "AMRUTHA"
    st.session_state.stored_password = hash_password("ABCD@123")
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_forgot" not in st.session_state:
    st.session_state.show_forgot = False
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Department"
if "initialized" not in st.session_state:
    initialize_database()
    st.session_state.initialized = True

# --- Page setup ---
st.set_page_config(page_title="HRM Login", layout="centered")

# --- Marquee ---
st.markdown("""
    <div style="width: 100%; overflow: hidden;">
        <marquee behavior="scroll" direction="left" scrollamount="6" style="
            font-size: 60px;
            color: #FF6347;
            font-weight: bold;
        ">
            HUMAN RESOURCE MANAGEMENT SYSTEM
        </marquee>
    </div>
""", unsafe_allow_html=True)

# --- Styling ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
        font-family: 'Arial', sans-serif;
    }
    .stButton > button {
        background: linear-gradient(to right, #f6b93b, #e55039);
        color: white;
        font-weight: bold;
        border: none;
        width: 100%;
        padding: 8px;
        border-radius: 5px;
        font-size: 15px;
        margin-top: 10px;
    }
    .forgot-link {
        display: block;
        margin-top: 12px;
        font-size: 13px;
        color: #7f8c8d;
        text-decoration: underline;
        cursor: pointer;
    }
    .user-icon {
        width: 70px;
        height: 70px;
        border-radius: 50%;
        margin-bottom: 10px;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    .login-title {
        font-size: 28px;
        color: #e74c3c;
        font-weight: bold;
        margin-bottom: 15px;
        text-align: center;
        display: block;
    }
    .main-content {
        margin-left: 270px;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Login and Main Logic ---
# [Code continues with section handling, forms, and deletion — no icon headings now]
# Let me know if you'd like the rest of the updated code pasted here too.


# --- Logged-in UI ---
if st.session_state.logged_in:
    with st.sidebar:
        st.markdown("## HRM MENU")
        if st.button("Employee Details"):
            st.session_state.selected_page = "Employee Details"
        if st.button("Department"):
            st.session_state.selected_page = "Department"
        if st.button("Salary"):
            st.session_state.selected_page = "Salary"
        if st.button("Attendance"):
            st.session_state.selected_page = "Attendance"
        if st.button("Leave Management"):
            st.session_state.selected_page = "Leave Management"
        if st.button("Rules & Regulations"):
            st.session_state.selected_page = "Rules"
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    conn = sqlite3.connect("hrm.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    if st.session_state.selected_page == "Employee Details":
        st.markdown("##  Add Employee Details")
        cursor.execute("SELECT  department_id FROM department")
        departments = [row[0] for row in cursor.fetchall()]
        with st.form("employee_form"):
            emp_id = st.text_input("Employee ID")
            name = st.text_input("Employee Name")
            address = st.text_area("Address")
            dob = st.date_input("Date of Birth")
            position = st.text_input("Position")
            department = st.selectbox("Select Department", departments) if departments else st.text_input("Department Name")
            submit_emp = st.form_submit_button("Add Employee")
            if submit_emp:
                try:
                    cursor.execute(
                        "INSERT INTO employee (emp_id, name, address, dob, position, department_id) VALUES (?, ?, ?, ?, ?, ?)",
                        (emp_id, name, address, dob, position, department)
                    )
                    conn.commit()
                    st.success("✅ Employee added successfully.")
                except sqlite3.IntegrityError:
                    st.error("❌ Employee ID already exists or invalid foreign key.")

        cursor.execute("SELECT * FROM employee")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        display_table_with_scroll(df)

        st.markdown("### Delete Employee Record")
        for i, row in df.iterrows():
            cols = st.columns([5,1])
            cols[0].write(f"ID: {row['emp_id']} | Name: {row['name']}")
            if cols[1].button("Delete", key=f"del_emp_{row['emp_id']}"):
                delete_single_record("employee", "emp_id = ?", (row['emp_id'],))
                st.rerun()

        if st.button("Delete All Employees"):
            delete_all_records("employee")
            st.rerun()

    elif st.session_state.selected_page == "Department":
        st.markdown("## Add Department Details")
        with st.form("department_form"):
            department_id = st.text_input("Department ID")
            department_name = st.text_input("Department Name")
            submit_dept = st.form_submit_button("Add Department")
            if submit_dept:
                try:
                    cursor.execute(
                        "INSERT INTO department (department_id, department_name) VALUES (?, ?)",
                        (department_id, department_name)
                    )
                    conn.commit()
                    st.success("✅ Department added successfully.")
                except sqlite3.IntegrityError:
                    st.error("❌ Department ID already exists.")

        cursor.execute("SELECT * FROM department")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        display_table_with_scroll(df)

        st.markdown("### Delete Department Record")
        for i, row in df.iterrows():
            cols = st.columns([5,1])
            cols[0].write(f"ID: {row['department_id']} | Name: {row['department_name']}")
            if cols[1].button("Delete", key=f"del_dept_{row['department_id']}"):
                delete_single_record("department", "department_id = ?", (row['department_id'],))
                st.rerun()

        if st.button("Delete All Departments"):
            delete_all_records("department")
            st.rerun()

    elif st.session_state.selected_page == "Salary":
        st.markdown("## Salary Management")
        cursor.execute("SELECT emp_id FROM employee")
        emp_ids = [row[0] for row in cursor.fetchall()]
        if not emp_ids:
            st.warning("⚠️ No employees found.")
        else:
            with st.form("salary_form"):
                emp_id = st.selectbox("Select Employee ID", emp_ids)
                amount = st.number_input("Basic Salary Amount", min_value=0)
                total_stipend = st.number_input("Total Monthly Stipend", min_value=0)
                amount_deducted = st.number_input("Amount Deducted", min_value=0)
                bank_details = st.text_input("Bank Details")
                payment_method = st.selectbox("Payment Method", ["Bank Transfer", "Cash", "UPI", "Other"])
                payment_date = st.date_input("Payment Date")
                submit_sal = st.form_submit_button("Add Salary Record")
                if submit_sal:
                    try:
                        cursor.execute("""
                            INSERT INTO salary (emp_id, amount, payment_date, bank_details, total_monthly_stipend, amount_deducted, payment_method)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (emp_id, amount, payment_date, bank_details, total_stipend, amount_deducted, payment_method))
                        conn.commit()
                        st.success("✅ Salary record added.")
                    except sqlite3.IntegrityError:
                        st.error("❌ Invalid Employee ID or duplicate payment date.")

        cursor.execute("""
            SELECT s.emp_id, e.name, s.amount, s.total_monthly_stipend, s.amount_deducted,
                   s.bank_details, s.payment_method, s.payment_date
            FROM salary s
            JOIN employee e ON s.emp_id = e.emp_id
        """)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        display_table_with_scroll(df)

        st.markdown("### Delete Salary Record")
        for i, row in df.iterrows():
            cols = st.columns([6,1])
            cols[0].write(f"Emp ID: {row['emp_id']} | Payment Date: {row['payment_date']} | Amount: {row['amount']}")
            if cols[1].button("Delete", key=f"del_sal_{row['emp_id']}_{row['payment_date']}"):
                delete_single_record("salary", "emp_id = ? AND payment_date = ?", (row['emp_id'], row['payment_date']))
                st.rerun()

        if st.button("Delete All Salaries"):
            delete_all_records("salary")
            st.rerun()

    elif st.session_state.selected_page == "Attendance":
        st.markdown("## Attendance Management")
        cursor.execute("SELECT emp_id FROM employee")
        emp_ids = [row[0] for row in cursor.fetchall()]
        if not emp_ids:
            st.warning("⚠️ No employees found.")
        else:
            with st.form("attendance_form"):
                employee_id = st.selectbox("Select Employee", emp_ids)
                date = st.date_input("Date")
                status = st.radio("Status", ["Present", "Absent"])
                submit_attn = st.form_submit_button("Submit Attendance")
                if submit_attn:
                    try:
                        cursor.execute(
                            "INSERT INTO attendance (employee_id, date, status) VALUES (?, ?, ?)",
                            (employee_id, date, status)
                        )
                        conn.commit()
                        st.success("✅ Attendance recorded.")
                    except sqlite3.IntegrityError:
                        st.error("❌ Error recording attendance.")

        cursor.execute("SELECT * FROM attendance")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        display_table_with_scroll(df)

        st.markdown("### Delete Attendance Record")
        for i, row in df.iterrows():
            cols = st.columns([6,1])
            cols[0].write(f"Emp ID: {row['employee_id']} | Date: {row['date']} | Status: {row['status']}")
            if cols[1].button("Delete", key=f"del_attn_{row['employee_id']}_{row['date']}"):
                delete_single_record("attendance", "employee_id = ? AND date = ?", (row['employee_id'], row['date']))
                st.rerun()

        if st.button("Delete All Attendance Records"):
            delete_all_records("attendance")
            st.rerun()

    elif st.session_state.selected_page == "Leave Management":
        st.markdown("## Leave Management")
        cursor.execute("SELECT emp_id FROM employee")
        emp_ids = [row[0] for row in cursor.fetchall()]
        if not emp_ids:
            st.warning("⚠️ No employees found.")
        else:
            with st.form("leave_form"):
                emp_id = st.selectbox("Select Employee", emp_ids)
                leave_type = st.selectbox("Leave Type", ["Sick Leave", "Casual Leave", "Paid Leave", "Other"])
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date")
                status = st.selectbox("Status", ["Pending", "Approved", "Rejected"])
                submit_leave = st.form_submit_button("Submit Leave")
                if submit_leave:
                    try:
                        cursor.execute(
                            "INSERT INTO leave_record (emp_id, leave_type, start_date, end_date, status) VALUES (?, ?, ?, ?, ?)",
                            (emp_id, leave_type, start_date, end_date, status)
                        )
                        conn.commit()
                        st.success("✅ Leave record added.")
                    except sqlite3.IntegrityError:
                        st.error("❌ Error inserting leave record.")

        cursor.execute("SELECT * FROM leave_record")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        display_table_with_scroll(df)

        st.markdown("### Delete Leave Record")
        for i, row in df.iterrows():
            cols = st.columns([6,1])
            cols[0].write(f"Emp ID: {row['emp_id']} | Leave: {row['leave_type']} | From: {row['start_date']} To: {row['end_date']}")
            if cols[1].button("Delete", key=f"del_leave_{row['emp_id']}_{row['start_date']}_{row['end_date']}"):
                delete_single_record("leave_record", "emp_id = ? AND start_date = ? AND end_date = ?", (row['emp_id'], row['start_date'], row['end_date']))
                st.rerun()

        if st.button("Delete All Leave Records"):
            delete_all_records("leave_record")
            st.rerun()

    elif st.session_state.selected_page == "Rules":
         st.markdown("## HRM Rules & Regulations")

         cursor.execute("SELECT rule_title, rule_description FROM rules")
         rules = cursor.fetchall()

         if rules:
            for i, (title, description) in enumerate(rules, 1):
                st.markdown(f"**{i}. {title}**\n\n- {description}\n")
         else:
            st.info("No rules found.")

         conn.close()


         if st.button("Delete All Rules"):
            delete_all_records("rules")
            st.rerun()

    conn.close()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- Login UI ---
    #st.markdown('<div class="login-box" style="max-width: 400px; margin: auto;">', unsafe_allow_html=True)
   # st.markdown('<img src="https://cdn-icons-png.flaticon.com/512/149/149071.png" class="user-icon">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">User Login</div>', unsafe_allow_html=True)

    if not st.session_state.show_forgot:
        username = st.text_input("Username", placeholder="Username", key="login_user")
        password = st.text_input("Password", placeholder="Password", type="password", key="login_pass")
        if st.button("Log In"):
            if username.strip().upper() == st.session_state.stored_username and hash_password(password) == st.session_state.stored_password:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")
        st.markdown('<a class="forgot-link" href="#">Forgot Password?</a>', unsafe_allow_html=True)
        if st.button("Click here to reset password"):
            st.session_state.show_forgot = True
    else:
        st.markdown("### 🔐 Reset Your Credentials", unsafe_allow_html=True)
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        confirm_pass = st.text_input("Confirm Password", type="password")
        if st.button("Reset Now"):
            if new_pass != confirm_pass:
                st.error("❗ Passwords do not match.")
            elif new_user.strip() == "" or new_pass.strip() == "":
                st.warning("Please fill all fields.")
            else:
                st.session_state.stored_username = new_user.strip().upper()
                st.session_state.stored_password = hash_password(new_pass)
                st.success("✅ Username & password updated!")
                st.session_state.show_forgot = False
