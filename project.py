import datetime
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
    except (mysql.connector.Error, ValueError, TypeError) as e:
        print("Database connection error:", e)
        raise

def close_db(conn, cursor):
    try:
        if cursor:
            cursor.close()
    except mysql.connector.Error:
        pass
    try:
        if conn:
            conn.close()
    except mysql.connector.Error:
        pass

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function

#EMPLOYEE------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Employee:
    def __init__(self):
        try:
            while True:
                c = int(input("\n---EMPLOYEE MANAGEMENT--- \n1. Add Employee \n2. Update Employee \n3. Search Employee \n4. Remove Employee \n5. List All Employees \n6. Inactive Employees \n0. Back to Main Menu\n---Enter: "))
                if c not in [0, 1, 2, 3, 4, 5, 6]:
                    print("\nInvalid choice! Please select 0, 1, 2 , 3 ,4 ,5 or 6.")
                    continue
                match c:
                    case 1:
                        print("--ADDING EMPLOYEES--")
                        e = input("\n1. Full-Time: \n2. Part-Time: \nSelect: ")
                        if e == '1':
                            fulltimeEmp()
                        elif e == '2':
                            parttimeEmp()
                        else:
                            print("!!Invalid Syntax!!")
                    case 2:
                        print("--UPDATING EMPLOYEES--")
                        updateemployee()
                    case 3:
                        print("--SEARCHING EMPLOYEE--")
                        searchemployee()
                    case 4:
                        print("--REMOVING EMPLOYEE--")
                        removemployee()
                    case 5:
                        print("--ALL EMPLOYEES--")
                        allemployee()
                    case 6:
                        print("--INACTIVE EMPLOYEES--")
                        inactive_emp()
                    case 0:
                        break
        except ValueError: print("\n!Invalid Input i.e Error, Try Again!\n")

def employee_exists(emp_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT emp_id FROM employees WHERE emp_id = %s",
        (emp_id,)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None
    
def get_employee_id():
    while True:
        emp_id = input("Employee ID: ").strip()
        if not emp_id:
            print("Employee ID cannot be empty!")
            continue
        if len(emp_id) > 20:
            print("Employee ID must be 20 characters or less!")
            continue
        if " " in emp_id:
            print("Employee ID cannot contain spaces!")
            continue
        return emp_id


def get_employee_name():
    while True:
        name = input("Emp Name: ").strip()
        if not name:
            print("Employee Name cannot be empty!")
            continue
        if len(name) > 100:
            print("Employee Name must be 100 characters or less!")
            continue
        if not all(
            ch.isalpha() or ch in " .'-"
            for ch in name
        ):
            print("Name can contain only letters, spaces, '.', apostrophe and '-'!")
            continue
        return name


def get_positive_pay(prompt):
    while True:
        try:
            pay = float(input(prompt))

            if pay <= 0:
                print("Pay must be greater than 0!")
                continue

            return pay

        except ValueError:
            print("Invalid pay! Enter a number.")
    
class fulltimeEmp:
    def __init__(self):
        print("-Full-Time Employee-")
        emp_id = get_employee_id()
        name = get_employee_name()
        pay = get_positive_pay("Monthly Salary: ")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT emp_id FROM employees WHERE emp_id = %s",
            (emp_id,)
        )
        if cursor.fetchone():
            print("!!Employee ID already exists!!")
        else:
            cursor.execute(
                """INSERT INTO employees
                (emp_id, name, pay, type)
                VALUES (%s, %s, %s, %s)""",
                (emp_id, name, pay, "Full-Time")
            )
            conn.commit()
            print("Employee Added Successfully!")
        cursor.close()
        conn.close()

class parttimeEmp:
    def __init__(self):
        print("-Part-Time Employee-")
        emp_id = get_employee_id()
        name = get_employee_name()
        pay = get_positive_pay("Hourly Pay: ")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT emp_id FROM employees WHERE emp_id = %s",
            (emp_id,)
        )
        if cursor.fetchone():
            print("!!Employee ID already exists!!")
        else:
            cursor.execute(
                """INSERT INTO employees
                (emp_id, name, pay, type)
                VALUES (%s, %s, %s, %s)""",
                (emp_id, name, pay, "Part-Time")
            )
            conn.commit()
            print("Employee Added Successfully!")
        cursor.close()
        conn.close()

