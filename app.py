import os
import math
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
import datetime
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = "employee-payroll-secret-key"


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


def close_db(conn, cursor):
    try:
        if cursor:
            cursor.close()
    except:
        pass

    try:
        if conn:
            conn.close()
    except:
        pass


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

@app.route("/")
@login_required
def home():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM employees")
        total_employees = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM employees WHERE status = 'Active'"
        )
        active_employees = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM employees WHERE status = 'Inactive'"
        )
        inactive_employees = cursor.fetchone()[0]

        return render_template(
            "dashboard.html",
            total_employees=total_employees,
            active_employees=active_employees,
            inactive_employees=inactive_employees
        )

    except mysql.connector.Error as e:
        return f"Database error: {e}"

    finally:
        close_db(conn, cursor)


# ---------------------------------------------------------
# EMPLOYEE LIST + ADD + SEARCH
# ---------------------------------------------------------

@app.route("/employees", methods=["GET", "POST"])
def employees():

    # ADD EMPLOYEE
    if request.method == "POST":

        emp_id = request.form.get("emp_id", "").strip()
        name = request.form.get("name", "").strip()
        pay = request.form.get("pay", "").strip()
        emp_type = request.form.get("type", "").strip()

        # Employee ID validation
        if not emp_id:
            flash("Employee ID cannot be empty!", "error")
            return redirect(url_for("employees"))

        if len(emp_id) > 20:
            flash("Employee ID must be 20 characters or less!", "error")
            return redirect(url_for("employees"))

        if " " in emp_id:
            flash("Employee ID cannot contain spaces!", "error")
            return redirect(url_for("employees"))

        # Name validation
        if not name:
            flash("Employee name cannot be empty!", "error")
            return redirect(url_for("employees"))

        if len(name) > 100:
            flash("Employee name must be 100 characters or less!", "error")
            return redirect(url_for("employees"))

        if not all(ch.isalpha() or ch in " .'-" for ch in name):
            flash("Invalid characters in employee name!", "error")
            return redirect(url_for("employees"))

        # Pay validation
        try:
            pay = float(pay)

            if not math.isfinite(pay) or pay <= 0:
                raise ValueError

        except ValueError:
            flash("Pay must be a valid number greater than 0!", "error")
            return redirect(url_for("employees"))

        # Type validation
        if emp_type not in ["Full-Time", "Part-Time"]:
            flash("Please select a valid employee type!", "error")
            return redirect(url_for("employees"))

        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Duplicate ID check
            cursor.execute(
                "SELECT emp_id FROM employees WHERE emp_id = %s",
                (emp_id,)
            )

            if cursor.fetchone():
                flash("Employee ID already exists!", "error")
                return redirect(url_for("employees"))

            # Insert employee
            cursor.execute(
                """
                INSERT INTO employees
                (emp_id, name, pay, type, status)
                VALUES (%s, %s, %s, %s, 'Active')
                """,
                (emp_id, name, pay, emp_type)
            )

            conn.commit()

            flash("Employee added successfully!", "success")

        except mysql.connector.Error as e:

            if conn:
                conn.rollback()

            flash("Database error while adding employee!", "error")
            print("Database Error:", e)

        finally:
            close_db(conn, cursor)

        return redirect(url_for("employees"))

    # SEARCH
    search = request.args.get("search", "").strip()

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if search:

            cursor.execute(
                """
                SELECT emp_id, name, pay, type, status
                FROM employees
                WHERE emp_id LIKE %s
                   OR name LIKE %s
                ORDER BY emp_id
                """,
                (f"%{search}%", f"%{search}%")
            )

        else:

            cursor.execute(
                """
                SELECT emp_id, name, pay, type, status
                FROM employees
                ORDER BY emp_id
                """
            )

        employee_data = cursor.fetchall()

        return render_template(
            "employees.html",
            employees=employee_data,
            search=search
        )

    except mysql.connector.Error as e:

        return f"Database error: {e}"

    finally:
        close_db(conn, cursor)