class updateemployee:
    def __init__(self):
        emp_id = get_employee_id()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT emp_id, name, pay, type
            FROM employees
            WHERE emp_id = %s""",
            (emp_id,)
        )
        employee = cursor.fetchone()
        if employee:
            print("\nEmployee Found!")
            print("Current Name :", employee[1])
            print("Current Pay  :", employee[2])
            new_name = get_employee_name()
            new_pay = get_positive_pay("Enter Updated Pay: ")
            cursor.execute(
                """UPDATE employees
                SET name = %s, pay = %s
                WHERE emp_id = %s""",
                (new_name, new_pay, emp_id)
            )
            conn.commit()
            print("Employee Updated Successfully!")
        else:
            print("Employee not found!")
        cursor.close()
        conn.close()
        
class searchemployee:
    def __init__(self):
        emp_id = input("Employee ID: ")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT emp_id, name, pay, type FROM employees WHERE emp_id = %s",
            (emp_id,)
        )
        employee = cursor.fetchone()
        if employee:
            print("\nEmployee Found!")
            print("Employee ID :", employee[0])
            print("Name        :", employee[1])
            print("Payment     :", employee[2])
            print("Type        :", employee[3])
        else:
            print("Employee not found.")
        cursor.close()
        conn.close()
        
class allemployee:
    def __init__(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT emp_id, name, pay, type FROM employees WHERE status = 'Active'"
        )
        employees_data = cursor.fetchall()
        if not employees_data:
            print("No employees found!")
        else:
            print("\n--- ALL EMPLOYEES ---")
            for employee in employees_data:
                print(
                    "ID:", employee[0],
                    "| Name:", employee[1],
                    "| Pay:", employee[2],
                    "| Type:", employee[3]
                )
        cursor.close()
        conn.close()

class removemployee:
    def __init__(self):
        emp_id = input("Employee ID: ").strip()
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT emp_id, name, status FROM employees WHERE emp_id = %s",
                (emp_id,)
            )
            employee = cursor.fetchone()
            if not employee:
                print("Employee not found.")
                return
            if employee[2] == "Inactive":
                print("Employee is already inactive.")
                return
            confirm = input(
                "Are you sure you want to remove this employee? (Y/N): "
            ).strip().upper()
            if confirm != "Y":
                print("Operation cancelled.")
                return
            cursor.execute(
                """UPDATE employees
                SET status = 'Inactive'
                WHERE emp_id = %s""",
                (emp_id,)
            )
            conn.commit()
            print("Employee marked as Inactive successfully!")
            print("Attendance and payroll history has been preserved.")
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            print("Database Error:", e)
        finally:
            close_db(conn, cursor)

def inactive_emp():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Show all inactive employees
        cursor.execute(
            """SELECT emp_id, name, pay, type
            FROM employees
            WHERE status = 'Inactive'
            ORDER BY emp_id"""
        )
        records = cursor.fetchall()
        if not records:
            print("No Inactive Employees Found!")
            return
        print("\n================================================")
        print("              INACTIVE EMPLOYEES")
        print("================================================")
        for record in records:
            print(
                "ID:", record[0],
                "| Name:", record[1],
                "| Pay:", record[2],
                "| Type:", record[3]
            )
        print("================================================")
        emp_id = input(
            "\nEnter Employee ID to view full history"
            "\nEnter 0 to go back"
            "\nEnter: "
        ).strip()
        if emp_id == "0":
            return
        # Get selected inactive employee
        cursor.execute(
            """SELECT emp_id, name, pay, type, status
            FROM employees
            WHERE emp_id = %s AND status = 'Inactive'""",
            (emp_id,)
        )
        employee = cursor.fetchone()
        if not employee:
            print("\nInactive Employee not found!")
            return
        print("\n================================================")
        print("             EMPLOYEE FULL DETAILS")
        print("================================================")
        print("Employee ID :", employee[0])
        print("Name        :", employee[1])
        print("Pay         :", employee[2])
        print("Type        :", employee[3])
        print("Status      :", employee[4])
        # Attendance history
        cursor.execute(
            """SELECT date, time, status, hours
            FROM attendance
            WHERE emp_id = %s
            ORDER BY date DESC""",
            (emp_id,)
        )
        attendance_records = cursor.fetchall()
        print("\n------------------------------------------------")
        print("              ATTENDANCE HISTORY")
        print("------------------------------------------------")
        if not attendance_records:
            print("No Attendance History Found!")
        else:
            for record in attendance_records:
                print(
                    "Date:", record[0],
                    "| Time:", record[1],
                    "| Status:", record[2],
                    "| Hours:", record[3]
                )
        # Payroll history
        cursor.execute(
            """SELECT payroll_month,
                      basic_pay,
                      overtime_hours,
                      overtime_pay,
                      total_pay
            FROM payroll
            WHERE emp_id = %s
            ORDER BY payroll_month DESC""",
            (emp_id,)
        )
        payroll_records = cursor.fetchall()
        print("\n------------------------------------------------")
        print("                PAYROLL HISTORY")
        print("------------------------------------------------")
        if not payroll_records:
            print("No Payroll History Found!")
        else:
            for record in payroll_records:
                print(
                    "Month:", record[0].strftime("%Y-%m"),
                    "| Basic Pay:", f"₹{float(record[1]):.2f}",
                    "| OT Hours:", f"{float(record[2]):.2f}",
                    "| OT Pay:", f"₹{float(record[3]):.2f}",
                    "| Total:", f"₹{float(record[4]):.2f}"
                )
        print("\n================================================")
        print("1. Activate Employee")
        print("0. Back")
        print("================================================")
        choice = input("Enter: ").strip()
        if choice == "1":
            confirm = input(
                f"Are you sure you want to activate {emp_id}? (Y/N): "
            ).strip().upper()
            if confirm != "Y":
                print("Operation cancelled.")
                return
            cursor.execute(
                """UPDATE employees
                SET status = 'Active'
                WHERE emp_id = %s""",
                (emp_id,)
            )
            conn.commit()
            print("\nEmployee activated successfully!")
        elif choice == "0":
            return
        else:
            print("Invalid choice!")
    except mysql.connector.Error as e:
        if conn:
            conn.rollback()
        print("Database Error:", e)
    finally:
        close_db(conn, cursor)

#ATTENDANCE---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Attendance:
    def __init__(self):
        try:
            while True:
                b = int(input("\n---ATTENDANCE MANAGEMENT--- \n1. Record Attendance \n2. Update Attendance \n3. View Employee Attendance \n4. List Present Employees \n5. List Absent Employees \n6. List Overtime Employees \n0. Back to Main Menu: \n---Enter: "))
                if b not in [0, 1, 2, 3, 4, 5, 6]:
                    print("\nInvalid choice! Please select 0, 1, 2 ,3 ,4 ,5 or 6.")
                    continue
                match b:
                    case 1:
                        print("--RECORDING TODAYS ATTENDANCE--")
                        record_atnd()
                    case 2:
                        print("--UPDATE ATTENDANCE--")
                        update_atnd()
                    case 3:
                        print("\n--VIEW EMPLOYEE ATTENDANCE--")
                        view_atnd()
                    case 4:
                        print("\n--PRESENT EMPLOYEES--")
                        present_emp()
                    case 5:
                        print("\n--ABSENT EMPLOYEES--")
                        absent_emp()
                    case 6:
                        print("\n-- OVERTIME EMPLOYEES --")
                        overtime_emp()
                    case 0:
                        break
        except ValueError: print("\n!Invalid Input i.e Error, Try Again!\n")

def update_atnd():
    conn = None
    cursor = None
    try:
        emp_id = input("Employee ID: ").strip()
        date = input("Date (YYYY-MM-DD): ").strip()
        try:
            date = datetime.datetime.strptime(date,"%Y-%m-%d").date()
        except ValueError:
            print("Invalid date! Use YYYY-MM-DD.")
            return
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id FROM attendance
            WHERE emp_id=%s AND date=%s""",
            (emp_id,date)
        )
        record = cursor.fetchone()
        if not record:
            print("Attendance not found!")
            return
        status = input("P/A: ").strip().upper()
        if status == "P":
            hours = float(input("Hours: "))
            if hours < 0 or hours > 24:
                print("Hours must be between 0 and 24!")
                return
            cursor.execute(
                """UPDATE attendance
                SET status='Present',hours=%s
                WHERE id=%s""",
                (hours,record[0])
            )
        elif status == "A":
            cursor.execute(
                """UPDATE attendance
                SET status='Absent',hours=0
                WHERE id=%s""",
                (record[0],)
            )
        else:
            print("Invalid Status!")
            return
        conn.commit()
        print("Attendance Updated!")
    except ValueError:
        print("!!Invalid hours! Enter a number!!")
    except mysql.connector.Error as e:
        if conn:
            conn.rollback()
        print("Database error:",e)
    finally:
        close_db(conn,cursor)

def view_atnd():
    emp_id = input("Employee ID: ").strip()
    print("\n1. View by Specific Date")
    print("2. View by Month")
    print("3. View All Attendance")
    choice = input("Select: ").strip()
    conn = get_connection()
    cursor = conn.cursor()
    if choice == "1":
        date = input("Enter Date (YYYY-MM-DD): ").strip()
        try:
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date! Use YYYY-MM-DD.")
            cursor.close()
            conn.close()
            return
        cursor.execute(
            """SELECT emp_id, name, date, time, status, hours
            FROM attendance
            WHERE emp_id = %s AND date = %s
            ORDER BY date""",
            (emp_id, date)
        )
    elif choice == "2":
        month = input("Enter Month (YYYY-MM): ").strip()
        try:
            year, month_number = map(int, month.split("-"))
            start_date = datetime.date(year, month_number, 1)
            if month_number == 12:
                end_date = datetime.date(year + 1, 1, 1)
            else:
                end_date = datetime.date(
                    year,
                    month_number + 1,
                    1
                )
        except ValueError:
            print("Invalid month! Use YYYY-MM.")
            cursor.close()
            conn.close()
            return
        cursor.execute(
            """SELECT emp_id, name, date, time, status, hours
            FROM attendance
            WHERE emp_id = %s
            AND date >= %s
            AND date < %s
            ORDER BY date""",
            (emp_id, start_date, end_date)
        )
    elif choice == "3":
        cursor.execute(
            """SELECT emp_id, name, date, time, status, hours
            FROM attendance
            WHERE emp_id = %s
            ORDER BY date""",
            (emp_id,)
        )
    else:
        print("Invalid choice!")
        cursor.close()
        conn.close()
        return
    records = cursor.fetchall()
    if not records:
        print("No Attendance Record Found!")
    else:
        print("\n------------------------------------------------------------")
        print("                 ATTENDANCE RECORDS")
        print("------------------------------------------------------------")
        for record in records:
            print(
                "ID:", record[0],
                "| Name:", record[1],
                "| Date:", record[2],
                "| Time:", record[3],
                "| Status:", record[4],
                "| Hours:", record[5]
            )
        print("------------------------------------------------------------")
    cursor.close()
    conn.close()