# ---------------------------------------------------------
# EDIT EMPLOYEE
# ---------------------------------------------------------

@app.route("/employees/edit/<emp_id>", methods=["GET", "POST"])
def edit_employee(emp_id):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # GET CURRENT EMPLOYEE
        cursor.execute(
            """
            SELECT emp_id, name, pay, type, status
            FROM employees
            WHERE emp_id = %s
            """,
            (emp_id,)
        )

        employee = cursor.fetchone()

        if not employee:
            flash("Employee not found!", "error")
            return redirect(url_for("employees"))

        # UPDATE
        if request.method == "POST":

            name = request.form.get("name", "").strip()
            pay = request.form.get("pay", "").strip()
            emp_type = request.form.get("type", "").strip()

            if not name:
                flash("Employee name cannot be empty!", "error")
                return redirect(
                    url_for("edit_employee", emp_id=emp_id)
                )

            if len(name) > 100:
                flash("Employee name is too long!", "error")
                return redirect(
                    url_for("edit_employee", emp_id=emp_id)
                )

            if not all(ch.isalpha() or ch in " .'-" for ch in name):
                flash("Invalid characters in employee name!", "error")
                return redirect(
                    url_for("edit_employee", emp_id=emp_id)
                )

            try:
                pay = float(pay)

                if not math.isfinite(pay) or pay <= 0:
                    raise ValueError

            except ValueError:
                flash("Pay must be greater than 0!", "error")
                return redirect(
                    url_for("edit_employee", emp_id=emp_id)
                )

            if emp_type not in ["Full-Time", "Part-Time"]:
                flash("Invalid employee type!", "error")
                return redirect(
                    url_for("edit_employee", emp_id=emp_id)
                )

            cursor.execute(
                """
                UPDATE employees
                SET name = %s,
                    pay = %s,
                    type = %s
                WHERE emp_id = %s
                """,
                (name, pay, emp_type, emp_id)
            )

            conn.commit()

            flash("Employee updated successfully!", "success")

            return redirect(url_for("employees"))

        return render_template(
            "edit_employee.html",
            employee=employee
        )

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        return f"Database error: {e}"

    finally:
        close_db(conn, cursor)


# ---------------------------------------------------------
# DEACTIVATE EMPLOYEE
# ---------------------------------------------------------

@app.route("/employees/deactivate/<emp_id>", methods=["POST"])
def deactivate_employee(emp_id):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE employees
            SET status = 'Inactive'
            WHERE emp_id = %s
            """,
            (emp_id,)
        )

        conn.commit()

        flash("Employee deactivated successfully!", "success")

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        flash("Unable to deactivate employee!", "error")
        print("Database Error:", e)

    finally:
        close_db(conn, cursor)

    return redirect(url_for("employees"))


# ---------------------------------------------------------
# ACTIVATE EMPLOYEE
# ---------------------------------------------------------

@app.route("/employees/activate/<emp_id>", methods=["POST"])
def activate_employee(emp_id):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE employees
            SET status = 'Active'
            WHERE emp_id = %s
            """,
            (emp_id,)
        )

        conn.commit()

        flash("Employee activated successfully!", "success")

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        flash("Unable to activate employee!", "error")
        print("Database Error:", e)

    finally:
        close_db(conn, cursor)

    return redirect(url_for("employees"))


# ---------------------------------------------------------
# EMPLOYEE FULL HISTORY
# ---------------------------------------------------------