def overtime_emp():
    choice = input(
        "\n1. View Today's Overtime Employees"
        "\n2. View All Overtime Employees"
        "\nEnter: "
    ).strip()
    conn = get_connection()
    cursor = conn.cursor()
    if choice == "1":
        today = datetime.date.today()
        cursor.execute(
            """SELECT emp_id, name, date, hours
            FROM attendance
            WHERE status = 'Present'
            AND hours > 8
            AND date = %s
            ORDER BY emp_id""",
            (today,)
        )
        records = cursor.fetchall()
        print("\n==========================================")
        print("       OVERTIME EMPLOYEES")
        print("Date :", today)
        print("==========================================")
        if not records:
            print("No Overtime Employees Found for today!")
        else:
            for record in records:
                overtime = record[3] - 8
                print(
                    "ID:", record[0],
                    "| Name:", record[1],
                    "| Hours:", record[3],
                    "| Overtime:", overtime
                )
    elif choice == "2":
        cursor.execute(
            """SELECT emp_id, name, date, hours
            FROM attendance
            WHERE status = 'Present'
            AND hours > 8
            ORDER BY date DESC, emp_id"""
        )
        records = cursor.fetchall()
        print("\n==========================================")
        print("       ALL OVERTIME EMPLOYEES")
        print("==========================================")
        if not records:
            print("No Overtime Employees Found!")
        else:
            current_date = None
            for record in records:
                record_date = record[2]
                if record_date != current_date:
                    current_date = record_date
                    print("\n------------------------------------------")
                    print("Date:", current_date)
                    print("------------------------------------------")
                overtime = record[3] - 8
                print(
                    "ID:", record[0],
                    "| Name:", record[1],
                    "| Hours:", record[3],
                    "| Overtime:", overtime
                )
    else:
        print("Invalid choice!")
    cursor.close()
    conn.close()