@app.route("/employees/history/<emp_id>")
def employee_history(emp_id):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        # Employee
        cursor.execute(
            """
            SELECT emp_id, name, pay, type, status
            FROM employees
            WHERE emp_id = %s
            """,
            (emp_id,)
        )

        employee = cursor.fetchone()

        if not employee:
            flash("Employee not found!", "error")
            return redirect(url_for("employees"))

        # Attendance history
        cursor.execute(
            """
            SELECT date, time, status, hours
            FROM attendance
            WHERE emp_id = %s
            ORDER BY date DESC
            """,
            (emp_id,)
        )

        attendance = cursor.fetchall()

        # Payroll history
        cursor.execute(
            """
            SELECT payroll_month,
                   basic_pay,
                   overtime_hours,
                   overtime_pay,
                   total_pay
            FROM payroll
            WHERE emp_id = %s
            ORDER BY payroll_month DESC
            """,
            (emp_id,)
        )

        payroll = cursor.fetchall()

        return render_template(
            "employee_history.html",
            employee=employee,
            attendance=attendance,
            payroll=payroll
        )

    except mysql.connector.Error as e:

        return f"Database error: {e}"

    finally:
        close_db(conn, cursor)


# ---------------------------------------------------------
# ATTENDANCE
# ---------------------------------------------------------

@app.route("/attendance")
def attendance():

    selected_date = request.args.get("date", "").strip()

    if not selected_date:
        selected_date = str(datetime.date.today())

    try:
        selected_date = datetime.datetime.strptime(
            selected_date, "%Y-%m-%d"
        ).date()
    except ValueError:
        flash("Invalid date!", "error")
        return redirect(url_for("attendance"))

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, emp_id, name, date, time, status, hours
            FROM attendance
            WHERE date = %s
            ORDER BY emp_id
            """,
            (selected_date,)
        )

        records = cursor.fetchall()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM attendance
            WHERE date = %s
            AND status = 'Present'
            """,
            (selected_date,)
        )

        present_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM attendance
            WHERE date = %s
            AND status = 'Absent'
            """,
            (selected_date,)
        )

        absent_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM attendance
            WHERE date = %s
            AND status = 'Present'
            AND hours > 8
            """,
            (selected_date,)
        )

        overtime_count = cursor.fetchone()[0]

        return render_template(
            "attendance.html",
            records=records,
            selected_date=selected_date,
            present_count=present_count,
            absent_count=absent_count,
            overtime_count=overtime_count
        )

    except mysql.connector.Error as e:

        return f"Database error: {e}"

    finally:
        close_db(conn, cursor)


@app.route("/attendance/record", methods=["POST"])
def record_attendance():

    emp_id = request.form.get("emp_id", "").strip()
    status = request.form.get("status", "").strip()
    hours_input = request.form.get("hours", "").strip()

    if not emp_id:
        flash("Employee ID cannot be empty!", "error")
        return redirect(url_for("attendance"))

    if status not in ["Present", "Absent"]:
        flash("Invalid attendance status!", "error")
        return redirect(url_for("attendance"))

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        # Check employee
        cursor.execute(
            """
            SELECT emp_id, name, status
            FROM employees
            WHERE emp_id = %s
            """,
            (emp_id,)
        )

        employee = cursor.fetchone()

        if not employee:
            flash("Employee not found!", "error")
            return redirect(url_for("attendance"))

        # Inactive employee
        if employee[2] == "Inactive":
            flash(
                "Inactive employees cannot have attendance recorded!",
                "error"
            )
            return redirect(url_for("attendance"))

        today = datetime.date.today()
        current_time = datetime.datetime.now().time()

        # Duplicate check
        cursor.execute(
            """
            SELECT id
            FROM attendance
            WHERE emp_id = %s
            AND date = %s
            """,
            (emp_id, today)
        )

        if cursor.fetchone():
            flash(
                "Attendance already recorded for this employee today!",
                "error"
            )
            return redirect(url_for("attendance"))

        # Present
        if status == "Present":

            try:
                hours = float(hours_input)

                if hours < 0 or hours > 24:
                    raise ValueError

            except ValueError:
                flash(
                    "Working hours must be between 0 and 24!",
                    "error"
                )
                return redirect(url_for("attendance"))

        # Absent
        else:
            hours = 0

        cursor.execute(
            """
            INSERT INTO attendance
            (emp_id, name, date, time, status, hours)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                employee[0],
                employee[1],
                today,
                current_time,
                status,
                hours
            )
        )

        conn.commit()

        flash(
            f"Attendance recorded for {employee[1]}!",
            "success"
        )

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("Database Error:", e)
        flash("Database error while recording attendance!", "error")

    finally:
        close_db(conn, cursor)

    return redirect(url_for("attendance"))


@app.route("/attendance/update/<int:record_id>", methods=["GET", "POST"])
def update_attendance(record_id):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, emp_id, name, date, time, status, hours
            FROM attendance
            WHERE id = %s
            """,
            (record_id,)
        )

        record = cursor.fetchone()

        if not record:
            flash("Attendance record not found!", "error")
            return redirect(url_for("attendance"))

        if request.method == "POST":

            status = request.form.get("status", "").strip()
            hours_input = request.form.get("hours", "").strip()

            if status not in ["Present", "Absent"]:
                flash("Invalid status!", "error")
                return redirect(
                    url_for("update_attendance", record_id=record_id)
                )

            if status == "Present":

                try:
                    hours = float(hours_input)

                    if hours < 0 or hours > 24:
                        raise ValueError

                except ValueError:
                    flash(
                        "Working hours must be between 0 and 24!",
                        "error"
                    )
                    return redirect(
                        url_for(
                            "update_attendance",
                            record_id=record_id
                        )
                    )

            else:
                hours = 0

            cursor.execute(
                """
                UPDATE attendance
                SET status = %s,
                    hours = %s
                WHERE id = %s
                """,
                (status, hours, record_id)
            )

            conn.commit()

            flash(
                "Attendance updated successfully!",
                "success"
            )

            return redirect(url_for("attendance"))

        return render_template(
            "edit_attendance.html",
            record=record
        )

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        return f"Database error: {e}"

    finally:
        close_db(conn, cursor)
        
# ---------------------------------------------------------
# PAYROLL
# ---------------------------------------------------------