def absent_emp():
    choice = input(
        "\n1. View Today's Absent Employees"
        "\n2. View All Absent Employees"
        "\nEnter: "
    ).strip()
    conn = get_connection()
    cursor = conn.cursor()
    if choice == "1":
        today = datetime.date.today()
        cursor.execute(
            """SELECT emp_id, name, date
            FROM attendance
            WHERE status = 'Absent'
            AND date = %s
            ORDER BY emp_id""",
            (today,)
        )
        records = cursor.fetchall()
        print("\n==========================================")
        print("        ABSENT EMPLOYEES")
        print("Date :", today)
        print("==========================================")
        if not records:
            print("No Absent Employees Found for today!")
        else:
            for record in records:
                print(
                    "ID:", record[0],
                    "| Name:", record[1]
                )
    elif choice == "2":
        cursor.execute(
            """SELECT emp_id, name, date
            FROM attendance
            WHERE status = 'Absent'
            ORDER BY date DESC, emp_id"""
        )
        records = cursor.fetchall()
        print("\n==========================================")
        print("        ALL ABSENT EMPLOYEES")
        print("==========================================")
        if not records:
            print("No Absent Employees Found!")
        else:
            current_date = None
            for record in records:
                record_date = record[2]
                if record_date != current_date:
                    current_date = record_date
                    print("\n------------------------------------------")
                    print("Date:", current_date)
                    print("------------------------------------------")
                print(
                    "ID:", record[0],
                    "| Name:", record[1]
                )
    else:
        print("Invalid choice!")
    cursor.close()
    conn.close()

def present_emp():
    choice = input(
        "\n1. View Today's Present Employees"
        "\n2. View All Present Employees"
        "\nEnter: "
    ).strip()
    conn = get_connection()
    cursor = conn.cursor()
    if choice == "1":
        today = datetime.date.today()
        cursor.execute(
            """SELECT emp_id, name, date, hours
            FROM attendance
            WHERE status = 'Present'
            AND date = %s
            ORDER BY emp_id""",
            (today,)
        )
        records = cursor.fetchall()
        print("\n==========================================")
        print("       PRESENT EMPLOYEES")
        print("Date :", today)
        print("==========================================")
        if not records:
            print("No Present Employees Found for today!")
        else:
            for record in records:
                print(
                    "ID:", record[0],
                    "| Name:", record[1],
                    "| Hours:", record[3]
                )
    elif choice == "2":
        cursor.execute(
            """SELECT emp_id, name, date, hours
            FROM attendance
            WHERE status = 'Present'
            ORDER BY date DESC, emp_id"""
        )
        records = cursor.fetchall()
        print("\n==========================================")
        print("       ALL PRESENT EMPLOYEES")
        print("==========================================")
        if not records:
            print("No Present Employees Found!")
        else:
            current_date = None
            for record in records:
                record_date = record[2]
                if record_date != current_date:
                    current_date = record_date
                    print("\n------------------------------------------")
                    print("Date:", current_date)
                    print("------------------------------------------")
                print(
                    "ID:", record[0],
                    "| Name:", record[1],
                    "| Hours:", record[3]
                )
    else:
        print("Invalid choice!")
    cursor.close()
    conn.close()

class record_atnd:
    def __init__(self):
        emp_id = input("Employee ID: ").strip()
        conn = get_connection()
        cursor = conn.cursor()
        # Check employee and status
        cursor.execute(
            """SELECT emp_id, name, status
            FROM employees
            WHERE emp_id = %s""",
            (emp_id,)
        )
        employee = cursor.fetchone()
        if not employee:
            print("No Employee Found with this Employee ID!")
            cursor.close()
            conn.close()
            return
        # Prevent inactive employees from getting attendance
        if employee[2] == "Inactive":
            print("Employee is Inactive. Attendance cannot be recorded!")
            cursor.close()
            conn.close()
            return
        # Automatically get current date and time
        today = datetime.date.today()
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print("\n==========================================")
        print("           RECORD ATTENDANCE")
        print("==========================================")
        print("Attendance Date :", today)
        print("Current Time    :", now)
        print("==========================================")
        # Check if attendance is already recorded today
        cursor.execute(
            """SELECT id
            FROM attendance
            WHERE emp_id = %s AND date = %s""",
            (emp_id, today)
        )
        if cursor.fetchone():
            print("Attendance already recorded for today!")
            cursor.close()
            conn.close()
            return
        atnd = input(
            "Enter P for Present\n"
            "Enter A for Absent\n"
            "Enter: "
        ).strip().upper()
        if atnd == "P":
            try:
                hours = float(input("Enter Working Hours: "))
                if hours < 0 or hours > 24:
                    print("Hours must be between 0 and 24!")
                    cursor.close()
                    conn.close()
                    return
            except ValueError:
                print("Invalid hours! Enter a number.")
                cursor.close()
                conn.close()
                return
            cursor.execute(
                """INSERT INTO attendance
                (emp_id, name, date, time, status, hours)
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    employee[0],
                    employee[1],
                    today,
                    now,
                    "Present",
                    hours
                )
            )
            print("Employee,", employee[0], "is marked Present!!")
        elif atnd == "A":
            cursor.execute(
                """INSERT INTO attendance
                (emp_id, name, date, time, status, hours)
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    employee[0],
                    employee[1],
                    today,
                    now,
                    "Absent",
                    0
                )
            )
            print("Employee,", employee[0], "is marked Absent!!")
        else:
            print("Invalid Command!")
            cursor.close()
            conn.close()
            return
        conn.commit()
        print("Attendance Saved Successfully!")
        cursor.close()
        conn.close()
        
#PAYROLL-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class payroll:
    def __init__(self):
        try:
            while True:
                d = int(input("\n---PAYROLL MANAGEMENT--- \n1. Generate Payslip \n2. Monthly Payroll Summary \n3. View Payroll Records \n0. Back to Main Menu: \n---Enter: "))
                if d not in [0, 1, 2, 3]:
                    print("\nInvalid choice! Please select 0, 1, 2 or 3.")
                    continue
                match d:
                    case 1:
                        print("--Generating Payslip Now--")
                        payslip()
                    case 2:
                        print("\n--Monthly Payroll Summary--")
                        monthly_payroll_summary()
                    case 3:
                        print("\n--Payroll Records--")
                        view_payroll_records()
                    case 0:
                        break
        except ValueError: print("\n!Invalid Input i.e Error, Try Again!\n")
                    