@app.route("/payroll")
def payroll():

    month = request.args.get("month", "").strip()

    if not month:
        month = datetime.date.today().strftime("%Y-%m")

    try:
        year, month_number = map(int, month.split("-"))
        start_date = datetime.date(year, month_number, 1)

        if month_number == 12:
            end_date = datetime.date(year + 1, 1, 1)
        else:
            end_date = datetime.date(year, month_number + 1, 1)

    except ValueError:
        flash("Invalid month. Use YYYY-MM.", "error")
        return redirect(url_for("payroll"))

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT DISTINCT e.emp_id, e.name, e.pay, e.type
            FROM employees e
            JOIN attendance a
                ON e.emp_id = a.emp_id
            WHERE a.date >= %s
              AND a.date < %s
            ORDER BY e.emp_id
            """,
            (start_date, end_date)
        )

        employees_data = cursor.fetchall()

        payroll_data = []
        total_payroll = 0
        
        # Combined payroll of all saved payroll records till date
        cursor.execute(
            """
            SELECT COALESCE(SUM(total_pay), 0)
            FROM payroll
            """
        )
        
        combined_payroll = cursor.fetchone()[0]

        for employee in employees_data:

            emp_id = employee[0]
            name = employee[1]
            pay = float(employee[2])
            emp_type = employee[3]

            cursor.execute(
                """
                SELECT status, hours
                FROM attendance
                WHERE emp_id = %s
                  AND date >= %s
                  AND date < %s
                """,
                (emp_id, start_date, end_date)
            )
            

            records = cursor.fetchall()

            total_hours = 0
            overtime_hours = 0
            present_days = 0
            absent_days = 0

            for record in records:

                status = record[0]
                hours = float(record[1])

                if status == "Present":

                    present_days += 1
                    total_hours += hours

                    if hours > 8:
                        overtime_hours += hours - 8

                elif status == "Absent":

                    absent_days += 1

            if emp_type == "Part-Time":
                basic_pay = total_hours * pay
            else:
                basic_pay = pay

            overtime_pay = overtime_hours * 100
            total_pay = basic_pay + overtime_pay

            total_payroll += total_pay

            payroll_data.append({
                "emp_id": emp_id,
                "name": name,
                "type": emp_type,
                "present_days": present_days,
                "absent_days": absent_days,
                "total_hours": total_hours,
                "overtime_hours": overtime_hours,
                "basic_pay": basic_pay,
                "overtime_pay": overtime_pay,
                "total_pay": total_pay
            })

        return render_template(
            "payroll.html",
            month=month,
            payroll_data=payroll_data,
            total_payroll=total_payroll,
            combined_payroll=combined_payroll
        )

    except mysql.connector.Error as e:

        return f"Database error: {e}"

    finally:
        close_db(conn, cursor)


@app.route("/payroll/save/<emp_id>/<month>", methods=["POST"])
def save_payroll(emp_id, month):

    try:
        year, month_number = map(int, month.split("-"))
        payroll_month = datetime.date(year, month_number, 1)

    except ValueError:
        flash("Invalid payroll month!", "error")
        return redirect(url_for("payroll"))

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT pay, type
            FROM employees
            WHERE emp_id = %s
            """,
            (emp_id,)
        )

        employee = cursor.fetchone()

        if not employee:
            flash("Employee not found!", "error")
            return redirect(url_for("payroll", month=month))

        pay = float(employee[0])
        emp_type = employee[1]

        start_date = payroll_month

        if month_number == 12:
            end_date = datetime.date(year + 1, 1, 1)
        else:
            end_date = datetime.date(year, month_number + 1, 1)

        cursor.execute(
            """
            SELECT status, hours
            FROM attendance
            WHERE emp_id = %s
              AND date >= %s
              AND date < %s
            """,
            (emp_id, start_date, end_date)
        )

        records = cursor.fetchall()

        total_hours = 0
        overtime_hours = 0

        for record in records:

            status = record[0]
            hours = float(record[1])

            if status == "Present":

                total_hours += hours

                if hours > 8:
                    overtime_hours += hours - 8

        if emp_type == "Part-Time":
            basic_pay = total_hours * pay
        else:
            basic_pay = pay

        overtime_pay = overtime_hours * 100
        total_pay = basic_pay + overtime_pay

        cursor.execute(
            """
            SELECT id
            FROM payroll
            WHERE emp_id = %s
              AND payroll_month = %s
            """,
            (emp_id, payroll_month)
        )

        existing = cursor.fetchone()

        if existing:

            cursor.execute(
                """
                UPDATE payroll
                SET basic_pay = %s,
                    overtime_hours = %s,
                    overtime_pay = %s,
                    total_pay = %s
                WHERE emp_id = %s
                  AND payroll_month = %s
                """,
                (
                    basic_pay,
                    overtime_hours,
                    overtime_pay,
                    total_pay,
                    emp_id,
                    payroll_month
                )
            )

        else:

            cursor.execute(
                """
                INSERT INTO payroll
                (
                    emp_id,
                    basic_pay,
                    overtime_hours,
                    overtime_pay,
                    total_pay,
                    payroll_month
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    emp_id,
                    basic_pay,
                    overtime_hours,
                    overtime_pay,
                    total_pay,
                    payroll_month
                )
            )

        conn.commit()

        flash("Payroll saved successfully!", "success")

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        flash("Database error while saving payroll!", "error")
        print("Database Error:", e)

    finally:
        close_db(conn, cursor)

    return redirect(url_for("payroll", month=month))


@app.route("/payroll/records")
@login_required
def payroll_records():

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                p.emp_id,
                e.name,
                e.type,
                p.payroll_month,
                p.basic_pay,
                p.overtime_hours,
                p.overtime_pay,
                p.total_pay
            FROM payroll p
            JOIN employees e
                ON p.emp_id = e.emp_id
            ORDER BY p.payroll_month DESC, p.emp_id
            """
        )

        records = cursor.fetchall()

        # Calculate total payroll
        cursor.execute(
            """
            SELECT COALESCE(SUM(total_pay), 0)
            FROM payroll
            """
        )

        total_payroll = cursor.fetchone()[0]

        return render_template(
            "payroll_records.html",
            records=records,
            total_payroll=total_payroll
        )

    except mysql.connector.Error as e:
        return f"Database error: {e}"

    finally:
        close_db(conn, cursor)