def monthly_payroll_summary():
    month = input(
        "Enter Payroll Month (YYYY-MM): "
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
        print("Invalid month! Use YYYY-MM.")
        return
    conn = get_connection()
    cursor = conn.cursor()
    # ---------------------------------------------------------
    # CHECK WHETHER ATTENDANCE DATA EXISTS FOR THIS MONTH
    # ---------------------------------------------------------
    cursor.execute(
        """SELECT COUNT(*)
        FROM attendance
        WHERE date >= %s
        AND date < %s""",
        (
            start_date,
            end_date
        )
    )
    attendance_count = cursor.fetchone()[0]
    if attendance_count == 0:
        print("\n==============================================================")
        print("                    MONTHLY PAYROLL SUMMARY")
        print("==============================================================")
        print("Month :", month)
        print("--------------------------------------------------------------")
        print("No attendance data found for", month)
        print("No payroll data is available or stored for this month.")
        print("==============================================================")
        cursor.close()
        conn.close()
        return
    # ---------------------------------------------------------
    # GET ONLY EMPLOYEES WHO HAVE ATTENDANCE IN THIS MONTH
    # ---------------------------------------------------------
    cursor.execute(
        """SELECT DISTINCT
            e.emp_id,
            e.name,
            e.pay,
            e.type
        FROM employees e
        JOIN attendance a
            ON e.emp_id = a.emp_id
        WHERE a.date >= %s
        AND a.date < %s
        ORDER BY e.emp_id""",
        (
            start_date,
            end_date
        )
    )
    employees_data = cursor.fetchall()
    if not employees_data:
        print("\nNo payroll data found for", month)
        cursor.close()
        conn.close()
        return
    total_payroll = 0
    print("\n======================================================================")
    print("                    MONTHLY PAYROLL SUMMARY")
    print("======================================================================")
    print("Month :", month)
    print("----------------------------------------------------------------------")
    # ---------------------------------------------------------
    # CALCULATE PAYROLL FOR THIS MONTH ONLY
    # ---------------------------------------------------------
    for employee in employees_data:
        emp_id = employee[0]
        name = employee[1]
        pay = float(employee[2])
        emp_type = employee[3]
        cursor.execute(
            """SELECT status, hours
            FROM attendance
            WHERE emp_id = %s
            AND date >= %s
            AND date < %s
            ORDER BY date""",
            (
                emp_id,
                start_date,
                end_date
            )
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
        # -----------------------------------------------------
        # BASIC PAY
        # -----------------------------------------------------
        if emp_type == "Part-Time":
            basic_pay = total_hours * pay
        else:
            basic_pay = pay
        # -----------------------------------------------------
        # OVERTIME PAY
        # -----------------------------------------------------
        overtime_pay = overtime_hours * 100
        total_pay = basic_pay + overtime_pay
        total_payroll += total_pay
        # -----------------------------------------------------
        # DISPLAY
        # -----------------------------------------------------
        print("\nEmployee ID   :", emp_id)
        print("Name          :", name)
        print("Type          :", emp_type)
        print("Present Days  :", present_days)
        print("Absent Days   :", absent_days)
        print("Working Hours :", total_hours)
        print("Overtime      :", overtime_hours)
        print("Basic Pay     :", f"₹{basic_pay:.2f}")
        print("Overtime Pay  :", f"₹{overtime_pay:.2f}")
        print("Total Pay     :", f"₹{total_pay:.2f}")
        print("------------------------------------------")
    print("\nTotal Employees :", len(employees_data))
    print("Total Payroll   :", f"₹{total_payroll:.2f}")
    print("======================================================================")
    cursor.close()
    conn.close()

def view_payroll_records():
    print("\n1. View All Payroll Records")
    print("2. View Payroll by Employee")
    print("3. View Payroll by Month")
    choice = input("Select: ").strip()
    conn = get_connection()
    cursor = conn.cursor()
    if choice == "1":
        cursor.execute(
            """SELECT
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
            ORDER BY p.payroll_month DESC, p.emp_id"""
        )
    elif choice == "2":
        emp_id = input("Employee ID: ").strip()
        cursor.execute(
            """SELECT
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
            WHERE p.emp_id = %s
            ORDER BY p.payroll_month DESC""",
            (emp_id,)
        )
    elif choice == "3":
        month = input("Enter Month (YYYY-MM): ").strip()
        try:
            year, month_number = map(int, month.split("-"))
            payroll_month = datetime.date(
                year,
                month_number,
                1
            )
        except ValueError:
            print("Invalid month! Use YYYY-MM.")
            cursor.close()
            conn.close()
            return
        cursor.execute(
            """SELECT
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
            WHERE p.payroll_month = %s
            ORDER BY p.emp_id""",
            (payroll_month,)
        )
    else:
        print("Invalid choice!")
        cursor.close()
        conn.close()
        return
    records = cursor.fetchall()
    if not records:
        print("\nNo payroll records found!")
    else:
        print("\n==============================================================")
        print("                    PAYROLL RECORDS")
        print("==============================================================")
        for record in records:
            print("\nEmployee ID    :", record[0])
            print("Name           :", record[1])
            print("Type           :", record[2])
            print("Payroll Month  :", record[3].strftime("%Y-%m"))
            print("Basic Pay      :", f"₹{float(record[4]):.2f}")
            print("Overtime Hours :", f"{float(record[5]):.2f}")
            print("Overtime Pay   :", f"₹{float(record[6]):.2f}")
            print("Total Pay      :", f"₹{float(record[7]):.2f}")
            print("-----------------------------------------------")
    cursor.close()
    conn.close()

class payslip:
    def __init__(self):
        emp_id = input("Employee ID: ").strip()
        month = input(
            "Enter Payroll Month (YYYY-MM): "
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
            print("Invalid month! Use YYYY-MM.")
            return
        conn = get_connection()
        cursor = conn.cursor()
        # GET EMPLOYEE
        cursor.execute(
            """SELECT emp_id, name, pay, type
            FROM employees
            WHERE emp_id = %s""",
            (emp_id,)
        )
        employee = cursor.fetchone()
        if not employee:
            print("Employee not found!")
            cursor.close()
            conn.close()
            return
        emp_id = employee[0]
        name = employee[1]
        pay = float(employee[2])
        emp_type = employee[3]
        # GET ONLY SELECTED MONTH ATTENDANCE
        cursor.execute(
            """SELECT date, status, hours
            FROM attendance
            WHERE emp_id = %s
            AND date >= %s
            AND date < %s
            ORDER BY date""",
            (
                emp_id,
                start_date,
                end_date
            )
        )
        records = cursor.fetchall()
        total_hours = 0
        overtime_hours = 0
        present_days = 0
        absent_days = 0
        for record in records:
            status = record[1]
            hours = float(record[2])
            if status == "Present":
                present_days += 1
                total_hours += hours
                if hours > 8:
                    overtime_hours += hours - 8
            elif status == "Absent":
                absent_days += 1
        # BASIC PAY
        if emp_type == "Part-Time":
            basic_pay = total_hours * pay
        else:
            basic_pay = pay
        # OVERTIME
        overtime_pay = overtime_hours * 100
        # TOTAL
        total_pay = basic_pay + overtime_pay
        # DISPLAY PAYSLIP
        print("\n================================================")
        print("                  MONTHLY PAYSLIP")
        print("================================================")
        print("Payroll Month  :", month)
        print("Employee ID    :", emp_id)
        print("Name           :", name)
        print("Employee Type  :", emp_type)
        print("-----------------------------------------------")
        print("Present Days   :", present_days)
        print("Absent Days    :", absent_days)
        print("Working Hours  :", total_hours)
        print("-----------------------------------------------")
        print("Basic Pay      :", f"₹{basic_pay:.2f}")
        print("Overtime Hours :", f"{overtime_hours:.2f}")
        print("Overtime Pay   :", f"₹{overtime_pay:.2f}")
        print("-----------------------------------------------")
        print("NET PAY        :", f"₹{total_pay:.2f}")
        print("================================================")
        # CHECK IF PAYROLL FOR THIS MONTH ALREADY EXISTS
        cursor.execute(
            """SELECT id
            FROM payroll
            WHERE emp_id = %s
            AND payroll_month = %s""",
            (
                emp_id,
                start_date
            )
        )
        existing = cursor.fetchone()
        if existing:
            # UPDATE EXISTING MONTH
            cursor.execute(
                """UPDATE payroll
                SET basic_pay = %s,
                    overtime_hours = %s,
                    overtime_pay = %s,
                    total_pay = %s
                WHERE emp_id = %s
                AND payroll_month = %s""",
                (
                    basic_pay,
                    overtime_hours,
                    overtime_pay,
                    total_pay,
                    emp_id,
                    start_date
                )
            )
            print("\nPayroll for this month UPDATED successfully!")
        else:
            # INSERT NEW MONTH
            cursor.execute(
                """INSERT INTO payroll
                (emp_id, basic_pay, overtime_hours,
                 overtime_pay, total_pay, payroll_month)
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    emp_id,
                    basic_pay,
                    overtime_hours,
                    overtime_pay,
                    total_pay,
                    start_date
                )
            )
            print("\nPayroll for this month SAVED successfully!")
        conn.commit()
        cursor.close()
        conn.close()

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
while True:
    try:
        a = int(input("\n----EMPLOYEE ATTENDANCE & PAYROLL SYSTEM MANAGEMENT---- \n 1. Attendance Management \n 2. Payroll Management \n 3. Employee Management \n 0. Exit \n Enter: "))
        if a not in [0, 1, 2, 3]:
            print("\nInvalid choice! Please select 0, 1, 2 or 3.")
            continue
        match a:
            case 1:
                Attendance()
                    
            case 2:
                payroll()
            
            case 3:
                Employee()
                  
            case 0:
                print("!!Thank You! Visit Again!!\n")
                break
    except ValueError: print("\n!Invalid Input i.e Error, Try Again!\n")
    
    