@app.route("/payslip/<emp_id>/<month>")
def payslip_page(emp_id, month):

    try:

        year, month_number = map(int, month.split("-"))

        start_date = datetime.date(year, month_number, 1)

        if month_number == 12:
            end_date = datetime.date(year + 1, 1, 1)
        else:
            end_date = datetime.date(year, month_number + 1, 1)

    except ValueError:

        flash("Invalid payroll month!", "error")
        return redirect(url_for("payroll"))

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT emp_id, name, pay, type
            FROM employees
            WHERE emp_id = %s
            """,
            (emp_id,)
        )

        employee = cursor.fetchone()

        if not employee:

            flash("Employee not found!", "error")
            return redirect(url_for("payroll"))

        cursor.execute(
            """
            SELECT date, status, hours
            FROM attendance
            WHERE emp_id = %s
              AND date >= %s
              AND date < %s
            ORDER BY date
            """,
            (emp_id, start_date, end_date)
        )

        attendance = cursor.fetchall()

        total_hours = 0
        overtime_hours = 0
        present_days = 0
        absent_days = 0

        for record in attendance:

            status = record[1]
            hours = float(record[2])

            if status == "Present":

                present_days += 1
                total_hours += hours

                if hours > 8:
                    overtime_hours += hours - 8

            elif status == "Absent":

                absent_days += 1

        pay = float(employee[2])
        emp_type = employee[3]

        if emp_type == "Part-Time":
            basic_pay = total_hours * pay
        else:
            basic_pay = pay

        overtime_pay = overtime_hours * 100
        total_pay = basic_pay + overtime_pay

        return render_template(
            "payslip.html",
            employee=employee,
            month=month,
            present_days=present_days,
            absent_days=absent_days,
            total_hours=total_hours,
            overtime_hours=overtime_hours,
            basic_pay=basic_pay,
            overtime_pay=overtime_pay,
            total_pay=total_pay
        )

    except mysql.connector.Error as e:

        return f"Database error: {e}"

    finally:
        close_db(conn, cursor)

# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id, username, password, role
                FROM users
                WHERE username = %s
                """,
                (username,)
            )

            user = cursor.fetchone()

            if user and user[2] == password:

                session["user_id"] = user[0]
                session["username"] = user[1]
                session["role"] = user[3]

                return redirect(url_for("home"))

            flash("Invalid username or password!", "error")
            return redirect(url_for("login"))

        except mysql.connector.Error as e:

            flash("Database error during login!", "error")
            print("Database Error:", e)

        finally:
            close_db(conn, cursor)

    return render_template("login.html")


# ---------------------------------------------------------
# REPORTS & EMPLOYEE PERFORMANCE
# ---------------------------------------------------------

@app.route("/reports")
@login_required
def reports():

    month = request.args.get(
        "month",
        datetime.date.today().strftime("%Y-%m")
    ).strip()

    try:
        year, month_number = map(int, month.split("-"))

        start_date = datetime.date(
            year,
            month_number,
            1
        )

        if month_number == 12:
            end_date = datetime.date(
                year + 1,
                1,
                1
            )
        else:
            end_date = datetime.date(
                year,
                month_number + 1,
                1
            )

    except ValueError:
        flash("Invalid month. Use YYYY-MM.", "error")
        return redirect(url_for("reports"))

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # SUMMARY COUNTS
        # -------------------------------------------------

        cursor.execute(
            "SELECT COUNT(*) AS total_employees FROM employees"
        )
        total_employees = cursor.fetchone()["total_employees"]

        cursor.execute(
            """
            SELECT COUNT(*) AS active_employees
            FROM employees
            WHERE status = 'Active'
            """
        )
        active_employees = cursor.fetchone()["active_employees"]

        cursor.execute(
            """
            SELECT COUNT(*) AS attendance_records
            FROM attendance
            WHERE date >= %s
              AND date < %s
            """,
            (start_date, end_date)
        )
        attendance_records = cursor.fetchone()["attendance_records"]

        cursor.execute(
            """
            SELECT COUNT(*) AS payroll_records
            FROM payroll
            WHERE payroll_month = %s
            """,
            (start_date,)
        )
        payroll_records = cursor.fetchone()["payroll_records"]

        cursor.execute(
            """
            SELECT COALESCE(SUM(total_pay), 0) AS total_payroll
            FROM payroll
            WHERE payroll_month = %s
            """,
            (start_date,)
        )
        total_payroll = cursor.fetchone()["total_payroll"]

        # -------------------------------------------------
        # EMPLOYEE PERFORMANCE
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                e.emp_id,
                e.name,
                e.type,
                e.status,

                COALESCE(a.present_days, 0) AS present_days,
                COALESCE(a.absent_days, 0) AS absent_days,
                COALESCE(a.total_hours, 0) AS total_hours,
                COALESCE(a.overtime_hours, 0) AS overtime_hours,

                COALESCE(p.total_pay, 0) AS total_pay

            FROM employees e

            LEFT JOIN
            (
                SELECT
                    emp_id,

                    SUM(
                        CASE
                            WHEN status = 'Present'
                            THEN 1
                            ELSE 0
                        END
                    ) AS present_days,

                    SUM(
                        CASE
                            WHEN status = 'Absent'
                            THEN 1
                            ELSE 0
                        END
                    ) AS absent_days,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN status = 'Present'
                                THEN hours
                                ELSE 0
                            END
                        ),
                        0
                    ) AS total_hours,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN status = 'Present'
                                     AND hours > 8
                                THEN hours - 8
                                ELSE 0
                            END
                        ),
                        0
                    ) AS overtime_hours

                FROM attendance

                WHERE date >= %s
                  AND date < %s

                GROUP BY emp_id

            ) a

            ON e.emp_id = a.emp_id

            LEFT JOIN payroll p

            ON e.emp_id = p.emp_id
            AND p.payroll_month = %s

            ORDER BY e.emp_id
            """,
            (start_date, end_date, start_date)
        )

        performance_data = cursor.fetchall()

        # -------------------------------------------------
        # PERFORMANCE PERCENTAGE BASED ON WORKING HOURS
        # -------------------------------------------------

        EXPECTED_HOURS_PER_MONTH = 200

        for employee in performance_data:

            total_hours = float(employee["total_hours"])

            if EXPECTED_HOURS_PER_MONTH > 0:
                performance_percentage = (
                    total_hours / EXPECTED_HOURS_PER_MONTH
                ) * 100
            else:
                performance_percentage = 0

            # Keep performance between 0% and 100%
            performance_percentage = min(performance_percentage, 100)

            employee["attendance_percentage"] = round(
                performance_percentage,
                2
            )

        return render_template(
            "reports.html",
            month=month,
            total_employees=total_employees,
            active_employees=active_employees,
            attendance_records=attendance_records,
            payroll_records=payroll_records,
            total_payroll=total_payroll,
            performance_data=performance_data
        )

    except mysql.connector.Error as e:

        print("Database Error:", e)

        return f"Database error: {e}"

    finally:
        close_db(conn, cursor)

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)